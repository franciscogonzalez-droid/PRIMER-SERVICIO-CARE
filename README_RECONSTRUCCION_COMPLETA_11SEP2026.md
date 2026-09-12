# Reconstrucción completa · corte 11 de septiembre 2026

## Qué se hizo

Con los tres archivos que compartiste (`BDC POSTVENTA - SEPTIEMBRE 2026 (10).xlsx`,
`MAESTRO - SEGUIMIENTO PRIMER SERVICIO SEPTIEMBRE 2026 (4).xlsx` e
`HISTORICO_CLIENTES_PERDIDOS_ENE_AGO_2026.xlsx`) más el U13/U10 del 11 de
septiembre, se corrió **el motor completo** de `03_CODIGO_COMPLETO_BUILD_HTML_V12_10.py`
(el paquete técnico que rescataste de la conversación con ChatGPT), sin
modificar ninguna regla de negocio — solo las rutas de entrada, el lector de
U13/U10 (xlsx en vez de csv crudo) y la fecha de corte.

A diferencia de la actualización previa (acotada, solo por citas), esta sí
reconstruye todo: los 4 segmentos (Perdidos/Riesgo/Retenidos/Leales), la
productividad, el histórico y el Primer Servicio completo con las hojas
`SIN CITA PROGRAMADA - 1ER SERVI` / `NO SHOWS - 1ER SERVICIO` del BDC ya
migrado a V3.7.0 y depurado.

## Fecha de corte

`CUT = 2026-09-10` (el U13 confirma generación el 11-sep vía `F.CREACI`;
mismo criterio que 9-sep → corte 8-sep: el último día completo y evaluable es
el día anterior a la descarga).

## Verificaciones de integridad (antes de entregar)

- Sin VIN duplicados en ningún segmento: Perdidos 87, Riesgos 1,265,
  Retenidos 18,059, Leales 9,470.
- Cruce histórico Ene-Ago vs. los 4 segmentos activos: 0 (como debe ser).
- Cruce histórico vs. Primer Servicio: 221, exactamente igual al conteo de
  `Perdido histórico` — consistente.
- Primer Servicio: 2,061 VIN, todos únicos.
- Histórico: 1,253 registros fuente, 1,056 VIN únicos (coincide con el dato
  ya documentado en el proyecto).

## Resultado Primer Servicio (Estatus monitoreo)

| Estatus monitoreo | Corte 8-sep | Corte 10-sep (ahora) |
|---|---:|---:|
| Sin cita programada | 924 | 1,078 |
| Show | 180 | 220 |
| No Show | 241 | 252 |
| Cita futura | 116 | 125 |
| Cita futura SICOP · Reconfirmar | 379 | 165 |
| Perdido histórico | 221 | 221 |
| **Total** | **2,061** | **2,061** |

La baja fuerte en SICOP · Reconfirmar (379→165) y la subida en Sin cita
programada (924→1,078) se explican porque ahora sí se usaron las hojas reales
`SIN CITA PROGRAMADA - 1ER SERVI` / `NO SHOWS - 1ER SERVICIO` del BDC vigente:
mucho de lo que estaba pendiente de reconfirmar SICOP ya fue trabajado por
los agentes y quedó reflejado como Sin cita programada u otro estatus real.

## Segmentos (Perdidos/Riesgo/Retenidos/Leales)

| Segmento | Referencia anterior | Ahora (BDC 10) |
|---|---:|---:|
| Perdidos | 87 | 87 |
| En riesgo | 1,265 | 1,265 |
| Retenidos | 18,059 | 18,059 |
| Leales | 9,504 | 9,470 |

Leales bajó en 34 VIN respecto a la referencia previa — es esperable dado que
el BDC sigue en operación diaria (agentes gestionando, posibles bajas o
reclasificaciones); no se detectó ninguna causa técnica anómala.

## Un hallazgo que te reporto, sin tocarlo

En `BDC CONTROL V3` del Maestro hay columnas repetidas al final del
encabezado (`Comentario BDC`, `Cita agendada BDC`, `Fecha cita BDC`, `Fecha
actividad BDC`, `Trabajado BDC`, `Usuario última gestión BDC`, `Archivo BDC`,
`Última actualización` aparecen dos veces). Esto hace que la productividad
tome el valor de la última columna repetida, no necesariamente un error, pero
vale la pena que lo revises en la estructura del Maestro. No se corrigió
nada — solo te lo señalo.

## Archivos de este paquete

Igual que la base v12.11.1, con estos archivos reemplazados: `index.html` (sin
cambios), `data_primer_servicio.js`, `data_citas_totales.js`, `data_taller.js`,
`data_historicos.js`, `data_bdc_perdidos.js`, `data_bdc_riesgos.js`,
`data_bdc_productividad.js`, `data_bdc_retenidos_01..04.js`,
`data_bdc_leales_01..03.js`, `data_meta.js`.
