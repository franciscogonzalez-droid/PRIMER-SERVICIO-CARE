# v12.11.1 — Botón V3.7.0 (migración diaria verde→azul) agregado al HTML

## Qué cambia respecto a v12.11.0
Sólo se tocó `index.html`. Ningún `data_*.js` cambió — mismos datos, mismo universo,
misma estructura de siempre.

Se agregó una segunda franja debajo del botón verde de "ACTUALIZAR BDC · PRIMER SERVICIO",
con el nuevo botón:

**🔒 MIGRAR VERDE → AZUL (V3.7.0)**

- Envía la acción `migrarGestionDiaria` al mismo Web App (misma URL de siempre, no se tocó).
- Muestra una confirmación clara de lo que va a hacer antes de enviar.
- El acceso está restringido del lado del script (sólo la cuenta autorizada de Frank
  puede ejecutarlo sin error) — el botón puede estar visible para todo el equipo sin riesgo.

## Estado actual: visual y funcionalmente listo del lado del HTML, falta un paso del lado del script

El botón ya arma y envía la solicitud correctamente. Pero el `doPost` del script en vivo
**todavía no tiene la rama que atiende `action === 'migrarGestionDiaria'`** — hoy sólo existe
documentada como ejemplo dentro de `AJUSTE_V370_MIGRACION_DIARIA.gs`. Si se sube este HTML
tal cual y alguien le da clic al botón antes de agregar esa rama, va a caer en el flujo
de compatibilidad de Agencia y va a mostrar un error de "agencia no válida" (no es un error
real, es sólo que todavía no hay rama que lo atienda).

**Por eso el orden correcto es:**

1. Frank termina de validar manualmente `migrarGestionVerdeAzulDiariaV370()` desde el editor
   de Apps Script (como ya está haciendo).
2. Una vez validado, se agrega al `doPost` real del script la rama:
   ```javascript
   if (action === 'migrarGestionDiaria') {
     verificarAccesoMigracionV370_();
     migrarGestionVerdeAzulDiariaV370();
     return jsonResponse_({ ok: true, mensaje: 'Migración verde→azul completada.' });
   }
   ```
   (o el equivalente con `HtmlService`, según el patrón que ya usan las otras acciones —
   se entrega el bloque exacto a pegar cuando llegue este paso).
3. Se sube este `index.html` a GitHub Pages (reemplaza sólo ese archivo).

Hasta que el paso 2 esté hecho, el botón puede subirse tal cual (queda visible, con su nota
de "en validación manual"), pero no debe usarse todavía para una migración real.

## Archivos de este paquete
Idénticos a `POSTVENTA_BDC_GITHUB_v12_11_0_NOSHOWS.zip`, salvo `index.html` (actualizado)
y este README nuevo.
