# Reconstrucción completa · corte 24 de septiembre 2026

## Archivos usados

- `BDC POSTVENTA - SEPTIEMBRE 2026 (27).xlsx`
- `MAESTRO - SEGUIMIENTO PRIMER SERVICIO SEPTIEMBRE 2026 (10).xlsx`
- `U13_javier_24-09-2026.xls`
- `U10_javier_24-09-2026.xls`
- Histórico de clientes perdidos: el mismo archivo Ene-Sep ya enriquecido
  (sin cambios esta entrega — ver sección "Perdidos" abajo, es un flujo
  distinto ahora).

## Fecha de corte

`CUT = 2026-09-24` — hoy, confirmado de nuevo por Frank.

## Cambio de fondo: el BDC cambió de arquitectura

Este BDC (27) ya no tiene la misma estructura que veníamos usando desde el
inicio del proyecto. El detalle completo del hallazgo está en
`HALLAZGO_ESTRUCTURA_BDC26_24SEP2026.md` (proyecto POSVENTA); resumen de lo
que cambió en el pipeline:

**1. Hojas renombradas y con otro alcance.** Antes cada hoja de segmento
(`CLIENTES PERDIDOS`/`CLIENTES EN RIESGO`/`CLIENTES RETENIDOS`/`CLIENTES
LEALES`) traía a TODOS los miembros del segmento. Ahora (`PERDIDOS`/`EN
RIESGO`/`RETENIDOS`/`LEALES`) solo traen lo **pendiente de gestionar**; en
cuanto un VIN se pierde, no se presenta o tiene cita, el archivo lo saca a
una hoja de salida aparte. Por eso los universos de Riesgo/Retenidos/Leales
se ven más chicos que en cortes anteriores — no es que la base de clientes
se haya encogido, es que ya no se cuenta a todos en un solo lugar:

| Segmento | Corte 21-sep | Corte 24-sep (hoy) |
|---|---:|---:|
| Riesgo | 1,265 | 1,200 |
| Retenidos | 18,053 | 10,318 |
| Leales | 9,470 | 2,707 |

**2. "Perdidos" ahora sale de la hoja `DESCARTADOS`.** La hoja que
literalmente se llama `PERDIDOS` ya NO es el equivalente — es otra cosa
(clientes pendientes, no lo usamos, por decisión tuya). El tablero arma
"Perdidos" desde `DESCARTADOS` (log de salida de los 4 segmentos),
filtrando solo los motivos que sí son pérdida real: **49 VIN** con motivo
"Gestión confirma pérdida" (con o sin bandera ARCO). Se excluyeron **21 VIN**
con motivo "Otro taller / Flotilla / Otra agencia" — eso es reclasificación,
no pérdida.

`DESCARTADOS` solo trae 12 columnas (sin Agencia/Modelo/Teléfono/Correo). Se
rellenaron esos campos cruzando por VIN contra, en este orden: (a) las
hojas del propio BDC (27) de este corte, (b) la salida ya calculada del
corte anterior (21-sep, último estado con detalle completo), (c) el
histórico Ene-Sep. Resultado: **35 de los 49 VIN quedaron con Agencia
rellenada**; los 14 restantes no aparecen en ninguna de esas tres fuentes,
así que se dejaron en blanco — sin inventar nada, tal como confirmaste.

**3. Primer Servicio: 2 hojas → 1 + una hoja de No Shows general.** Antes
"sin cita" y "no show" eran 2 hojas dedicadas a 1er servicio. Ahora es 1
hoja `PRIMER SERVICIO` (557 registros) + la hoja general `NO SHOWS` (569,
multi-segmento), de la cual se usó el subconjunto de Primer Servicio (387).

**4. Cambio de arquitectura del pipeline (importante para trazabilidad).**
Como `PRIMER SERVICIO` + `NO SHOWS` ya no cubren cerca del 100% del universo
fijo de 2,061 VIN cada corte (antes sí lo cubrían casi todo), la semilla de
"Primer Servicio" **ya no se toma del archivo original congelado del
09-sep**, sino de la salida ya calculada del corte anterior (21-sep). Así,
los VIN que este corte no tocan directamente conservan su último estatus
conocido en vez de regresar al estado de hace dos semanas. A partir de esta
entrega, cada corte debe encadenarse desde la salida del corte anterior
(no desde el original de 09-sep) mientras el BDC siga con este formato de
"solo pendientes".

## Verificaciones de integridad

- Sin VIN duplicados en ningún segmento: Perdidos 49, Riesgo 1,200,
  Retenidos 10,318, Leales 2,707, Primer Servicio 2,061 (universo fijo, sin
  cambio).
- Histórico: 1,340 registros fuente, 1,143 VIN únicos (archivo congelado,
  sin tocar esta entrega — ver pendiente abajo).

## Resultado Primer Servicio (Estatus monitoreo)

| Estatus monitoreo | Corte 21-sep | Corte 24-sep (ahora) |
|---|---:|---:|
| Sin cita programada | 1,047 | 929 |
| Show | 356 | 399 |
| No Show | 283 | 384 |
| Cita futura | 74 | 80 |
| Cita futura SICOP · Reconfirmar | 80 | 48 |
| Perdido histórico | 221 | 221 |
| **Total** | **2,061** | **2,061** |

## Citas de septiembre (U13)

7,443 citas totales (antes 6,511) — Show 4,061, No Show 1,278, Cancelada
1,178, Cita futura 923, Show con fecha futura 3.

## Taller (U10)

2,426 VIN únicos (antes 2,398).

## Cambios al HTML en esta entrega

1. **Corte evaluable**: sin cambios de código — el sistema automático ya
   existente (`window.__META.cutQuiter` → `fixCutDateLabels()`) propagó el
   24-sep correctamente en todo el sitio, sin tocar el HTML a mano.
2. **Nueva sección "% DE CONTACTO POR AGENCIA"** en la pestaña principal
   (Primer Servicio), justo antes de "Análisis de clientes perdidos". Por
   agencia: universo (según los filtros activos), VIN con intento de
   contacto válido (estatus de gestión BDC registrado), VIN sin intento, y
   % de contacto. Respeta los filtros de Región/Agencia/Universo que ya
   existían arriba. La definición de "intento válido" es: el VIN tiene un
   valor no vacío en "Último estatus mes anterior" (el estatus de gestión
   BDC más reciente). Si esta definición no es la que buscabas, dime cuál
   sería el criterio correcto y la ajusto.
3. Se detectó y limpió una sección de código muerto ("Gestión Contact
   Center" / `initG`/`renderG`) que existía en el HTML pero nunca se
   mostraba (no estaba conectada a ningún botón de pestaña) — no se borró
   por seguridad, pero no afecta nada visible; si en algún momento sí la
   quieres visible como pestaña propia, avísame.

## Pendiente / a tu criterio

1. El histórico Ene-Sep (1,340 registros) no se tocó esta entrega — los 49
   VIN de `DESCARTADOS` (pérdida confirmada) son un flujo distinto y hoy no
   se cruzan contra el histórico. Si quieres que las pérdidas confirmadas
   de este corte se vayan sumando también al histórico acumulado, dime y
   lo armo.
2. 14 de los 49 VIN de Perdidos quedaron sin Agencia/Modelo/Teléfono (no
   aparecen en ninguna fuente de respaldo disponible) — se puede investigar
   más si hace falta esa información puntual.
3. La hoja `PERDIDOS` literal del BDC y las hojas `Mes 5 1er Servicio` /
   `Mes 5 Retención Total` siguen fuera de esta iteración, por decisión
   tuya.
4. `Copia de Bases Retención` (Quiter BI) y los VIN `DEMO` de inventario —
   siguen fuera de este corte.
