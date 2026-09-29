# Monitoreo de Citas · Perdidos / Riesgos / Retenidos / Leales (29-sep-2026)

## Qué es esto

Se agregó el panel **"MONITOREO DE CITAS · SEPTIEMBRE"** (gráfica día a día) en las 4
pestañas de segmento: 4. Perdidos, 5. En riesgo, 6. Retenidos, 7. Leales — además del
**"FUNNEL DE AVANCE"** agregado antes en la misma sesión.

## Por qué no se pudo con las bases que ya estaban cargadas

Las bases `BDC_SEGMENTS` (Perdidos/Riesgos/Retenidos/Leales) que ya alimentan estas 4
pestañas son, por definición, el universo "sin cita todavía" — casi ningún registro
trae una fecha de cita real. Se validó también el campo "Histórico BDC · Fecha": trae
la misma fecha fija (11/sep) en todos los registros, es la fecha de carga/migración,
no la fecha real de cada gestión. Por eso se le pidió a Frank una fuente distinta.

## Fuente usada

`BDC_POSTVENTA_SEPTIEMBRE_2026_v35.xlsx`, hoja **"CITAS FUTURAS Y CONCRETADAS"** (14,671
filas). Trae, por VIN, la columna `Base_origen` que identifica de qué base/segmento
viene cada cita, más `Fecha_cita_futura` y `Fecha_cita_concretada` con fechas reales.

Mapeo `Base_origen` → segmento del tablero:

- Clientes Perdidos → Perdidos (2 filas)
- Clientes En Riesgo → Riesgos (60 filas)
- Clientes Retenidos → Retenidos (7,586 filas)
- Clientes Leales → Leales (6,671 filas)
- Primer Servicio (352 filas) se ignoró aquí — esa pestaña ya tiene su propio pipeline.

Script: `scripts_build_citas_segmento.py` → genera `data_citas_segmento.js`
(`window.__CITAS_SEGMENTO`).

## Qué muestra la gráfica

Por cada día de septiembre, dos barras apiladas:

- **Concretadas** (verde) = citas con `Fecha_cita_concretada` en ese día.
- **Futuras programadas** (azul) = citas con `Fecha_cita_futura` en ese día.

No existe un campo explícito de "No Show" en esta hoja (se revisó: "Estatus gestión BDC"
está vacío en 14,208 de 14,671 filas), así que la gráfica no incluye esa categoría —
sería inventar un dato que la fuente no trae.

## Volumen real por segmento (septiembre)

- Retenidos: 1,047 concretadas / 965 futuras — buen volumen, gráfica representativa.
- Leales: 1,065 concretadas / 1,028 futuras — buen volumen.
- Riesgos: 45 concretadas / 42 futuras — volumen bajo pero visible.
- Perdidos: 2 concretadas / 2 futuras — prácticamente sin actividad, esperado porque
  Perdidos ya son clientes descartados. El panel muestra una nota aclarando esto en
  vez de una gráfica vacía sin contexto.

## Actualización — filtro propio de Agencia (29-sep, tarde)

Frank pidió que la gráfica respetara los filtros de la pestaña, cruzando por VIN. Se
intentó exactamente así primero, y se descubrió algo importante: el cruce por VIN
entre `CITAS_SEGMENTO` (hoja de citas) y `BDC_SEGMENTS` (tabla operativa de cada
pestaña) da **0% de coincidencia**, incluso después de refrescar ambas bases al mismo
corte (29-sep). No es un problema de datos desactualizados — es arquitectura: las
hojas RETENIDOS/LEALES/EN RIESGO que alimentan la tabla operativa **sólo traen lo
pendiente de gestionar** (documentado en el pipeline, ver más abajo), mientras que
"CITAS FUTURAS Y CONCRETADAS" son VIN que **ya tienen** una cita agendada o realizada —
son poblaciones prácticamente disjuntas por diseño, un VIN sale de "pendiente" en cuanto
consigue una cita.

Por eso se cambió de enfoque: en vez de intentar sincronizar con los filtros de la
tabla (que nunca va a funcionar bien por lo anterior), se le puso a la gráfica **su
propio filtro de Agencia**, construido directamente con el campo `Agencia` que sí trae
la hoja de citas. Validado: filtrar Retenidos a "ACAMBARO" da 1 concretada / 5 futuras,
consistente con lo que hay realmente en esa hoja para esa agencia.

## Actualización — refresco de corte a 29-sep (29-sep, tarde)

Frank pidió mover el corte del tablero al día de hoy. Se encontró el script de la
corrida anterior (`rebuild_full_sep24.py`, con la arquitectura completa del pipeline
documentada en sus comentarios) y se adaptó a `scripts_rebuild_full_sep29.py` con los
archivos nuevos que compartió Frank (U13/U10 29-sep, BDC_POSTVENTA v35, MAESTRO v13),
encadenando Primer Servicio desde la salida de 24-sep (mismo criterio que las corridas
anteriores).

Totales nuevos vs. 24-sep:

| Segmento | 24-sep | 29-sep |
|---|---|---|
| Perdidos | 49 | 69 |
| Riesgos | 1,200 | 1,189 |
| Retenidos | 10,318 | 10,256 |
| Leales | 2,707 | 2,730 |

Histórico Ene-Ago también se corrigió en los textos estáticos del tablero: decía
"1,056 VIN / 1,253 registros" pero los datos reales ya eran 1,143 VIN / 1,340
registros (discrepancia que ya existía antes de esta sesión, no introducida ahora).

## Pendiente / a validar con Frank

- No se validó aún si `Fecha_cita_concretada_historica` debería usarse en vez de
  `Fecha_cita_concretada` para algún caso — se dejó fuera por ahora porque trae fechas
  mucho más antiguas (hasta febrero) que no representan actividad de septiembre.
- El archivo `Copia_de_Bases_Retención_Nissan_agosto_2026_13.xlsx` que compartió Frank
  en el mismo lote no se usó en este refresco — no está referenciado en el pipeline
  documentado (`rebuild_full_sep24.py`/`scripts_rebuild_full_sep29.py`). Si tiene un
  propósito específico, confirmar con Frank para qué parte del tablero aplica.
