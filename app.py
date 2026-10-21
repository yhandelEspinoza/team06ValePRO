# ---------------------------------------------------------
# IMPORTACIÓN DE LIBRERÍAS
# ---------------------------------------------------------

# datetime nos permite obtener la fecha y hora actual
# para mostrar cuándo se actualizó por última vez el dashboard.
from datetime import datetime

# Flask crea la aplicación web.
# render_template() permite cargar un archivo HTML desde templates.
from flask import Flask, render_template

# Importamos la función que obtiene los datos principales
# desde Google Sheets.
from conexion_sheets import obtener_datos_dashboard

# Importamos las funciones de análisis que se usarán
# para calcular indicadores y preparar los gráficos.
from analisis import (
    contar_solicitudes,
    contar_estado,
    calcular_monto_total,
    calcular_monto_promedio,
    contar_por_estado,
    agrupar_por_area,
    agrupar_por_categoria,
    calcular_monto_por_categoria,
    obtener_estado_predominante,
    obtener_area_mas_solicitudes,
    obtener_categoria_mas_usada,
)


# ---------------------------------------------------------
# CREACIÓN DE LA APLICACIÓN FLASK
# ---------------------------------------------------------

# Flask(__name__) crea la aplicación web.
# __name__ ayuda a Flask a identificar la ubicación
# de nuestro archivo y de las carpetas templates y static.
app = Flask(__name__)


# ---------------------------------------------------------
# FUNCIÓN PARA LIMPIAR TEXTO
# ---------------------------------------------------------

def texto_limpio(valor):
    """
    Convierte cualquier valor a texto limpio y seguro
    para poder compararlo o mostrarlo en el dashboard.
    """

    # Si el valor recibido es None, devolvemos una cadena vacía
    # para evitar errores al convertirlo o compararlo.
    if valor is None:
        return ""

    # str() convierte el valor a texto.
    # strip() elimina espacios al inicio y al final.
    return str(valor).strip()


# ---------------------------------------------------------
# CREAR ÍNDICE DE FIRMAS
# ---------------------------------------------------------

def indexar_firmas(firmas):
    """
    Crea un diccionario donde cada firma queda identificada
    mediante el Código vale.

    Esto permite encontrar rápidamente la firma correspondiente
    a cada solicitud.
    """

    # Creamos un diccionario vacío donde guardaremos las firmas.
    indice = {}

    # Recorremos todas las firmas recuperadas desde Google Sheets.
    for firma in firmas:

        # get() obtiene el Código vale del diccionario.
        # texto_limpio() elimina espacios o valores no válidos.
        codigo = texto_limpio(
            firma.get("Código vale", "")
        )

        # Solo guardamos la firma si existe un código válido.
        if codigo:

            # Usamos el código del vale como clave del diccionario.
            # Si el mismo código aparece más de una vez,
            # se conserva la última firma encontrada.
            indice[codigo] = firma

    return indice


# ---------------------------------------------------------
# RELACIONAR SOLICITUDES CON SUS FIRMAS
# ---------------------------------------------------------

def enriquecer_solicitudes_con_firmas(solicitudes, firmas):
    """
    Relaciona SOLICITUDES.Código con FIRMAS.Código vale.

    La información original de Google Sheets no se modifica.
    Se crean nuevos registros solamente para mostrarlos
    dentro del dashboard.
    """

    # Primero organizamos las firmas en un diccionario
    # para poder buscarlas rápidamente por código.
    indice_firmas = indexar_firmas(firmas)

    # Aquí guardaremos las solicitudes ya enriquecidas.
    resultado = []

    # Recorremos cada solicitud registrada.
    for solicitud in solicitudes:

        # dict() crea una copia de la solicitud original.
        # De esta forma podemos agregar nuevos campos
        # sin modificar los datos obtenidos desde Google Sheets.
        registro = dict(solicitud)

        # Obtenemos el Código de la solicitud.
        codigo = texto_limpio(
            solicitud.get("Código", "")
        )

        # get() busca ese código dentro del índice de firmas.
        # Si no existe, devuelve None.
        firma = indice_firmas.get(codigo)

        # Si encontramos una firma asociada al vale:
        if firma:

            # Obtenemos la URL del archivo donde se guarda la firma.
            url_firma = texto_limpio(
                firma.get("URL archivo", "")
            )

            # bool() convierte el valor en True o False.
            # Si existe una URL válida, la firma está disponible.
            registro["firma_disponible"] = bool(url_firma)

            # Agregamos campos adicionales que serán utilizados
            # solamente por la interfaz del dashboard.
            registro["firma_url"] = url_firma

            registro["firma_tipo"] = texto_limpio(
                firma.get("Tipo", "")
            )

            registro["firma_estado"] = texto_limpio(
                firma.get("Estado", "")
            )

            registro["firma_registro"] = texto_limpio(
                firma.get("Registro", "")
            )

            registro["firma_id"] = texto_limpio(
                firma.get("ID Firma", "")
            )

        else:
            # Si la solicitud todavía no tiene firma,
            # asignamos valores vacíos o un estado pendiente.
            registro["firma_disponible"] = False
            registro["firma_url"] = ""
            registro["firma_tipo"] = ""
            registro["firma_estado"] = "PENDIENTE"
            registro["firma_registro"] = ""
            registro["firma_id"] = ""

        # append() agrega el registro procesado
        # al final de la lista resultado.
        resultado.append(registro)

    return resultado


# ---------------------------------------------------------
# RUTA PRINCIPAL DEL DASHBOARD
# ---------------------------------------------------------

# @app.route("/") indica que esta función se ejecutará
# cuando el usuario visite la página principal.
@app.route("/")
def dashboard():

    # Guardamos aquí un posible mensaje de error.
    error = None

    # Por defecto asumimos que la conexión funciona.
    conexion_correcta = True

    try:
        # obtener_datos_dashboard() recupera las solicitudes
        # y las firmas desde Google Sheets.
        solicitudes, firmas = obtener_datos_dashboard()


        # -------------------------------------------------
        # CÁLCULO DE INDICADORES PRINCIPALES
        # -------------------------------------------------

        # Creamos un diccionario con los indicadores
        # que se mostrarán en la parte superior del dashboard.
        indicadores = {

            # Número total de solicitudes registradas.
            "total_solicitudes": contar_solicitudes(solicitudes),

            # Cantidad de solicitudes pendientes de firma.
            "pendiente_firma": contar_estado(
                solicitudes,
                "PENDIENTE FIRMA"
            ),

            # Cantidad de solicitudes pendientes de revisión del jefe.
            "pendiente_jefe": contar_estado(
                solicitudes,
                "PENDIENTE JEFE"
            ),

            # Cantidad de solicitudes aprobadas.
            "aprobadas": contar_estado(
                solicitudes,
                "APROBADO"
            ),

            # Cantidad de solicitudes rechazadas.
            "rechazadas": contar_estado(
                solicitudes,
                "RECHAZADO"
            ),

            # Suma de todos los montos solicitados.
            "monto_total": calcular_monto_total(
                solicitudes
            ),

            # Promedio de los montos solicitados.
            "monto_promedio": calcular_monto_promedio(
                solicitudes
            ),
        }


        # -------------------------------------------------
        # DATOS PARA LOS GRÁFICOS
        # -------------------------------------------------

        # contar_por_estado() agrupa las solicitudes
        # según su estado.
        estados = contar_por_estado(solicitudes)

        # agrupar_por_area() cuenta cuántas solicitudes
        # existen por cada área.
        areas = agrupar_por_area(solicitudes)

        # agrupar_por_categoria() cuenta las solicitudes
        # registradas en cada categoría.
        categorias = agrupar_por_categoria(solicitudes)

        # calcular_monto_por_categoria() suma los montos
        # correspondientes a cada categoría.
        montos_categoria = calcular_monto_por_categoria(
            solicitudes
        )


        # -------------------------------------------------
        # DATOS DESTACADOS
        # -------------------------------------------------

        # Esta función devuelve dos resultados:
        # el estado más frecuente y su cantidad.
        estado_predominante, cantidad_estado = (
            obtener_estado_predominante(solicitudes)
        )

        # Obtenemos el área con más solicitudes
        # y la cantidad correspondiente.
        area_principal, cantidad_area = (
            obtener_area_mas_solicitudes(solicitudes)
        )

        # Obtenemos la categoría más utilizada
        # y cuántas solicitudes tiene.
        categoria_principal, cantidad_categoria = (
            obtener_categoria_mas_usada(solicitudes)
        )

        # Organizamos los valores destacados
        # dentro de un único diccionario.
        destacados = {
            "estado_predominante": estado_predominante,
            "cantidad_estado": cantidad_estado,
            "area_principal": area_principal,
            "cantidad_area": cantidad_area,
            "categoria_principal": categoria_principal,
            "cantidad_categoria": cantidad_categoria,
        }


        # -------------------------------------------------
        # RELACIÓN ENTRE SOLICITUDES Y FIRMAS
        # -------------------------------------------------

        # Agregamos a cada solicitud la información
        # relacionada con su firma para mostrarla en la interfaz.
        registros = enriquecer_solicitudes_con_firmas(
            solicitudes,
            firmas
        )


    # -----------------------------------------------------
    # MANEJO DE ERRORES
    # -----------------------------------------------------

    # Si ocurre cualquier error dentro del bloque try,
    # Python entra en este bloque except.
    except Exception as exc:

        # Indicamos que la conexión no fue correcta.
        conexion_correcta = False

        # str() convierte el error recibido en texto
        # para poder mostrarlo en el dashboard.
        error = str(exc)

        # Si existe un error dejamos vacíos los registros.
        registros = []

        # Colocamos todos los indicadores en cero
        # para evitar errores dentro de la interfaz.
        indicadores = {
            "total_solicitudes": 0,
            "pendiente_firma": 0,
            "pendiente_jefe": 0,
            "aprobadas": 0,
            "rechazadas": 0,
            "monto_total": 0,
            "monto_promedio": 0,
        }

        # También dejamos vacíos los datos de los gráficos.
        estados = {}
        areas = {}
        categorias = {}
        montos_categoria = {}

        # Valores predeterminados para los datos destacados.
        destacados = {
            "estado_predominante": "-",
            "cantidad_estado": 0,
            "area_principal": "-",
            "cantidad_area": 0,
            "categoria_principal": "-",
            "cantidad_categoria": 0,
        }


    # ---------------------------------------------------------
    # FECHA Y HORA DE ACTUALIZACIÓN
    # ---------------------------------------------------------

    # datetime.now() obtiene la fecha y hora actual.
    # strftime() permite mostrarla con el formato que queremos.
    ultima_actualizacion = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


    # ---------------------------------------------------------
    # ENVÍO DE DATOS AL HTML
    # ---------------------------------------------------------

    # render_template() carga dashboard.html
    # y envía todos los datos calculados desde Python.
    return render_template(
        "dashboard.html",

        # Solicitudes que se mostrarán en la tabla.
        registros=registros,

        # Indicadores y valores destacados.
        indicadores=indicadores,
        destacados=destacados,

        # keys() obtiene las claves del diccionario.
        # values() obtiene sus valores.
        # list() convierte esos resultados en listas
        # para utilizarlos desde JavaScript y Chart.js.
        estados_labels=list(estados.keys()),
        estados_valores=list(estados.values()),

        areas_labels=list(areas.keys()),
        areas_valores=list(areas.values()),

        categorias_labels=list(categorias.keys()),
        categorias_valores=list(categorias.values()),

        montos_categoria_labels=list(
            montos_categoria.keys()
        ),

        montos_categoria_valores=list(
            montos_categoria.values()
        ),

        # Información sobre el estado de la conexión.
        conexion_correcta=conexion_correcta,
        error=error,

        # Fecha y hora de la última carga.
        ultima_actualizacion=ultima_actualizacion,
    )


# ---------------------------------------------------------
# EJECUCIÓN DEL SERVIDOR FLASK
# ---------------------------------------------------------

# Este bloque solamente se ejecuta cuando usamos:
# python app.py
if __name__ == "__main__":

    # app.run() inicia el servidor web local de Flask.
    app.run(

        # El servidor solamente estará disponible
        # desde esta computadora.
        host="127.0.0.1",

        # Flask utilizará el puerto 5000.
        port=5000,

        # debug=True permite mostrar errores detallados
        # mientras desarrollamos el proyecto.
        debug=True,

        # Desactivamos el reloader automático para evitar
        # que Flask ejecute ciertas partes dos veces.
        use_reloader=False,
    )