"""Lecturas de Google Sheets con un cliente y una consulta conjunta por carga."""
from pathlib import Path
import os
import gspread
from google.auth.exceptions import GoogleAuthError
from requests.exceptions import RequestException
from tabulate import tabulate

BASE_DIR = Path(__file__).resolve().parent
SPREADSHEET_ID = os.environ.get("VALPRO_SPREADSHEET_ID", "1PV09vawEnQE5wAqj4JZarJUuQIjLhg7Ii7eV2WHzUGI")
RUTA_CREDENCIALES = Path(os.environ.get("VALPRO_CREDENTIALS", str(BASE_DIR / "credenciales.json")))
HOJA_SOLICITUDES = "SOLICITUDES"
HOJA_FIRMAS = "FIRMAS"
READONLY_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class ErrorSheets(RuntimeError):
    """Mensaje público seguro; nunca incluye respuesta cruda ni secretos."""


def _mensaje_error(exc):
    if isinstance(exc, FileNotFoundError):
        return "No se encontró el archivo de credenciales. Configure VALPRO_CREDENTIALS en el servidor."
    if isinstance(exc, (GoogleAuthError, ValueError)):
        return "No se pudo autenticar con Google Sheets. Revise la cuenta de servicio y sus credenciales."
    if isinstance(exc, (PermissionError, gspread.exceptions.SpreadsheetNotFound)):
        return "No se puede abrir la hoja. Revise su identificador y compártala con la cuenta de servicio como lector."
    if isinstance(exc, gspread.exceptions.APIError):
        codigo = getattr(exc.response, "status_code", None)
        if codigo in (401, 403):
            return "Google Sheets rechazó el acceso. Revise permisos y habilitación de la API."
        if codigo == 429:
            return "Google Sheets alcanzó su límite de consultas. Espere un momento y vuelva a intentar."
        if codigo == 400:
            return "No se pudieron leer SOLICITUDES y FIRMAS. Revise los nombres de las hojas."
    if isinstance(exc, RequestException):
        return "No se pudo conectar con Google Sheets dentro del tiempo permitido. Vuelva a intentar."
    return "Google Sheets no está disponible. Revise la configuración y vuelva a intentar."


def conectar_archivo():
    try:
        cliente = gspread.service_account(filename=str(RUTA_CREDENCIALES), scopes=READONLY_SCOPES)
        cliente.set_timeout((5, 15))
        return cliente.open_by_key(SPREADSHEET_ID)
    except (OSError, ValueError, GoogleAuthError, RequestException, gspread.exceptions.GSpreadException) as exc:
        raise ErrorSheets(_mensaje_error(exc)) from None


def _registros(valores, nombre):
    if not valores:
        return []
    encabezados = [str(v).strip() for v in valores[0]]
    no_vacios = [v for v in encabezados if v]
    if len(no_vacios) != len(set(no_vacios)):
        raise ErrorSheets(f"La hoja {nombre} tiene encabezados duplicados.")
    requeridos = {"Código", "Estado", "Monto", "Área", "Categoría"} if nombre == HOJA_SOLICITUDES else {"Código vale", "URL archivo"}
    if not requeridos.issubset(encabezados):
        raise ErrorSheets(f"Faltan columnas requeridas en {nombre}: {', '.join(sorted(requeridos - set(encabezados)))}.")
    registros = []
    for fila in valores[1:]:
        if any(str(v).strip() for v in fila[len(encabezados):]):
            raise ErrorSheets(f"La hoja {nombre} tiene datos en columnas sin encabezado.")
        if any(str(v).strip() and not encabezados[i] for i, v in enumerate(fila[:len(encabezados)])):
            raise ErrorSheets(f"La hoja {nombre} tiene datos en columnas sin encabezado.")
        registros.append({k: fila[i] if i < len(fila) else "" for i, k in enumerate(encabezados) if k})
    return registros


def _leer_hojas(nombres):
    try:
        archivo = conectar_archivo()
        respuesta = archivo.values_batch_get(
            [f"'{nombre}'" for nombre in nombres],
            params={"valueRenderOption": "FORMATTED_VALUE"},
        )
        rangos = respuesta.get("valueRanges", [])
        if len(rangos) != len(nombres):
            raise ErrorSheets("La respuesta de Google Sheets está incompleta. Vuelva a intentar.")
        return tuple(_registros(rango.get("values", []), nombre) for rango, nombre in zip(rangos, nombres))
    except ErrorSheets:
        raise
    except (OSError, ValueError, GoogleAuthError, RequestException, gspread.exceptions.GSpreadException) as exc:
        raise ErrorSheets(_mensaje_error(exc)) from None


def obtener_datos_dashboard():
    return _leer_hojas([HOJA_SOLICITUDES, HOJA_FIRMAS])


def obtener_solicitudes():
    return _leer_hojas([HOJA_SOLICITUDES])[0]


def obtener_datos():
    return obtener_solicitudes()


def obtener_firmas():
    return _leer_hojas([HOJA_FIRMAS])[0]


def mostrar_solicitudes(datos):
    columnas = ["Código", "Registro", "Estado", "Solicitante", "DNI / CE", "Monto", "Área", "Categoría", "Uso previsto"]
    print(tabulate([[r.get(c, "") for c in columnas] for r in datos], headers=columnas, tablefmt="grid") if datos else "No hay solicitudes registradas.")


def mostrar_firmas(datos):
    columnas = ["ID Firma", "Código vale", "Registro", "Tipo", "Estado"]
    print(tabulate([[r.get(c, "") for c in columnas] for r in datos], headers=columnas, tablefmt="grid") if datos else "No hay firmas registradas.")


if __name__ == "__main__":
    try:
        solicitudes, firmas = obtener_datos_dashboard()
        print(f"Conexión correcta: {len(solicitudes)} solicitudes; {len(firmas)} firmas.")
        mostrar_solicitudes(solicitudes)
        mostrar_firmas(firmas)
    except ErrorSheets as exc:
        print(exc)
        raise SystemExit(1)
