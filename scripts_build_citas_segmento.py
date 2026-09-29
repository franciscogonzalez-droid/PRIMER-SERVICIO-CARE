import openpyxl
import json
import datetime

SRC = '/root/.claude/uploads/3860e1a5-c308-5661-9863-8e430089bdec/a51aa6df-BDC_POSTVENTA_SEPTIEMBRE_2026_v35.xlsx'
OUT = '/home/claude/outputs_citas_seg/data_citas_segmento.json'

BASE_ORIGEN_MAP = {
    'Clientes Perdidos': 'Perdidos',
    'Clientes En Riesgo': 'Riesgos',
    'Clientes Retenidos': 'Retenidos',
    'Clientes Leales': 'Leales',
    # 'Primer Servicio' ya se cubre en la pestaña 1 con su propio pipeline; se ignora aquí.
}

def iso(v):
    if isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%d')
    return None

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
ws = wb['CITAS FUTURAS Y CONCRETADAS']
rows = list(ws.iter_rows(values_only=True))
header = rows[0]
idx = {h: i for i, h in enumerate(header)}
data = rows[1:]

out = {k: [] for k in BASE_ORIGEN_MAP.values()}
skipped_other = 0
for r in data:
    base = r[idx['Base_origen']]
    seg = BASE_ORIGEN_MAP.get(base)
    if not seg:
        skipped_other += 1
        continue
    vin = (r[idx['VIN']] or '').strip()
    if not vin:
        continue
    out[seg].append({
        'VIN': vin,
        'Cliente': r[idx['Cliente']] or '',
        'Agencia': r[idx['Agencia']] or '',
        'Modelo': r[idx['Modelo sin versión']] or '',
        'FechaCitaFutura': iso(r[idx['Fecha_cita_futura']]),
        'FechaCitaConcretada': iso(r[idx['Fecha_cita_concretada']]),
        'EjecutivoBDC': r[idx['Ejecutivo BDC']] or '',
        'EstatusGestionBDC': r[idx['Estatus gestión BDC']] or '',
        'CitaAgendadaBDC': r[idx['Cita agendada BDC']] or '',
    })

summary = {k: len(v) for k, v in out.items()}
print('rows per segment:', summary)
print('skipped (otro Base_origen, ej. Primer Servicio):', skipped_other)

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)

print('escrito en', OUT)
