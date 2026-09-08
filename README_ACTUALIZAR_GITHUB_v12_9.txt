POSTVENTA BDC · v12.9 · UNIVERSO MARCA + OBJETIVOS
===================================================

NUEVO UNIVERSO MARCA
--------------------
Fuente: Datos Subyacentes Sin1erServ_2026-09-07.xlsx
VIN únicos: 1,597

Cruce vs referencia anterior Marca (1,488):
- Permanecen: 1,435
- Reingresan históricos Marca agosto: 162
- Dejan de aparecer: 53
  - 52 estaban como Show
  - 1 era Sin cita programada

GRUPO EXCLUSIVO
---------------
Se conserva: 464 VIN
Cruce nuevo Marca vs Grupo exclusivo: 0 VIN

CONSOLIDADO DE REFERENCIA
-------------------------
1,597 Marca + 464 Grupo exclusivo = 2,061 VIN

TRAZABILIDAD
------------
Los 162 VIN históricos Marca de agosto reaparecen exactamente en la nueva fuente.
Se mantienen con Cliente perdido histórico = Sí y Estatus monitoreo = Perdido histórico,
por lo que el Apps Script V3.5.0 los conserva como salida/inactivos en BDC y no los
confunde con pérdidas nuevas de septiembre.

ANTECEDENTE BDC
---------------
VIN Marca con antecedente de gestión/histórico identificado: 540
Históricos agosto dentro de Marca: 162

OBJETIVOS
---------
Se integró el documento OBJETIVOS POSVENTA PRIMER SERVICIO SEPTIEMBRE.docx:
- Por CVE / agencia
- Por región: Michoacán, Querétaro, CDMX
- Grupo Autocom
- Objetivo nacional: 78.6%

Objetivo Grupo Autocom:
- Primer Servicio actual fuente: 61.93%
- Objetivo: 82.72%
- PS con venta: 3,756
- Objetivo VIN: 5,017
- Brecha: 1,261 VIN
- Sin 1er Servicio: 1,597

NOTA CVE 226 / 266
------------------
El documento rotula la primera sección como 266, pero la nueva base utiliza CVE 226.
La relación se integró como CVE 226 porque ambos muestran exactamente 148 VIN Sin
1er Servicio, y el resto del desglose coincide con la nueva base.

GITHUB
------
1. Descomprime POSTVENTA_BDC_GITHUB_v12_9.zip.
2. Reemplaza TODOS los archivos del repositorio.
3. Commit a main.
4. Espera GitHub Pages.
5. Refresca con Ctrl+F5.

BDC
---
Después de validar el HTML, sincroniza Primer Servicio con el botón verde.
El Apps Script V3.5.0 ya instalado puede recibir la nueva referencia.
Las bases Retención no se modifican en esta versión.
