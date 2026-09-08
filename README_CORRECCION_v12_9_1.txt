POSTVENTA BDC · v12.9.1 · CORRECCIÓN GENERADOR POR AGENCIA
===========================================================

CORRECCIÓN PRINCIPAL
--------------------
El botón “Generar / actualizar Google Sheet” por Agencia no respondía porque
la función intentaba utilizar WORKED_DATA, variable que no estaba cargada en
el paquete optimizado de GitHub. El navegador generaba un error JavaScript
antes de mostrar la confirmación, por eso parecía que el botón no hacía nada.

v12.9.1 reconstruye el contexto WORKED_DATA a partir de DATA y agrega manejo
visible de errores.

ARQUITECTURA ACTUAL
-------------------
- Botón verde de Agencia:
  genera / actualiza el archivo individual de la Agencia y su Maestro.
- Botón global de Primer Servicio:
  actualiza BDC POSTVENTA con el universo completo.

El botón de Agencia ya NO debe reconstruir el BDC global, porque eso podría
volver a reducir el universo a una fuente parcial. Esta separación es intencional.

ADEMÁS
------
Se corrigieron las tarjetas de referencia del universo:
- Marca: 1,597
- Grupo exclusivo: 464
- Consolidado: 2,061

PASOS
-----
1. Subir todos los archivos v12.9.1 a GitHub reemplazando los anteriores.
2. Esperar GitHub Pages y actualizar con Ctrl+F5.
3. Elegir una agencia y probar “Generar / actualizar Google Sheet”.
4. Debe aparecer el cuadro de confirmación y abrir la respuesta del Web App.
5. Para actualizar BDC Primer Servicio, utilizar el botón global correspondiente.

APPS SCRIPT
-----------
No requiere cambiar Código.gs por esta corrección HTML.
Sí conviene confirmar que la implementación existente del Web App esté
actualizada a la versión V3.5.0 del código actual, conservando la misma URL.
