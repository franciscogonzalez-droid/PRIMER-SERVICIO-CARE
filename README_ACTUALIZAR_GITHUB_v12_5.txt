POSTVENTA BDC · v12.5 · DEPURACIÓN U13 + ORDEN DE TALLER
=========================================================

CORTE
-----
U13: 05/09/2026

NUEVA REGLA
-----------
1. FEC.APER informada y fecha <= corte:
   => vehículo ya ingresó a taller => se retira de campaña activa.

2. Cita CUMPLIDA <= corte:
   => se retira.

3. Cita vigente / futura:
   => se retira temporalmente.

4. No Show:
   => permanece para recuperación.

5. Cancelada:
   => permanece para recontacto.

VALIDACIÓN DEL VIN REPORTADO
----------------------------
VIN: 3N1AB8AE4SY426356
Resultado: Servicio realizado
Fuente: ORDEN U13 · FEC.APER
Fecha apertura O.R.: 2026-06-02
Tipo O.R.: 3 OR MANTENIMIENTO Y  SERVICIO
Estado O.R.: CERRADA

PRIMER SERVICIO · 1,952 VIN
----------------------------
Sin cita programada: 1,054
No Show: 247
Cita vigente/futura: 382
Servicio/Show validado: 263
Perdido: 5
Servicio sin cita: 1

BASES ACTIVAS BDC
-----------------
Perdidos: 91
En riesgo: 1,297
Retenidos: 18,538
Leales: 9,954

SERVICIOS ADICIONALES RETIRADOS VS v12.4
----------------------------------------
Perdidos: 0
En riesgo: 1
Retenidos: 2,100
Leales: 3,282

GITHUB
------
1. Descomprime POSTVENTA_BDC_GITHUB_v12_5.zip.
2. En PRIMER-SERVICIO-CARE:
   Add file > Upload files.
3. Sube TODOS los archivos.
4. Conserva exactamente los nombres.
5. Commit directly to main.
6. Espera GitHub Pages y usa Ctrl+F5.

BDC POSTVENTA
-------------
Después de validar la web, sincroniza uno por uno:
1. Primer Servicio
2. Perdidos
3. En riesgo
4. Retenidos
5. Leales

Espera confirmación antes de iniciar el siguiente.
No requiere cambio adicional del Apps Script V3.2.0.
