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
