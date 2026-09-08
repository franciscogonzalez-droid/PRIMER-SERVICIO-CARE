CORRECCIÓN v12.9.2
===================

Se corrigió un error de inicialización JavaScript de v12.9.1.
WORKED_DATA se calculaba antes de declarar norm(), provocando un ReferenceError
al iniciar la página. Por eso el HTML se veía, pero pestañas, filtros, KPIs,
gráficas y botones quedaban sin funcionar.

No cambia la lógica de negocio ni los datos.
No requiere cambio de Apps Script.

SUBIDA A GITHUB
1. Descomprime POSTVENTA_BDC_GITHUB_v12_9_2.zip.
2. Sube TODOS los archivos del paquete y reemplaza los existentes.
3. Commit a main.
4. Espera GitHub Pages.
5. Abre el sitio y usa Ctrl+F5.

VALIDACIÓN RÁPIDA
- Debe mostrar v12.9.2 GitHub.
- Los KPI deben mostrar números.
- Las pestañas deben cambiar.
- Restablecer filtros debe funcionar.
- Al seleccionar Agencia, se habilita Generar / actualizar Google Sheet.
