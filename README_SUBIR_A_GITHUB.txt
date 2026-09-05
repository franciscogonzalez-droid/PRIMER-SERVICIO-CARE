PUBLICAR MONITOREO POSTVENTA BDC EN GITHUB PAGES
VERSIÓN v12.3 GitHub
============================================================

QUÉ CAMBIÓ
----------
El tablero original era un solo index.html de más de 25 MB.
GitHub no permite subir por su interfaz web un archivo individual de ese tamaño.

Esta versión separa:
- index.html = estructura, diseño y lógica.
- archivos data_*.js = bases de datos.

Todos los archivos individuales quedan por debajo de 25 MB.
Retenidos y Leales se dividieron en varias partes para dejar margen adicional.

IMPORTANTE
----------
NO abras ni edites los archivos data_*.js.
NO cambies sus nombres.
TODOS deben quedar en la misma carpeta del repositorio que index.html.

ARCHIVOS QUE DEBES SUBIR
------------------------
- index.html
- data_primer_servicio.js
- data_taller.js
- data_historicos.js
- data_citas_totales.js
- data_bdc_perdidos.js
- data_bdc_riesgos.js
- data_bdc_retenidos_01.js
- data_bdc_retenidos_02.js
- data_bdc_retenidos_03.js
- data_bdc_retenidos_04.js (si existe)
- data_bdc_leales_01.js
- data_bdc_leales_02.js
- data_bdc_leales_03.js
- data_bdc_leales_04.js (si existe)
- data_meta.js

También puedes subir este README, aunque no es obligatorio.

============================================================
A. SUBIR LOS ARCHIVOS A TU REPOSITORIO
============================================================

1. Descarga y DESCOMPRIME el ZIP que te entregó ChatGPT.

2. En GitHub abre tu repositorio:
   PRIMER-SERVICIO-CARE

3. En la pestaña Code, entra a:
   Add file > Upload files

4. Arrastra TODOS los archivos de la carpeta descomprimida.
   IMPORTANTE:
   - arrastra los archivos, no el ZIP;
   - index.html y todos los data_*.js deben quedar en el mismo nivel.

5. Espera a que GitHub termine de cargar TODOS los archivos.

6. En “Commit changes” puedes escribir:
   Actualización tablero Postventa BDC v12.3

7. Selecciona:
   Commit directly to the main branch

8. Pulsa:
   Commit changes

Si ya existe un index.html anterior, GitHub lo reemplazará al confirmar el commit.

============================================================
B. ACTIVAR GITHUB PAGES
============================================================

Si GitHub Pages YA estaba funcionando en este repositorio:
- no necesitas configurar esta sección otra vez;
- únicamente espera a que termine el nuevo despliegue.

Si todavía no está activado:

1. Ve a Settings del repositorio.

2. En el menú lateral busca:
   Pages

3. En “Build and deployment”:
   Source = Deploy from a branch

4. Selecciona:
   Branch = main
   Folder = / (root)

5. Pulsa Save.

6. GitHub mostrará la URL pública cuando termine el despliegue.

Normalmente la liga tendrá una estructura similar a:
https://TU-USUARIO.github.io/PRIMER-SERVICIO-CARE/

============================================================
C. VALIDAR QUE TODO CARGÓ
============================================================

Cuando abras la liga revisa:

1. Pestaña “Primer Servicio”
   - Debe mostrar el universo consolidado de 1,952 VIN.

2. Pestaña “Perdidos”
   - Debe mostrar datos y KPIs.

3. Pestaña “En riesgo”
   - Debe mostrar datos y KPIs.

4. Pestaña “Retenidos”
   - Debe mostrar datos y KPIs.

5. Pestaña “Leales”
   - Debe mostrar datos y KPIs.

6. Prueba los filtros.

7. Los botones verdes BDC seguirán utilizando la misma URL del Web App.

Si ves la versión anterior:
- espera 1 a 5 minutos;
- actualiza con Ctrl + F5;
- o abre la página en una ventana de incógnito.

============================================================
D. ACTUALIZACIONES FUTURAS
============================================================

Con esta estructura ya no es necesario que todo esté dentro de index.html.

Para una actualización futura:
- si cambia el diseño o la lógica, se reemplaza index.html;
- si cambian las bases, se reemplazan los data_*.js correspondientes;
- conserva siempre exactamente los mismos nombres de archivo.

Para reemplazar:
1. Add file > Upload files.
2. Sube los archivos nuevos con el mismo nombre.
3. Commit directly to main.
4. Espera el despliegue de GitHub Pages.

============================================================
E. ERROR MÁS COMÚN
============================================================

Si el tablero abre pero alguna pestaña aparece vacía:
- confirma que TODOS los data_*.js fueron subidos;
- confirma que están en la misma carpeta que index.html;
- confirma que ningún nombre cambió;
- revisa especialmente las partes de Retenidos y Leales.

No uses Git LFS para estos archivos.
GitHub Pages debe poder servirlos como archivos JavaScript normales.
