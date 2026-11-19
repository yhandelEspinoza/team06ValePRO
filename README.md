# VALPRO — versión estabilizada de team06.zip

El ZIP original de 18/11/2026 contenía `credenciales.json` y entornos virtuales de Windows. Este entregable contiene solamente código fuente, pruebas y recursos. No suba el ZIP original a GitHub.

## Ejecutar en Windows

```powershell
py -3.14 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest
$env:VALPRO_DEMO='1'
.venv\Scripts\python.exe app.py
```

Abra `http://127.0.0.1:5000/`. La demo usa datos ficticios. Para datos reales, quite `VALPRO_DEMO` y establezca `VALPRO_CREDENTIALS` a la ruta del archivo privado. Puede establecer `VALPRO_SPREADSHEET_ID` si cambia la hoja. No copie las credenciales al repositorio.

## Preparar Ubuntu / AWS sin tocar el servicio existente

```bash
python3.14 -m venv venv
venv/bin/python -m pip install -r requirements-dev.txt
venv/bin/python -m pytest
VALPRO_DEMO=1 venv/bin/gunicorn --bind 127.0.0.1:5001 --workers 2 --timeout 60 app:app
```

El puerto 5001 evita interferir con el servicio actual. Los ejemplos `deploy/` muestran Gunicorn, systemd y Nginx ligados a loopback. Antes de conmutar: confirmar pruebas en Ubuntu 26.04/Python 3.14, revisar `nginx -t`, estado de systemd, respuesta HTTP, reglas de Security Group y autenticación. No abrir 5000 a Internet.

## Presentación desde otra computadora

La computadora de exposición solo necesitará navegador cuando se habilite una URL HTTPS con autenticación. Actualmente no existe esa URL. Comprobar previamente acceso/login, siete KPI, cuatro gráficos, filtros, modales y consola del navegador. Si Sheets falla, usar una instancia de demostración separada con `VALPRO_DEMO=1` y comprobar que el aviso «DATOS FICTICIOS» sea visible. No exponer información real sin autenticación.

Las reglas de datos se documentan en `docs/DATOS.md`.

## Gráficos Plotly y demostración docente

Flujo: **Google Sheets → `conexion_sheets.py` (gspread y google-auth) → `analisis.py` (limpieza, KPI y agrupaciones) → `graficos.py` (figuras Plotly Graph Objects) → `app.py` (JSON de figuras) → `dashboard.html` y `static/js/dashboard.js` (Plotly.js en el navegador)**. Los cuatro gráficos visibles representan estado, categoría, área y monto por categoría. El selector de la segunda tarjeta también muestra la distribución por estado. Todas las figuras parten de los registros procesados en Python, sin valores fijos en JavaScript.

Se usa Graph Objects porque Plotly Express 7.1 requiere Pandas al recibir listas; esta aplicación ya obtiene agrupaciones simples en Python y no necesita una dependencia de tablas. El navegador carga el paquete Plotly.js local incluido en `static/vendor/`, sin CDN. No se cargan otros motores de gráficos.

Para demostrarlo sin credenciales: instale las dependencias, active `VALPRO_DEMO=1` y ejecute `app.py`. Muestre el aviso «DATOS FICTICIOS», los siete KPI y los cuatro gráficos. En las herramientas de desarrollo del navegador, compruebe `window.Plotly` y el elemento `#plotly-data`; este contiene las figuras serializadas por Flask. Cambie el selector «Agrupar por» y verifique el tema, la búsqueda, los filtros y el botón Limpiar. Ejecute `python -m pytest -q`; las pruebas validan tipos, trazas y sumas reales de las figuras, además de la respuesta Flask. Para datos reales use una cuenta autorizada de Sheets y nunca exponga `credenciales.json`.
