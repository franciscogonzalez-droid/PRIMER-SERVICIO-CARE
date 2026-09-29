# Ranking Ejecutivos Nissan · piloto (29-sep-2026)

## Qué es esto

Nueva pestaña "9. Ranking Ejecutivos" en el mismo HTML, con datos **independientes**
al pipeline BDC/Maestro/U13/U10. Es la primera entrega de portar el tablero
"Citas Nissan" (ver hallazgo en el proyecto POSVENTA), con alcance acordado con
Frank: solo Ranking Ejecutivos por ahora, granularidad de agencia agrupada
(no aplica todavía a esta vista porque no trae columna de agencia), y arrancar
sin esperar al código servidor (.gs).

## Fuente

`Citas_Nissan_Respuestas_2026.xlsx` (el libro real que compartió Frank el 29-sep),
hojas:

- **"Por ejecutivo Nissan"**: de aquí se toman los **Objetivo age.** y
  **Objetivo show** oficiales por ejecutivo. Trae un bloque de columnas propio
  para Agosto y otro para Septiembre, cada uno con sus propios objetivos (NO
  son iguales entre meses: Agosto es 333.33/300 parejo para todos; Septiembre
  varía por ejecutivo, 475–496.11 / 427.5–446.5).
- **"Respuestas de formulario 1"**: el log transaccional real (46 mil+ filas,
  todas las marcas). Se filtra a `Marca = Nissan`. De aquí se calculan
  **Agendadas**, **Agendada mismo mes**, **Agendada otro mes** y
  **Concretadas** — no se usan las cifras "Logro" del pivote para estas
  columnas, para garantizar que Agendadas = mismo mes + otro mes siempre
  cuadre internamente.

Script: `scripts/build_ranking_ejecutivos.py` → genera `data_ranking_ejecutivos.js`.

## Definiciones aplicadas

- **Roster de ejecutivos**: los 11 nombres del bloque de Agosto que tienen
  Objetivo age. definido (excluye filas agregadas como "Cumplida"/"Resultados
  citas agendadas"/"Total" y roles sin objetivo comparable como Confirmaciones
  y no show/Leads/Admin).
- **Agendada mismo mes** = "Mes" de captura de la respuesta == "Mes de cita".
  **Agendada otro mes** = son distintos. Agendadas = suma de ambos.
- **Concretadas** = filas cuyo campo "Estatus" contiene "concretada" (y no
  "no concretada"), dentro del mes analizado (por "Mes de cita").
- **% Cumpl.** = Agendadas u concretadas ÷ objetivo del mes, mismo criterio
  visual que el tablero original: verde ≥100%, ámbar 70–99%, rojo <70%.

## Actualización — podio con fotos/medallas (29-sep, tarde)

Frank compartió 4 capturas del tablero real y pidió acercar la presentación a
la original. Se agregó:

- Selector de mes tipo dropdown ("Mes: Agosto 2026 ▾") en vez de botones.
- Dos podios lado a lado — "Podio — % Cumpl. Citas Agendadas" y "Podio — %
  Cumpl. Citas Concretadas" — con medallero (🥇🥈🥉), barras de alturas
  distintas por lugar, nombre y valor absoluto debajo del %.
- Como no tenemos las fotos reales de Google Drive, cada ejecutivo se
  representa con un avatar de iniciales en un círculo de color (determinista
  por nombre, para que cada quien tenga siempre el mismo color). Si Frank
  consigue las fotos, se pueden insertar sin tocar el resto de la lógica.

Verificado visualmente: los 3 primeros lugares y sus % de Agosto coinciden
con la captura original casi exacto (Jorge Luis 174%, Ariana 111.3% vs. 112%
en la captura, Perla 106.8% vs. 107%).

## Validado contra las capturas del Meet (9-sep, datos de Agosto)

Los números de Agosto calculados aquí coinciden de cerca con lo que se ve en
la captura `04_06m00s_Ranking_Ejecutivos_agosto_detalle.jpg` del Meet (Jorge
Luis 580 vs. 581 en la captura, Perla 356 vs. 356, Monica 319 vs. 319, Alfredo
242 vs. 242, Lennin 231 vs. 231 — diferencias de 1-3 registros en el resto,
esperable por el corte de tiempo exacto de cada snapshot). Esto da confianza
de que la lógica replica razonablemente bien al tablero original, sin haber
visto su código servidor.

## Decisiones tomadas sin confirmar aún con Frank — pendientes de validar

1. **No se incluye una fila "Vambe"**: en el log, las citas del canal Vambe
   vienen atribuidas al correo del ejecutivo humano que las gestiona (no a un
   "ejecutivo Vambe" separado), así que agregarlas de nuevo en una fila aparte
   duplicaría el conteo. La captura del Meet de septiembre sí mostraba una
   fila "Vambe" con objetivo altísimo (4,942/3,558) — no se pudo reconciliar
   con ninguna fuente de objetivo de canal en los archivos recibidos. Si Frank
   confirma que sí debe existir como fila/objetivo propio, hace falta que
   comparta esa fuente de objetivo específica.
2. Septiembre muestra "Concretadas" muy bajas para varios ejecutivos (p. ej.
   Ariana 0/372, Joel 0/80, Lennin 31/394) pese a estar casi al cierre del
   mes — esto puede ser un problema real de actualización de estatus en la
   fuente (el mismo tipo de inconsistencia que el propio Meet marcó como
   pendiente de validar en agosto), no necesariamente un error de este
   cálculo. Vale la pena que Frank lo revise con su equipo antes de tomarlo
   como cifra final.
3. Meses disponibles limitados a Agosto y Septiembre porque son los únicos
   con bloque de Objetivo oficial en "Por ejecutivo Nissan". Si Frank quiere
   más meses (el log de respuestas sí los tiene), hace falta el objetivo de
   esos meses.
4. Sigue pendiente: código .gs (solo para verificar fórmulas si algo no
   cuadra), Objetivos 1er Serv./RT, fotos de ejecutivos, y las 4 vistas
   genéricas (1er Servicio/Retención/Campaña/Vines Conquistados) — fuera de
   alcance de esta entrega por decisión de Frank.
