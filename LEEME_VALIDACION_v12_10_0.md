# POSTVENTA BDC · HTML v12.10.0

Actualización construida sobre la versión estable v12.9.2, sin rediseñar la navegación ni sustituir la URL del Web App.

## Fuentes integradas

- `BDC POSTVENTA - SEPTIEMBRE 2026 (4).xlsx`
- `MAESTRO - SEGUIMIENTO PRIMER SERVICIO SEPTIEMBRE 2026 (3).xlsx`
- `U13_javier 09-09-26.xls`
- `U10_javier 09-09-26.xls`
- `HISTORICO_CLIENTES_PERDIDOS_ENE_AGO_2026.xlsx`
- `BDD BI POSVENTA SEPTIEMBRE.xlsx`, analizada como fuente de enriquecimiento en transición.

## Conteos validados

- Primer Servicio de referencia: 2,061 VIN.
- Citas U13 de septiembre: 3,586 referencias.
- Histórico Ene–Ago: 1,253 registros fuente / 1,056 VIN únicos.
- U10: 2,228 VIN únicos con su orden más reciente.
- Clientes perdidos activos: 87 VIN.
- Clientes en riesgo activos: 1,265 VIN.
- Clientes retenidos activos: 18,059 VIN.
- Clientes leales activos: 9,504 VIN.
- Cruces entre histórico Ene–Ago y los cuatro segmentos activos: 0.

## Reglas aplicadas

- El último día evaluable de U13 es el 08/sep. Las citas del 09/sep en adelante no se clasifican como No Show.
- Una cita `NO CUMPLIDA` cancelada (`AC`) se clasifica como Cancelada, no como No Show.
- Los históricos Ene–Ago permanecen en su pestaña y se excluyen de las bases activas.
- La base directa no contiene filas identificadas como febrero; se conserva el mes fuente original, conforme a la validación del usuario.
- En productividad, `Retornó` sólo cuenta como Show cuando existe evidencia de cita/servicio. Hay un retorno actual pendiente de evidencia.
- Para productividad BDC se usa primero `Ejecutivo BDC` (gestión verde actual) y, si está vacío, `Ejecutivo BDC anterior`.
- La BDD BI no reemplaza todavía a U13: se conserva U13 como fuente operativa principal y BI como enriquecimiento.

## Validaciones técnicas

- Sintaxis del HTML y de todos los archivos JavaScript: correcta.
- Archivos JavaScript referenciados: presentes.
- VIN duplicados dentro de cada segmento activo: 0.
- No Shows con fecha futura: 0.
- `NO CUMPLIDA` pasada, no cancelada y sin clasificar como No Show: 0.

## Publicación

Sube el contenido completo de esta carpeta al mismo repositorio/ubicación de la versión anterior. Sustituye todos los archivos juntos para evitar que `index.html` se combine con datos de otra versión.
