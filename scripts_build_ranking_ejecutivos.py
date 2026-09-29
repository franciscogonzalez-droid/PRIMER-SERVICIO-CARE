# -*- coding: utf-8 -*-
"""
Construye data_ranking_ejecutivos.js para la nueva pestaña "Ranking Ejecutivos"
del tablero HTML, a partir de:
  - Citas_Nissan_Respuestas_2026.xlsx -> hoja "Respuestas de formulario 1" (log
    transaccional real, todas las marcas) y hoja "Por ejecutivo Nissan" (pivote
    con los Objetivos mensuales oficiales por ejecutivo, bloques Agosto y
    Septiembre).
  - No usa el .gs de servidor (Frank aún no lo comparte) ni Citas_no_show_...
    (esa se reserva para la vista de Objetivos 1er Serv./RT, fuera de alcance
    de esta primera entrega).

Definiciones aplicadas (documentadas también en el README de entrega):
  - Roster de ejecutivos = filas de "Por ejecutivo Nissan" (bloque Agosto) con
    Objetivo mensual citas age. no vacío y nombre real (se excluyen filas
    agregadas como "Cumplida"/"Resultados citas agendadas"/"Total" y roles no
    comparables sin objetivo como Confirmaciones/Leads/Admin).
  - Objetivo age. / Objetivo show: se toman DIRECTO de "Por ejecutivo Nissan"
    por correo y por mes (Agosto y Septiembre tienen bloques propios con
    objetivos distintos entre sí).
  - Agendadas / Agendada mismo mes / Agendada otro mes / Concretadas: se
    calculan desde CERO a partir del log "Respuestas de formulario 1"
    (Marca=Nissan, Correo, Mes de cita=mes analizado), para que Agendadas
    siempre sea exactamente mismo+otro (no se mezcla con la cifra "Logro"
    del pivote, que es una fuente distinta).
      * "mismo mes": Mes (captura) == Mes de cita
      * "otro mes": Mes (captura) != Mes de cita
      * Concretadas: Estatus == "Cita concretada" (columna "Estatus ")
  - Se EXCLUYE una fila "Vambe" agregada: en el log, las citas por canal Vambe
    ya vienen atribuidas al correo del ejecutivo humano que las gestiona (ver
    " Datos (no tocar)"), así que sumarlas de nuevo en una fila aparte
    duplicaría el conteo. Punto pendiente de validar con Frank.
"""
import re
import json
import unicodedata
from pathlib import Path
import openpyxl

SRC = Path("/root/.claude/uploads/3860e1a5-c308-5661-9863-8e430089bdec/98b6e3b7-Citas_Nissan_Respuestas_2026.xlsx")
OUT_DIR = Path("/home/claude/outputs_ranking")
OUT_DIR.mkdir(exist_ok=True)

MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto",
         "septiembre","octubre","noviembre","diciembre"]

def norm(s):
    if s is None:
        return ""
    s = str(s).strip()
    return s

def norm_month(s):
    s = norm(s).lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s

def norm_email(s):
    return norm(s).lower()

print("Cargando workbook...")
wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)

# ---------- 1) Roster + objetivos desde "Por ejecutivo Nissan" ----------
ws = wb['Por ejecutivo Nissan']
AGG_NAMES = {"cumplida", "resultados citas agendadas", "total", ""}

roster = {}          # correo -> nombre bonito (preferimos el de Agosto)
objetivos = {}        # (correo, mes) -> {"objAge":..,"objShow":..}

rows_iter = ws.iter_rows(min_row=2, values_only=True)
current_block = "agosto"  # el primer bloque de la hoja es Agosto
seen_header_row2 = False
for r in rows_iter:
    correo_raw = r[1]
    nombre_raw = r[2]
    correo = norm_email(correo_raw)
    nombre = norm(nombre_raw)
    objAge = r[4]
    objShow = r[12]

    # Detectar el encabezado del segundo bloque (Septiembre) para cambiar de mes
    if correo_raw == "Correo" and nombre_raw == "Ejecutivo de citas":
        current_block = "septiembre"
        continue

    if not correo or "@" not in correo:
        continue
    if nombre.lower() in AGG_NAMES:
        continue

    is_bot = "userqis" in nombre.lower() or "userqis" in correo.lower()

    if current_block == "agosto":
        # Roster oficial = filas de Agosto con objetivo definido (excluye
        # Confirmaciones/Leads/Admin, que ahí vienen con objetivo vacío)
        if objAge is not None and not is_bot:
            if correo not in roster:
                roster[correo] = nombre
        if objAge is not None:
            objetivos[(correo, "agosto")] = {"objAge": objAge, "objShow": objShow}
    elif current_block == "septiembre":
        if objAge is not None:
            objetivos[(correo, "septiembre")] = {"objAge": objAge, "objShow": objShow}

print(f"Roster oficial (Agosto, con objetivo): {len(roster)} ejecutivos")
for c, n in roster.items():
    print(" -", c, "->", n)

# ---------- 2) Log transaccional "Respuestas de formulario 1" ----------
ws2 = wb['Respuestas de formulario 1']
header = next(ws2.iter_rows(min_row=1, max_row=1, values_only=True))
# localizar índices de columnas por nombre (puede haber duplicados; nos
# quedamos con la primera ocurrencia relevante)
idx = {}
for i, h in enumerate(header):
    if h is None:
        continue
    key = norm(h)
    if key not in idx:
        idx[key] = i

COL_MES_CAPTURA = idx.get("Mes")
COL_CORREO = idx.get("Correo")
COL_MARCA = idx.get("Marca")
COL_MES_CITA = idx.get("Mes de cita")
COL_ESTATUS = idx.get("Estatus")
COL_FUENTE = idx.get("Fuente de cita")
print("columnas:", COL_MES_CAPTURA, COL_CORREO, COL_MARCA, COL_MES_CITA, COL_ESTATUS, COL_FUENTE)

# acumuladores: (mes_cita, correo) -> {mismo, otro, concretadas}
acc = {}
total_rows = 0
nissan_rows = 0
for row in ws2.iter_rows(min_row=2, values_only=True):
    total_rows += 1
    marca = norm(row[COL_MARCA]).lower() if COL_MARCA is not None else ""
    if marca != "nissan":
        continue
    nissan_rows += 1
    mes_cita = norm_month(row[COL_MES_CITA]) if COL_MES_CITA is not None else ""
    mes_captura = norm_month(row[COL_MES_CAPTURA]) if COL_MES_CAPTURA is not None else ""
    correo = norm_email(row[COL_CORREO]) if COL_CORREO is not None else ""
    estatus = norm(row[COL_ESTATUS]).lower() if COL_ESTATUS is not None else ""
    if mes_cita not in ("agosto", "septiembre"):
        continue
    if not correo:
        continue
    key = (mes_cita, correo)
    a = acc.setdefault(key, {"mismo": 0, "otro": 0, "concretadas": 0})
    if mes_captura == mes_cita:
        a["mismo"] += 1
    else:
        a["otro"] += 1
    if "concretada" in estatus and "no concretada" not in estatus:
        a["concretadas"] += 1

print("filas totales:", total_rows, "| filas Nissan:", nissan_rows)

# ---------- 3) Construir estructura final ----------
def pct(n, d):
    if not d:
        return None
    return round(100 * n / d, 1)

result = {"months": [], "byMonth": {}}
for mes in ("agosto", "septiembre"):
    rows_out = []
    for correo, nombre in roster.items():
        a = acc.get((mes, correo), {"mismo": 0, "otro": 0, "concretadas": 0})
        obj = objetivos.get((correo, mes))
        agendadas = a["mismo"] + a["otro"]
        objAge = obj["objAge"] if obj else None
        objShow = obj["objShow"] if obj else None
        rows_out.append({
            "correo": correo,
            "ejecutivo": nombre,
            "agendadas": agendadas,
            "mismoMes": a["mismo"],
            "otroMes": a["otro"],
            "objetivoAge": round(objAge, 2) if objAge is not None else None,
            "pctAge": pct(agendadas, objAge) if objAge else None,
            "concretadas": a["concretadas"],
            "objetivoShow": round(objShow, 2) if objShow is not None else None,
            "pctShow": pct(a["concretadas"], objShow) if objShow else None,
        })
    rows_out.sort(key=lambda x: -x["agendadas"])
    total_agendadas = sum(r["agendadas"] for r in rows_out)
    total_concretadas = sum(r["concretadas"] for r in rows_out)
    top = rows_out[0] if rows_out else None
    result["byMonth"][mes] = {
        "rows": rows_out,
        "kpis": {
            "totalAgendadas": total_agendadas,
            "totalConcretadas": total_concretadas,
            "ejecutivoTop": top["ejecutivo"] if top else None,
            "ejecutivoTopAgendadas": top["agendadas"] if top else None,
        }
    }
    result["months"].append(mes)

result["meta"] = {
    "fuente": "Citas_Nissan_Respuestas_2026.xlsx (hojas 'Respuestas de formulario 1' + 'Por ejecutivo Nissan')",
    "generado": "2026-09-29",
    "notas": [
        "Objetivo age./Objetivo show vienen del pivote oficial 'Por ejecutivo Nissan' (bloques Agosto y Septiembre, con objetivos propios cada uno).",
        "Agendadas/Agendada mismo mes/Agendada otro mes/Concretadas se calculan desde el log transaccional 'Respuestas de formulario 1' filtrado a Marca=Nissan.",
        "No se incluye una fila 'Vambe' agregada: en el log, las citas por canal Vambe ya están atribuidas al correo del ejecutivo humano que las gestiona, así que sumarlas aparte duplicaría el conteo. Pendiente de validar con Frank si se requiere una vista de canal separada.",
        "No se incluyen roles sin objetivo comparable (Confirmaciones y no show, Leads, Admin) ni canales automatizados (IA/userQIS).",
        "Meses disponibles limitados a Agosto y Septiembre porque son los únicos con bloque de Objetivo oficial en 'Por ejecutivo Nissan'."
    ]
}

out_path = OUT_DIR / "data_ranking_ejecutivos.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Escrito:", out_path)

# resumen impreso
for mes in result["months"]:
    b = result["byMonth"][mes]
    print(f"\n=== {mes.upper()} === agendadas={b['kpis']['totalAgendadas']} concretadas={b['kpis']['totalConcretadas']} top={b['kpis']['ejecutivoTop']}({b['kpis']['ejecutivoTopAgendadas']})")
    for r in b["rows"]:
        print(f"  {r['ejecutivo']:<12} ag={r['agendadas']:<4} mismo={r['mismoMes']:<4} otro={r['otroMes']:<4} objAge={r['objetivoAge']} pctAge={r['pctAge']} conc={r['concretadas']:<4} objShow={r['objetivoShow']} pctShow={r['pctShow']}")
