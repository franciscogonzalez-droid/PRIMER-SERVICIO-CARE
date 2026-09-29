from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import openpyxl

# ------------------------------------------------------------------
# Reconstruccion COMPLETA · corte 24-sep-2026.
#
# Cambia respecto a las corridas anteriores (18-sep / 21-sep): el BDC
# cambio de arquitectura (ver HALLAZGO_ESTRUCTURA_BDC26_24SEP2026.md
# en el proyecto POSVENTA). Resumen de los cambios reales al pipeline:
#
# 1. Hojas de segmento renombradas y ahora SOLO traen lo pendiente de
#    gestionar (ya no toda la base): CLIENTES PERDIDOS->PERDIDOS (ya NO
#    se usa esta hoja), CLIENTES EN RIESGO->EN RIESGO, CLIENTES
#    RETENIDOS->RETENIDOS, CLIENTES LEALES->LEALES.
# 2. "Perdidos" ahora sale de la hoja DESCARTADOS (log de salida
#    multi-segmento), filtrado a motivo "Gestion confirma perdida"
#    (se excluye "Otro taller/Flotilla/Otra agencia", que no es perdida
#    real). DESCARTADOS solo trae 12 columnas (sin Agencia/Modelo/
#    Telefono/Correo/etc.) - esos campos se rellenan por VIN cruzando
#    contra (a) las hojas del propio BDC de este corte, (b) la salida
#    ya calculada del corte anterior (21-sep, ultimo estado bueno con
#    detalle completo), (c) el historico Ene-Sep. Lo que no aparezca en
#    ningun lado queda en blanco, sin inventar nada (confirmado con
#    Frank).
# 3. Primer Servicio: antes 2 hojas (sin cita / no show), ahora 1 hoja
#    PRIMER SERVICIO (universo activo) + hoja NO SHOWS general
#    (multi-segmento), filtrada aqui a Segmento="Primer Servicio".
# 4. IMPORTANTE - cambio de arquitectura del pipeline: como PRIMER
#    SERVICIO+NO SHOWS ya no cubren el universo fijo completo de 2,061
#    VIN (antes las hojas cubrian casi todo el universo cada corte), el
#    "existing_primer" semilla YA NO se lee del archivo original
#    congelado de 09-sep (github_v370_prep) sino de la salida ya
#    calculada del corte anterior (21-sep) - asi los ~1,117 VIN que no
#    se tocan este corte conservan su ultimo estatus conocido en vez de
#    revertir al estado de hace 2 semanas. Los data files base
#    (coverageRequired, primerServiceObjectives, etc.) se siguen
#    heredando del original via meta.update().
#
# "Mes 5 1er Servicio"/"Mes 5 Retencion Total" y la hoja PERDIDOS
# literal quedan fuera de esta iteracion (decision explicita de Frank).
# ------------------------------------------------------------------

BASE_DIR = Path("/home/claude/github_v370_prep")
PREV_DIR = Path("/home/claude/github_v370_sep24_full")
OUT_DIR = Path("/home/claude/outputs_sep29_full")
OUT_DIR.mkdir(parents=True, exist_ok=True)

U13_PATH = Path("/home/claude/converted_sep29/6ab1ad97-U13_javier_29-09-2026.xlsx")
U10_PATH = Path("/home/claude/converted_sep29/1ceac99a-U10_javier_29-09-2026.xlsx")
BDC_PATH = Path("/root/.claude/uploads/3860e1a5-c308-5661-9863-8e430089bdec/a51aa6df-BDC_POSTVENTA_SEPTIEMBRE_2026_v35.xlsx")
MASTER_PATH = Path("/root/.claude/uploads/3860e1a5-c308-5661-9863-8e430089bdec/2071f52d-MAESTRO_-_SEGUIMIENTO_PRIMER_SERVICIO_SEPTIEMBRE_2026_13.xlsx")
HIST_PATH = Path("/home/claude/hist_sep21/HISTORICO_CLIENTES_PERDIDOS_ENE_SEP_2026_ENRIQUECIDO.xlsx")

CUT = date(2026, 9, 29)  # corte = HOY, confirmado explícitamente por Frank (mismo criterio que cortes anteriores)

TALLER_AGENCY = {
    "1": "MADERO", "2": "URIANGATO", "5": "CHAPULTEPEC",
    "6": "ACAMBARO", "7": "ZITACUARO", "8": "VALLE DE BRAVO",
    "10": "HUETAMO", "11": "URUAPAN", "12": "LOS REYES",
    "13": "ZAMORA", "14": "SAHUAYO", "15": "CONSTITUYENTES",
    "16": "CONSTITUYENTES", "17": "LA CAPILLA",
    "18": "BERNARDO QUINTANA", "20": "SAN JUAN DEL RIO",
    "45": "JURIQUILLA", "67": "CAMPA", "90": "REVOLUCION",
    "91": "PATRIOTISMO",
}
TALLER_REGION = {
    **{k: "MICHOACÁN" for k in ["1", "2", "5", "6", "7", "8", "10", "11", "12", "13", "14"]},
    **{k: "QRO" for k in ["15", "16", "17", "18", "20", "45", "67"]},
    **{k: "CDMX" for k in ["90", "91"]},
}


def clean(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Sí" if value else "No"
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def norm(value):
    text = unicodedata.normalize("NFKD", clean(value))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).upper().strip()


def vin(value):
    return re.sub(r"[^A-Z0-9]", "", clean(value).upper())


def valid_vin(value):
    v = vin(value)
    return v if len(v) == 17 else ""


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = clean(value)
    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def load_js_array(path: Path, variable: str):
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(rf"window\.{re.escape(variable)}\s*=\s*(\[.*\])\s*;?\s*$", text, re.S)
    if not match:
        raise ValueError(f"No se encontró {variable} en {path}")
    return json.loads(match.group(1))


def load_js_object(path: Path, variable: str):
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(rf"window\.{re.escape(variable)}\s*=\s*(\{{.*\}})\s*;?\s*$", text, re.S)
    if not match:
        raise ValueError(f"No se encontró {variable} en {path}")
    return json.loads(match.group(1))


def load_js_chunk_parts(path: Path, variable: str):
    """Lee un archivo con el patrón window.VAR=window.VAR||[];window.VAR.push([...]);"""
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(rf"window\.{re.escape(variable)}\.push\((\[.*\])\)\s*;?\s*$", text, re.S)
    if not match:
        raise ValueError(f"No se encontró push de {variable} en {path}")
    return json.loads(match.group(1))


def write_js(path: Path, variable: str, value):
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    path.write_text(f"window.{variable}={payload};\n", encoding="utf-8")


def read_xlsx_records(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    raw_headers = list(next(rows))
    seen = Counter()
    headers = []
    for h in raw_headers:
        h = clean(h)
        seen[h] += 1
        headers.append(h if seen[h] == 1 else f"{h}__{seen[h]}")
    out = [
        {headers[i]: value for i, value in enumerate(row) if i < len(headers) and headers[i]}
        for row in rows
        if any(clean(x) for x in row)
    ]
    wb.close()
    return out


def appointment_class(row):
    status = norm(row.get("Estado"))
    result = norm(row.get("Cita"))
    appt_date = parse_date(row.get("Fec.cita"))

    if status.startswith("AC ") or status == "AC":
        return "Cancelada"
    if result == "CUMPLIDA":
        if appt_date and appt_date > CUT:
            return "Show con fecha futura"
        return "Show"
    if result == "NO CUMPLIDA":
        if appt_date and appt_date <= CUT:
            return "No Show"
        return "Cita futura"
    if appt_date and appt_date > CUT:
        return "Cita futura"
    return "Pendiente sin resultado"


def citas_type(row):
    status = norm(row.get("Estado"))
    if status.startswith("AC "):
        return "Anulada"
    if status.startswith("CC "):
        return "Confirmada"
    if status.startswith("CR "):
        return "Reprogramada"
    if status.startswith("CI "):
        return "Cita"
    return clean(row.get("Estado")) or "Sin tipo"


def make_citas(u13_rows):
    out = []
    events_by_vin = defaultdict(list)
    for row in u13_rows:
        appt_date = parse_date(row.get("Fec.cita"))
        if not appt_date or appt_date.year != 2026 or appt_date.month != 9:
            continue
        code = clean(row.get("Taller"))
        classification = appointment_class(row)
        v = valid_vin(row.get("VIN"))
        item = {
            "Región": TALLER_REGION.get(code, "SIN MAPEAR"),
            "Taller Quiter": code,
            "Referencia": clean(row.get("Referencia")),
            "Cumplimiento": clean(row.get("Cita")),
            "VIN": v,
            "Modelo": clean(row.get("Marca/modelo")),
            "Año unidad": clean(row.get("Año vehíc")),
            "Usuario": clean(row.get("USUARIO")),
            "Fecha cita": appt_date.isoformat(),
            "Estado cita": clean(row.get("Estado")),
            "Cliente": clean(row.get("Contacto")),
            "Teléfono": clean(row.get("Teléfono")),
            "Correo": clean(row.get("E-mail")),
            "Des. avería": clean(row.get("Des.avería")),
            "Fecha apertura OR": clean(row.get("FEC.APER")),
            "Tipo OR": clean(row.get("TIPO.OR")),
            "Estado OR": clean(row.get("Estado O.R.")),
            "Asesor OR": clean(row.get("ASESOR OR")) or clean(row.get("ASESOR O")),
            "Validación taller": "Sí" if clean(row.get("FEC.APER")) else "No",
            "Clasificación": classification,
            "Tipo de cita": citas_type(row),
            "Agencia Quiter": TALLER_AGENCY.get(code, ""),
        }
        out.append(item)
        if v:
            events_by_vin[v].append(item)
    return out, events_by_vin


def select_vin_event(events):
    if not events:
        return None

    def event_date(item):
        return parse_date(item.get("Fecha cita")) or date.min

    shows = [e for e in events if e["Clasificación"] == "Show"]
    if shows:
        return max(shows, key=event_date)
    future = [e for e in events if e["Clasificación"] in {"Cita futura", "Show con fecha futura"}]
    if future:
        return min(future, key=event_date)
    no_shows = [e for e in events if e["Clasificación"] == "No Show"]
    if no_shows:
        return max(no_shows, key=event_date)
    cancelled = [e for e in events if e["Clasificación"] == "Cancelada"]
    if cancelled:
        return max(cancelled, key=event_date)
    return max(events, key=event_date)


def read_sheet_records(workbook, sheet_name):
    sheet = workbook[sheet_name]
    rows = sheet.iter_rows(values_only=True)
    headers = [clean(v) for v in next(rows)]
    return [
        {headers[i]: value for i, value in enumerate(row) if i < len(headers) and headers[i]}
        for row in rows
        if any(value not in (None, "") for value in row)
    ]


def first_nonempty(record, *keys):
    for key in keys:
        value = record.get(key)
        if clean(value):
            return clean(value)
    return ""


def join_unique(values):
    out = []
    for value in values:
        text = clean(value)
        if text and text not in out:
            out.append(text)
    return " / ".join(out)


def bdc_js_record(record, events_by_vin):
    v = valid_vin(record.get("VIN"))
    event = select_vin_event(events_by_vin.get(v, [])) or {}
    result = first_nonempty(record, "Resultado cita U13") or event.get("Clasificación", "")
    if result == "Pendiente sin resultado":
        result = "Sin cita"

    phones = join_unique([
        record.get("Teléfono correcto BDC"),
        record.get("Teléfono móvil / principal"),
        record.get("Teléfono casa / alterno"),
    ])
    emails = join_unique([
        record.get("Correo correcto BDC"),
        record.get("Correo electrónico"),
    ])
    agency = first_nonempty(record, "Agencia origen", "Agencia")
    model = first_nonempty(record, "Modelo sin versión", "Modelo")
    year = first_nonempty(record, "Año vehículo", "Año")
    current_exec = first_nonempty(record, "Ejecutivo BDC")
    previous_exec = first_nonempty(record, "Ejecutivo BDC anterior")

    return {
        "VIN": v,
        "Cliente": first_nonempty(record, "Cliente"),
        "Modelo": model,
        "Año": year,
        "Región": first_nonempty(record, "Región"),
        "Agencia": agency,
        "Cve": first_nonempty(record, "Cve"),
        "Tipo venta": first_nonempty(record, "Tipo venta"),
        "APV": first_nonempty(record, "APV"),
        "Condición": first_nonempty(record, "Condición"),
        "Garantía": first_nonempty(record, "Garantía"),
        "Última visita riesgo": first_nonempty(record, "Fecha último servicio"),
        "Teléfonos": phones,
        "Correos": emails,
        "Fuente contacto": "",
        "Oferta comercial": first_nonempty(record, "Oferta comercial") or "SIN OFERTA",
        "Resultado cita": result,
        "Fecha cita": clean(event.get("Fecha cita")) or first_nonempty(record, "Fecha cita BDC"),
        "Tipo cita": clean(event.get("Tipo de cita")),
        "Estado cita": clean(event.get("Estado cita")),
        "Cumplimiento": clean(event.get("Cumplimiento")),
        "Usuario cita": clean(event.get("Usuario")) or first_nonempty(record, "Usuario cita U13"),
        "Ciclo operativo": first_nonempty(record, "Ciclo operativo"),
        "Histórico BDC · Ejecutivo": previous_exec,
        "Histórico BDC · Fecha": first_nonempty(record, "Fecha última gestión BDC"),
        "Histórico BDC · Estatus": first_nonempty(record, "Estatus BDC anterior"),
        "Histórico BDC · Subestatus": first_nonempty(record, "Subestatus BDC anterior"),
        "Histórico BDC · Comentario": first_nonempty(record, "Comentario BDC anterior"),
        "Ejecutivo BDC": current_exec,
        "Estatus gestión BDC": first_nonempty(record, "Estatus gestión BDC"),
        "Subestatus BDC": first_nonempty(record, "Subestatus BDC"),
        "Comentario BDC": first_nonempty(record, "Comentario BDC"),
        "Fecha cita BDC": first_nonempty(record, "Fecha cita BDC"),
        "Validación U13": "CON EVIDENCIA U13" if event else "SIN EVIDENCIA U13",
        "Mes": first_nonempty(record, "Mes"),
        "Agencia origen": agency,
        "CSA": first_nonempty(record, "CSA"),
        "Modelo sin versión": model,
        "Versión": first_nonempty(record, "Versión"),
        "Año vehículo": year,
        "Teléfono móvil / principal": first_nonempty(record, "Teléfono correcto BDC", "Teléfono móvil / principal"),
        "Teléfono casa / alterno": first_nonempty(record, "Teléfono casa / alterno"),
        "Correo electrónico": first_nonempty(record, "Correo correcto BDC", "Correo electrónico"),
        "Agencia última visita OR tipo 3": first_nonempty(record, "Agencia última visita OR tipo 3"),
        "Fecha factura nuevo": first_nonempty(record, "Fecha factura"),
        "Fecha factura seminuevo": "",
        "Fecha último servicio": first_nonempty(record, "Fecha último servicio"),
        "Último kilometraje registrado": first_nonempty(record, "Último kilometraje registrado"),
        "Medio de contacto preferente": first_nonempty(record, "Medio de contacto preferente"),
        "Cantidad VIN relacionados": first_nonempty(record, "Cantidad VIN relacionados"),
        "Último estatus mes anterior": first_nonempty(record, "Último estatus mes anterior"),
        "Validación registro": first_nonempty(record, "Validación registro"),
        "Formato ARCO / LPHD": "",
        "Contactos últimos 90 días": "",
        "OR abierta últimos 90 días": "",
        "Inventario / Demo": "",
        "Exclusión NU/PT": "",
        "Fecha referencia cliente": "",
        "Usuario cita U13": first_nonempty(record, "Usuario cita U13") or clean(event.get("Usuario")),
        "Fecha factura": first_nonempty(record, "Fecha factura"),
    }


PERDIDA_CONFIRMADA_RE = re.compile(r"GESTION CONFIRMA PERDIDA")


def build_backfill_index(events_by_vin):
    """VIN -> registro con forma bdc_js_record, para rellenar Agencia/
    Modelo/Telefono/etc. de los registros de DESCARTADOS (que no traen
    esos campos). Prioridad: (1) hojas del propio BDC de este corte,
    (2) salida ya calculada del corte anterior (21-sep), (3) histórico."""
    idx = {}
    workbook = openpyxl.load_workbook(BDC_PATH, read_only=True, data_only=True)
    for sheet_name in ["EN RIESGO", "RETENIDOS", "LEALES", "PRIMER SERVICIO", "NO SHOWS"]:
        for raw in read_sheet_records(workbook, sheet_name):
            v = valid_vin(raw.get("VIN"))
            if v and v not in idx:
                idx[v] = bdc_js_record(raw, events_by_vin)
    workbook.close()

    prev_specs = [
        (PREV_DIR / "data_bdc_perdidos.js", "__BDC_PERDIDOS", False),
        (PREV_DIR / "data_bdc_riesgos.js", "__BDC_RIESGOS", False),
        (PREV_DIR / "data_bdc_retenidos_01.js", "__BDC_RETENIDOS_PARTS", True),
        (PREV_DIR / "data_bdc_retenidos_02.js", "__BDC_RETENIDOS_PARTS", True),
        (PREV_DIR / "data_bdc_retenidos_03.js", "__BDC_RETENIDOS_PARTS", True),
        (PREV_DIR / "data_bdc_retenidos_04.js", "__BDC_RETENIDOS_PARTS", True),
        (PREV_DIR / "data_bdc_leales_01.js", "__BDC_LEALES_PARTS", True),
        (PREV_DIR / "data_bdc_leales_02.js", "__BDC_LEALES_PARTS", True),
        (PREV_DIR / "data_bdc_leales_03.js", "__BDC_LEALES_PARTS", True),
    ]
    for path, variable, chunked in prev_specs:
        rows = load_js_chunk_parts(path, variable) if chunked else load_js_array(path, variable)
        for row in rows:
            v = valid_vin(row.get("VIN"))
            if v and v not in idx:
                idx[v] = row

    hist_workbook = openpyxl.load_workbook(HIST_PATH, read_only=True, data_only=True)
    for raw in read_sheet_records(hist_workbook, "Consolidado Ene-Ago"):
        v = valid_vin(raw.get("VIN"))
        if v and v not in idx:
            idx[v] = {
                "Agencia": clean(raw.get("Agencia")),
                "Agencia origen": clean(raw.get("Agencia")),
                "Región": clean(raw.get("Región")),
                "Modelo": clean(raw.get("Modelo")),
                "Modelo sin versión": clean(raw.get("Modelo")),
                "Año": clean(raw.get("Año unidad")),
                "Año vehículo": clean(raw.get("Año unidad")),
                "Teléfono móvil / principal": clean(raw.get("Teléfono")),
                "Correo electrónico": clean(raw.get("Correo")),
                "Oferta comercial": clean(raw.get("Oferta comercial")),
            }
    hist_workbook.close()
    return idx


def build_perdidos_from_descartados(events_by_vin, backfill):
    workbook = openpyxl.load_workbook(BDC_PATH, read_only=True, data_only=True)
    rows = read_sheet_records(workbook, "DESCARTADOS")
    workbook.close()

    out = []
    excluded_no_real_loss = 0
    for record in rows:
        v = valid_vin(record.get("VIN"))
        if not v:
            continue
        motivo = clean(record.get("Motivo_descarte"))
        if not PERDIDA_CONFIRMADA_RE.search(norm(motivo)):
            excluded_no_real_loss += 1
            continue

        fill = backfill.get(v, {})
        current_exec = first_nonempty(record, "Ejecutivo BDC")
        previous_exec = ""

        out.append({
            "VIN": v,
            "Cliente": first_nonempty(record, "Cliente") or fill.get("Cliente", ""),
            "Modelo": fill.get("Modelo", ""),
            "Año": fill.get("Año", ""),
            "Región": fill.get("Región", ""),
            "Agencia": fill.get("Agencia", ""),
            "Cve": fill.get("Cve", ""),
            "Tipo venta": fill.get("Tipo venta", ""),
            "APV": fill.get("APV", ""),
            "Condición": fill.get("Condición", ""),
            "Garantía": fill.get("Garantía", ""),
            "Última visita riesgo": fill.get("Última visita riesgo", ""),
            "Teléfonos": fill.get("Teléfonos") or fill.get("Teléfono móvil / principal", ""),
            "Correos": fill.get("Correos") or fill.get("Correo electrónico", ""),
            "Fuente contacto": "",
            "Oferta comercial": fill.get("Oferta comercial") or "SIN OFERTA",
            "Resultado cita": "",
            "Fecha cita": "",
            "Tipo cita": "",
            "Estado cita": "",
            "Cumplimiento": "",
            "Usuario cita": "",
            "Ciclo operativo": "Descartado · Pérdida confirmada",
            "Histórico BDC · Ejecutivo": previous_exec,
            "Histórico BDC · Fecha": "",
            "Histórico BDC · Estatus": first_nonempty(record, "Estatus BDC anterior"),
            "Histórico BDC · Subestatus": first_nonempty(record, "Subestatus BDC anterior"),
            "Histórico BDC · Comentario": first_nonempty(record, "Comentario BDC anterior"),
            "Ejecutivo BDC": current_exec,
            "Estatus gestión BDC": first_nonempty(record, "Estatus gestión BDC"),
            "Subestatus BDC": first_nonempty(record, "Subestatus BDC"),
            "Comentario BDC": first_nonempty(record, "Comentario BDC") or first_nonempty(record, "Motivo gestión BDC"),
            "Fecha cita BDC": "",
            "Validación U13": "SIN EVIDENCIA U13",
            "Mes": "Septiembre",
            "Agencia origen": fill.get("Agencia origen") or fill.get("Agencia", ""),
            "CSA": fill.get("CSA", ""),
            "Modelo sin versión": fill.get("Modelo sin versión") or fill.get("Modelo", ""),
            "Versión": fill.get("Versión", ""),
            "Año vehículo": fill.get("Año vehículo") or fill.get("Año", ""),
            "Teléfono móvil / principal": fill.get("Teléfono móvil / principal", ""),
            "Teléfono casa / alterno": fill.get("Teléfono casa / alterno", ""),
            "Correo electrónico": fill.get("Correo electrónico", ""),
            "Agencia última visita OR tipo 3": fill.get("Agencia última visita OR tipo 3", ""),
            "Fecha factura nuevo": fill.get("Fecha factura", ""),
            "Fecha factura seminuevo": "",
            "Fecha último servicio": fill.get("Fecha último servicio", ""),
            "Último kilometraje registrado": fill.get("Último kilometraje registrado", ""),
            "Medio de contacto preferente": fill.get("Medio de contacto preferente", ""),
            "Cantidad VIN relacionados": fill.get("Cantidad VIN relacionados", ""),
            "Último estatus mes anterior": first_nonempty(record, "Estatus gestión BDC") or fill.get("Último estatus mes anterior", ""),
            "Validación registro": fill.get("Validación registro", ""),
            "Formato ARCO / LPHD": "",
            "Contactos últimos 90 días": "",
            "OR abierta últimos 90 días": "",
            "Inventario / Demo": "",
            "Exclusión NU/PT": "",
            "Fecha referencia cliente": "",
            "Usuario cita U13": "",
            "Fecha factura": fill.get("Fecha factura", ""),
            "Motivo descarte BDC": motivo,
            "Base origen BDC": first_nonempty(record, "Base_origen") or first_nonempty(record, "Segmento"),
        })
    return out, excluded_no_real_loss


def build_bdc_segments(events_by_vin, backfill):
    workbook = openpyxl.load_workbook(BDC_PATH, read_only=True, data_only=True)
    specs = {
        "Riesgos": "EN RIESGO",
        "Retenidos": "RETENIDOS",
        "Leales": "LEALES",
    }
    result = {}
    for key, sheet_name in specs.items():
        rows = read_sheet_records(workbook, sheet_name)
        result[key] = [bdc_js_record(row, events_by_vin) for row in rows if valid_vin(row.get("VIN"))]

    perdidos, excluded = build_perdidos_from_descartados(events_by_vin, backfill)
    result["Perdidos"] = perdidos

    first = {}
    sin_cita_rows = read_sheet_records(workbook, "PRIMER SERVICIO")
    first["sin_cita"] = {
        valid_vin(row.get("VIN")): row for row in sin_cita_rows if valid_vin(row.get("VIN"))
    }
    no_show_rows = read_sheet_records(workbook, "NO SHOWS")
    first["no_show"] = {
        valid_vin(row.get("VIN")): row
        for row in no_show_rows
        if valid_vin(row.get("VIN")) and norm(row.get("Segmento")) == "PRIMER SERVICIO"
    }
    workbook.close()
    return result, first, excluded


def build_productivity(events_by_vin):
    workbook = openpyxl.load_workbook(MASTER_PATH, read_only=True, data_only=True)
    rows = read_sheet_records(workbook, "BDC CONTROL V3")
    workbook.close()

    segment_map = {
        "CLIENTES PERDIDOS": "Perdidos",
        "CLIENTES EN RIESGO": "Riesgos",
        "CLIENTES RETENIDOS": "Retenidos",
        "CLIENTES LEALES": "Leales",
    }
    by_key = {}
    for record in rows:
        segment = segment_map.get(clean(record.get("Segmento")))
        v = valid_vin(record.get("VIN"))
        if not segment or not v:
            continue
        if "HISTORICO CLIENTES PERDIDOS ENE-AGO" in norm(record.get("Motivo salida")):
            continue

        event = select_vin_event(events_by_vin.get(v, [])) or {}
        classification = clean(event.get("Clasificación"))
        if classification == "Show con fecha futura":
            classification = "Cita futura"
        result = classification or first_nonempty(record, "Resultado cita U13")
        status = first_nonempty(record, "Estatus gestión BDC")
        agent = first_nonempty(record, "Ejecutivo BDC", "Ejecutivo BDC anterior")

        by_key[(segment, v)] = {
            "Segmento tablero": segment,
            "VIN": v,
            "Ejecutivo": agent,
            "Región": first_nonempty(record, "Región"),
            "Agencia": first_nonempty(record, "Agencia origen", "Agencia"),
            "Cve": first_nonempty(record, "Cve"),
            "Año": first_nonempty(record, "Año vehículo", "Año"),
            "Modelo": first_nonempty(record, "Modelo sin versión", "Modelo"),
            "APV": first_nonempty(record, "APV"),
            "Oferta comercial": first_nonempty(record, "Oferta comercial"),
            "Resultado cita": result,
            "Fecha cita": clean(event.get("Fecha cita")) or first_nonempty(record, "Fecha cita U13", "Fecha cita BDC"),
            "Ciclo operativo": first_nonempty(record, "Ciclo operativo"),
            "Estatus gestión BDC": status,
            "Estatus BDC anterior": first_nonempty(record, "Estatus BDC anterior"),
            "Validación retorno": first_nonempty(record, "Validación registro"),
        }
    return list(by_key.values())


def build_historical():
    workbook = openpyxl.load_workbook(HIST_PATH, read_only=True, data_only=True)
    rows = read_sheet_records(workbook, "Consolidado Ene-Ago")
    workbook.close()

    grouped = defaultdict(list)
    for row in rows:
        v = valid_vin(row.get("VIN"))
        if v:
            grouped[v].append(row)

    month_order = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
        "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
    }
    out = []
    for v, items in grouped.items():
        items.sort(key=lambda r: clean(r.get("Periodo pérdida")))
        latest = items[-1]
        months = []
        for row in items:
            month = clean(row.get("Mes pérdida"))
            if month and month not in months:
                months.append(month)
        months.sort(key=lambda m: month_order.get(norm(m), 99))
        periods = sorted({clean(r.get("Periodo pérdida")) for r in items if clean(r.get("Periodo pérdida"))})
        reasons = []
        comments = []
        offers = []
        for row in items:
            for bucket, key in ((reasons, "Motivo perdido"), (comments, "Comentario origen"), (offers, "Oferta comercial")):
                value = clean(row.get(key))
                if value and value not in bucket:
                    bucket.append(value)

        offer = offers[-1] if offers else ""
        out.append({
            "Región": clean(latest.get("Región")),
            "Agencia": clean(latest.get("Agencia")),
            "Cliente": clean(latest.get("Cliente")),
            "VIN": v,
            "Año unidad": clean(latest.get("Año unidad")),
            "Modelo": clean(latest.get("Modelo")),
            "Motivo perdido": reasons[-1] if reasons else "",
            "Comentario origen": comments[-1] if comments else "",
            "Motivo perdido agosto": reasons[-1] if reasons else "",
            "Comentario origen agosto": comments[-1] if comments else "",
            "Teléfono": clean(latest.get("Teléfono")),
            "Correo": clean(latest.get("Correo")),
            "Oferta comercial": offer,
            "Tiene oferta comercial": "Sí" if offer else "No",
            "Origen histórico": "HISTÓRICO ENE-AGO",
            "Mes(es) pérdida": ", ".join(months),
            "Primera pérdida": periods[0] if periods else "",
            "Última pérdida": periods[-1] if periods else "",
            "N registros histórico": sum(int(float(clean(r.get("N registros origen")) or 1)) for r in items),
            "Motivos históricos": " | ".join(reasons),
        })
    out.sort(key=lambda r: (r["Última pérdida"], r["Región"], r["Agencia"], r["VIN"]), reverse=True)
    return out, len(rows)


def build_taller():
    rows = read_xlsx_records(U10_PATH)
    latest = {}
    for row in rows:
        v = valid_vin(row.get("VIN"))
        if not v:
            continue
        opened = parse_date(row.get("Fec.aper")) or date.min
        current = latest.get(v)
        if not current or opened >= current[0]:
            latest[v] = (opened, row)

    out = []
    for v, (_, row) in latest.items():
        out.append({
            "VIN": v,
            "Taller": clean(row.get("Nombre")),
            "Ref OR": clean(row.get("Ref.OR")),
            "Fecha apertura": (parse_date(row.get("Fec.aper")) or date.min).isoformat() if parse_date(row.get("Fec.aper")) else "",
            "Cliente OR": clean(row.get("Nombre__2")),
            "Tipo": clean(row.get("Tipo O")),
            "Tipo OR": clean(row.get("Tipo O.R.")),
            "Asesor taller": clean(row.get("Asesor")),
            "Días": clean(row.get("Dias")),
            "Status actual": clean(row.get("STATUS ACTUAL")),
        })
    out.sort(key=lambda r: (r["Fecha apertura"], r["VIN"]), reverse=True)
    return out


def update_primer(existing, events_by_vin, historical, first_active):
    hist_by_vin = {row["VIN"]: row for row in historical}
    sin_cita = first_active["sin_cita"]
    no_show = first_active["no_show"]

    for row in existing:
        v = valid_vin(row.get("VIN"))
        if not v:
            continue
        event = select_vin_event(events_by_vin.get(v, []))
        hist = hist_by_vin.get(v)
        active = sin_cita.get(v) or no_show.get(v)

        if active:
            row["Mes"] = first_nonempty(active, "Mes") or row.get("Mes", "")
            row["Agencia origen"] = first_nonempty(active, "Agencia origen") or row.get("Agencia origen", "")
            row["CSA"] = first_nonempty(active, "CSA")
            row["Modelo sin versión"] = first_nonempty(active, "Modelo sin versión") or row.get("Modelo sin versión", "")
            row["Versión"] = first_nonempty(active, "Versión") or row.get("Versión", "")
            row["Año vehículo"] = first_nonempty(active, "Año vehículo") or row.get("Año vehículo", "")
            row["Teléfono móvil / principal"] = first_nonempty(active, "Teléfono correcto BDC", "Teléfono móvil / principal") or row.get("Teléfono móvil / principal", "")
            row["Teléfono casa / alterno"] = first_nonempty(active, "Teléfono casa / alterno") or row.get("Teléfono casa / alterno", "")
            row["Correo electrónico"] = first_nonempty(active, "Correo correcto BDC", "Correo electrónico") or row.get("Correo electrónico", "")
            row["Fecha factura"] = first_nonempty(active, "Fecha factura") or row.get("Fecha factura", "")
            row["Fecha último servicio"] = first_nonempty(active, "Fecha último servicio") or row.get("Fecha último servicio", "")
            row["Último kilometraje registrado"] = first_nonempty(active, "Último kilometraje registrado") or row.get("Último kilometraje registrado", "")
            row["Ejecutivo Contact Center"] = first_nonempty(active, "Ejecutivo BDC", "Ejecutivo BDC anterior") or row.get("Ejecutivo Contact Center", "")
            row["Último comentario agencia"] = first_nonempty(active, "Comentario BDC", "Comentario BDC anterior") or row.get("Último comentario agencia", "")
            row["Último estatus mes anterior"] = first_nonempty(active, "Estatus gestión BDC", "Estatus BDC anterior") or row.get("Último estatus mes anterior", "")
            row["Validación registro"] = first_nonempty(active, "Validación registro") or row.get("Validación registro", "")

        if event:
            classification = event["Clasificación"]
            operational_class = "Cita futura" if classification == "Show con fecha futura" else classification
            row["Referencia cita"] = event["Referencia"]
            row["Fecha cita"] = event["Fecha cita"]
            row["Estado cita"] = event["Estado cita"]
            row["Cumplimiento Quiter"] = event["Cumplimiento"]
            row["Usuario cita"] = event["Usuario"]
            row["Usuario cita U13"] = event["Usuario"]
            row["Nombre agente"] = event["Usuario"]
            row["Agencia cita"] = event["Agencia Quiter"]
            row["Des. avería"] = event["Des. avería"]
            row["Fecha OR"] = event["Fecha apertura OR"]
            row["Tiene cita vigente"] = "No" if operational_class == "Cancelada" else "Sí"
            row["Concretada Quiter"] = "Sí" if operational_class == "Show" else "No"
            row["Validación taller U13"] = "CON EVIDENCIA U13"
            if not hist:
                if operational_class == "Show":
                    row["Estatus monitoreo"] = "Show"
                elif operational_class == "No Show":
                    row["Estatus monitoreo"] = "No Show"
                elif operational_class == "Cita futura":
                    row["Estatus monitoreo"] = (
                        "Cita futura SICOP · Reconfirmar"
                        if "SICOP" in norm(event["Usuario"])
                        else "Cita futura"
                    )
                elif operational_class == "Cancelada" and v not in no_show:
                    row["Estatus monitoreo"] = "Sin cita programada"

        if v in no_show and not hist and (not event or event.get("Clasificación") != "Show"):
            row["Estatus monitoreo"] = "No Show"
        elif v in sin_cita and not hist and not event:
            row["Estatus monitoreo"] = "Sin cita programada"

        if hist:
            row["Cliente perdido histórico"] = "Sí"
            row["Motivo perdido histórico"] = hist["Motivo perdido"]
            row["Estatus monitoreo"] = "Perdido histórico"
        else:
            row["Cliente perdido histórico"] = "No"

    return existing


def write_chunked(prefix, parts_variable, rows, part_count):
    size = (len(rows) + part_count - 1) // part_count
    for index in range(part_count):
        chunk = rows[index * size:(index + 1) * size]
        payload = json.dumps(chunk, ensure_ascii=False, separators=(",", ":"))
        path = OUT_DIR / f"{prefix}_{index + 1:02d}.js"
        path.write_text(
            f"window.{parts_variable}=window.{parts_variable}||[];\n"
            f"window.{parts_variable}.push({payload});\n",
            encoding="utf-8",
        )


def main():
    # IMPORTANTE: la semilla de Primer Servicio ya NO es el archivo original
    # congelado de 09-sep (BASE_DIR) sino la salida ya calculada del corte
    # anterior (21-sep) — ver nota de arquitectura al inicio del archivo.
    existing_primer = load_js_array(PREV_DIR / "data_primer_servicio.js", "__DATA")
    meta = load_js_object(BASE_DIR / "data_meta.js", "__META")

    print("Leyendo U13...")
    u13_rows = read_xlsx_records(U13_PATH)
    citas, events_by_vin = make_citas(u13_rows)

    print("Construyendo índice de respaldo (Agencia/Modelo/Teléfono/Correo) para Descartados...")
    backfill = build_backfill_index(events_by_vin)

    print("Leyendo BDC (segmentos + sin cita/no shows + descartados)...")
    segments, first_active, excluded_descartados = build_bdc_segments(events_by_vin, backfill)

    print("Leyendo Maestro (productividad)...")
    productivity = build_productivity(events_by_vin)

    print("Leyendo historico Ene-Sep...")
    historical, historical_source_rows = build_historical()

    print("Leyendo U10 (taller)...")
    taller = build_taller()

    print("Actualizando Primer Servicio...")
    primer = update_primer(existing_primer, events_by_vin, historical, first_active)

    write_js(OUT_DIR / "data_primer_servicio.js", "__DATA", primer)
    write_js(OUT_DIR / "data_citas_totales.js", "__CITAS_TOTAL_DATA", citas)
    write_js(OUT_DIR / "data_taller.js", "__TALLER_DATA", taller)
    write_js(OUT_DIR / "data_historicos.js", "__HIST_LOST_GROUP", historical)
    write_js(OUT_DIR / "data_bdc_perdidos.js", "__BDC_PERDIDOS", segments["Perdidos"])
    write_js(OUT_DIR / "data_bdc_riesgos.js", "__BDC_RIESGOS", segments["Riesgos"])
    write_js(OUT_DIR / "data_bdc_productividad.js", "__BDC_PRODUCTIVITY", productivity)
    write_chunked("data_bdc_retenidos", "__BDC_RETENIDOS_PARTS", segments["Retenidos"], 4)
    write_chunked("data_bdc_leales", "__BDC_LEALES_PARTS", segments["Leales"], 3)

    primer_counts = Counter(clean(row.get("Estatus monitoreo")) for row in primer)
    citas_counts = Counter(row["Clasificación"] for row in citas)
    segment_counts = {key: len(value) for key, value in segments.items()}
    perdidos_con_agencia = sum(1 for r in segments["Perdidos"] if clean(r.get("Agencia")))
    meta.update({
        "cutQuiter": CUT.isoformat(),
        "u13SepRows": len(citas),
        "logicVersion": "v12.10 (motor original, adaptado) · corte U13/U10 29-sep (corte = hoy, confirmado por Frank) · BDC(v35)/Maestro(13) misma arquitectura que 24-sep (PERDIDOS->DESCARTADOS, PRIMER SERVICIO+NO SHOWS consolidados) · Primer Servicio encadenado desde salida 24-sep",
        "segmentCounts": segment_counts,
        "primerCounts": dict(primer_counts),
        "citasCounts": dict(citas_counts),
        "historicalLostUnique": len(historical),
        "historicalLostSourceRows": historical_source_rows,
        "u10UniqueVins": len(taller),
        "dataRefresh": "2026-09-29",
        "perdidosDescartadosExcluidosNoPerdidaReal": excluded_descartados,
        "perdidosConAgenciaRellenada": perdidos_con_agencia,
    })
    write_js(OUT_DIR / "data_meta.js", "__META", meta)

    summary = {
        "cut": CUT.isoformat(),
        "primer_rows": len(primer),
        "primer_counts": dict(primer_counts),
        "citas_rows": len(citas),
        "citas_counts": dict(citas_counts),
        "historical_unique_vin": len(historical),
        "historical_source_rows": historical_source_rows,
        "taller_unique_vin": len(taller),
        "segment_counts": segment_counts,
        "productivity_rows": len(productivity),
        "descartados_excluidos_no_perdida_real": excluded_descartados,
        "perdidos_con_agencia_rellenada": perdidos_con_agencia,
        "perdidos_total": segment_counts["Perdidos"],
    }
    (OUT_DIR / "resumen_validacion_completa_29sep2026.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
