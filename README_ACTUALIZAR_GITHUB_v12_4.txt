ACTUALIZACIÓN GITHUB PAGES · POSTVENTA BDC v12.4
=================================================

CORTE U13
---------
05/09/2026

VENTANA DE DEPURACIÓN DE CAMPAÑAS
---------------------------------
05/06/2026 al 05/10/2026

REGLAS
------
- Cita CUMPLIDA al corte: se retira de la base activa.
- Cita vigente hoy o futura: se retira de la base activa.
- No Show: permanece para recuperación.
- Cancelada: permanece para volver a contactar.
- Si un VIN tiene una cita cumplida o futura además de No Show/Cancelada,
  prevalece la salida de la base activa.
- Retenidos y Leales se deduplican por VIN.

RESULTADO DE DEPURACIÓN
-----------------------
Perdidos:
- Base anterior: 95
- Concluidos retirados: 4
- Cita vigente/futura retirada: 0
- Activos nuevos: 91

En riesgo:
- Base anterior: 1,321
- Concluidos retirados: 20
- Cita vigente/futura retirada: 3
- Activos nuevos: 1,298

Retenidos:
- Base anterior: 27,064
- VIN únicos: 25,921
- Duplicados eliminados: 1,143
- Concluidos retirados: 4,932
- Cita vigente/futura retirada: 351
- Activos nuevos: 20,638

Leales:
- Base anterior: 23,728
- VIN únicos: 23,621
- Duplicados eliminados: 107
- Concluidos retirados: 10,181
- Cita vigente/futura retirada: 204
- Activos nuevos: 13,236

PRIMER SERVICIO · UNIVERSO 1,952
--------------------------------
Sin cita programada: 1,158
No Show: 163
Cita vigente/futura: 390
Show / CUMPLIDA: 235
Perdido: 5
Servicio sin cita: 1

CITAS TOTALES SEPTIEMBRE
------------------------
Total referencias U13: 2,494
Show: 851
No Show: 139
Cita vigente/futura: 992
Cancelada: 509
CUMPLIDA con fecha futura a validar: 3

CÓMO ACTUALIZAR GITHUB
----------------------
1. Descomprime POSTVENTA_BDC_GITHUB_v12_4.zip.
2. En tu repositorio PRIMER-SERVICIO-CARE:
   Add file > Upload files.
3. Sube TODOS los archivos descomprimidos.
4. Conserva exactamente los mismos nombres.
5. Commit directly to main.
6. Espera el despliegue de GitHub Pages.
7. Abre la liga y usa Ctrl + F5 si todavía ves la versión anterior.

IMPORTANTE PARA BDC POSTVENTA
-----------------------------
Después de validar el HTML, usa los botones verdes uno por uno:
1. Primer Servicio
2. Perdidos
3. En riesgo
4. Retenidos
5. Leales

Espera la confirmación de cada proceso antes de iniciar el siguiente.
Al sincronizar Perdidos/Riesgo/Retenidos/Leales, los VIN que ya no vienen
en estas bases depuradas quedarán inactivos en BDC CONTROL V3, pero se
conservará su trazabilidad.
