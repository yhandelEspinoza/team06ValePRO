# ---------------------------------------------------------
# IMPORTACIÓN DE LIBRERÍAS
# ---------------------------------------------------------

from pathlib import Path

import gspread

from tabulate import tabulate


# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------

SPREADSHEET_ID = "1PV09vawEnQE5wAqj4JZarJUuQIjLhg7Ii7eV2WHzUGI"

HOJA_SOLICITUDES = "SOLICITUDES"
HOJA_FIRMAS = "FIRMAS"


# ---------------------------------------------------------
# RUTA DEL ARCHIVO DE CREDENCIALES
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

RUTA_CREDENCIALES = BASE_DIR / "credenciales.json"


# ---------------------------------------------------------
# CONEXIÓN CON GOOGLE SHEETS
# ---------------------------------------------------------

def conectar_archivo():
    """
    Conecta con la hoja principal de Valpro utilizando
    la cuenta de servicio configurada en credenciales.json.
    """

    if not RUTA_CREDENCIALES.exists():
        raise FileNotFoundError(
            f"No se encontró credenciales.json en: {RUTA_CREDENCIALES}"
        )

    cliente = gspread.service_account(
        filename=str(RUTA_CREDENCIALES)
    )

    archivo = cliente.open_by_key(SPREADSHEET_ID)

    return archivo


# ---------------------------------------------------------
# OBTENER SOLICITUDES
# ---------------------------------------------------------

def obtener_solicitudes():
    """
    Recupera todos los registros de la hoja SOLICITUDES.
    """

    archivo = conectar_archivo()

    hoja = archivo.worksheet(HOJA_SOLICITUDES)

    solicitudes = hoja.get_all_records()

    return solicitudes


# ---------------------------------------------------------
# OBTENER DATOS
# ---------------------------------------------------------

def obtener_datos():
    """
    Función utilizada por analisis.py.

    Devuelve las solicitudes registradas en Google Sheets.
    """

    return obtener_solicitudes()


# ---------------------------------------------------------
# OBTENER FIRMAS
# ---------------------------------------------------------

def obtener_firmas():
    """
    Recupera todos los registros de la hoja FIRMAS.
    """

    archivo = conectar_archivo()

    hoja = archivo.worksheet(HOJA_FIRMAS)

    firmas = hoja.get_all_records()

    return firmas


# ---------------------------------------------------------
# OBTENER DATOS PARA EL DASHBOARD
# ---------------------------------------------------------

def obtener_datos_dashboard():
    """
    Recupera la información necesaria para app.py.

    Retorna dos listas:

    1. solicitudes
    2. firmas

    Esto permite que app.py pueda hacer:

    solicitudes, firmas = obtener_datos_dashboard()
    """

    archivo = conectar_archivo()

    hoja_solicitudes = archivo.worksheet(HOJA_SOLICITUDES)
    hoja_firmas = archivo.worksheet(HOJA_FIRMAS)

    solicitudes = hoja_solicitudes.get_all_records()
    firmas = hoja_firmas.get_all_records()

    return solicitudes, firmas


# ---------------------------------------------------------
# MOSTRAR SOLICITUDES EN TERMINAL
# ---------------------------------------------------------

def mostrar_solicitudes(datos):
    """
    Muestra las solicitudes principales en formato de tabla.
    """

    if not datos:
        print("No hay solicitudes registradas.")
        return

    columnas = [
        "Código",
        "Registro",
        "Estado",
        "Solicitante",
        "DNI / CE",
        "Monto",
        "Área",
        "Categoría",
        "Uso previsto",
    ]

    tabla = []

    for solicitud in datos:

        fila = [
            solicitud.get(columna, "")
            for columna in columnas
        ]

        tabla.append(fila)

    print(
        tabulate(
            tabla,
            headers=columnas,
            tablefmt="grid",
        )
    )


# ---------------------------------------------------------
# MOSTRAR FIRMAS EN TERMINAL
# ---------------------------------------------------------

def mostrar_firmas(datos):
    """
    Muestra las firmas principales en formato de tabla.
    """

    if not datos:
        print("No hay firmas registradas.")
        return

    columnas = [
        "ID Firma",
        "Código vale",
        "Registro",
        "Tipo",
        "Estado",
    ]

    tabla = []

    for firma in datos:

        fila = [
            firma.get(columna, "")
            for columna in columnas
        ]

        tabla.append(fila)

    print(
        tabulate(
            tabla,
            headers=columnas,
            tablefmt="grid",
        )
    )


# ---------------------------------------------------------
# PRUEBA DIRECTA DEL ARCHIVO
# ---------------------------------------------------------

if __name__ == "__main__":

    try:

        solicitudes, firmas = obtener_datos_dashboard()

        print("\n========================================")
        print("VALPRO - PRUEBA DE CONEXIÓN")
        print("========================================")

        print("\nConexión correcta.")

        print(
            f"Solicitudes encontradas: {len(solicitudes)}"
        )

        print(
            f"Firmas encontradas: {len(firmas)}"
        )

        print("\nSOLICITUDES")
        mostrar_solicitudes(solicitudes)

        print("\nFIRMAS")
        mostrar_firmas(firmas)

    except Exception as error:

        print("\n========================================")
        print("ERROR DE CONEXIÓN")
        print("========================================")

        print(error)