# ---------------------------------------------------------
# IMPORTACIÓN DE LIBRERÍAS Y FUNCIONES
# ---------------------------------------------------------

# pyplot es el módulo de Matplotlib que utilizamos
# para crear y mostrar los gráficos.
import matplotlib.pyplot as plt

# Importamos obtener_datos() para recuperar
# las solicitudes directamente desde Google Sheets.
from conexion_sheets import obtener_datos

# Importamos las funciones de analisis.py que preparan
# la información necesaria para construir los gráficos.
from analisis import (
    contar_por_estado,
    agrupar_por_area,
    calcular_monto_por_categoria
)


# ---------------------------------------------------------
# GRÁFICO DE SOLICITUDES POR ESTADO
# ---------------------------------------------------------

def grafico_solicitudes_por_estado(registros):
    """
    Muestra un gráfico de barras con la cantidad
    de solicitudes registradas en cada estado.
    """

    # contar_por_estado() devuelve un diccionario donde
    # cada estado está relacionado con su cantidad.
    resumen = contar_por_estado(registros)

    # keys() obtiene los nombres de los estados.
    # list() los convierte en una lista para utilizarlos
    # como etiquetas del gráfico.
    estados = list(resumen.keys())

    # values() obtiene las cantidades de cada estado.
    cantidades = list(resumen.values())

    # figure() crea una nueva figura para el gráfico.
    # figsize=(9, 5) establece su tamaño en pulgadas:
    # 9 de ancho y 5 de alto.
    plt.figure(figsize=(9, 5))

    # bar() crea un gráfico de barras.
    # estados se utiliza en el eje horizontal
    # y cantidades representa la altura de cada barra.
    plt.bar(estados, cantidades)

    # title() establece el título principal del gráfico.
    plt.title("Solicitudes por estado")

    # xlabel() y ylabel() colocan los nombres
    # de los ejes horizontal y vertical.
    plt.xlabel("Estado")
    plt.ylabel("Cantidad de solicitudes")

    # xticks() modifica las etiquetas del eje horizontal.
    # rotation=25 las gira para facilitar su lectura.
    plt.xticks(rotation=25)

    # tight_layout() ajusta automáticamente los espacios
    # para evitar que títulos o etiquetas queden cortados.
    plt.tight_layout()

    # show() muestra finalmente el gráfico en pantalla.
    plt.show()


# ---------------------------------------------------------
# GRÁFICO DE SOLICITUDES POR ÁREA
# ---------------------------------------------------------

def grafico_solicitudes_por_area(registros):
    """
    Muestra un gráfico de barras con la cantidad
    de solicitudes registradas en cada área.
    """

    # agrupar_por_area() devuelve un diccionario
    # con cada área y su cantidad de solicitudes.
    resumen = agrupar_por_area(registros)

    # Obtenemos los nombres de las áreas.
    areas = list(resumen.keys())

    # Obtenemos las cantidades asociadas a cada área.
    cantidades = list(resumen.values())

    # Creamos una nueva figura independiente.
    plt.figure(figsize=(9, 5))

    # Construimos el gráfico de barras.
    plt.bar(areas, cantidades)

    # Agregamos el título y los nombres de los ejes.
    plt.title("Solicitudes por área")
    plt.xlabel("Área")
    plt.ylabel("Cantidad de solicitudes")

    # Giramos las etiquetas para que los nombres
    # de las áreas puedan visualizarse correctamente.
    plt.xticks(rotation=25)

    # Ajustamos automáticamente el espacio disponible.
    plt.tight_layout()

    # Mostramos el gráfico.
    plt.show()


# ---------------------------------------------------------
# GRÁFICO DE MONTO POR CATEGORÍA
# ---------------------------------------------------------

def grafico_monto_por_categoria(registros):
    """
    Muestra un gráfico de barras con el monto total
    solicitado dentro de cada categoría.
    """

    # calcular_monto_por_categoria() suma los montos
    # de las solicitudes pertenecientes a cada categoría.
    resumen = calcular_monto_por_categoria(registros)

    # keys() obtiene los nombres de las categorías.
    categorias = list(resumen.keys())

    # values() obtiene el dinero acumulado
    # correspondiente a cada categoría.
    montos = list(resumen.values())

    # Creamos una figura de 9 pulgadas de ancho
    # y 5 pulgadas de alto.
    plt.figure(figsize=(9, 5))

    # Creamos las barras utilizando las categorías
    # en el eje X y los montos en el eje Y.
    plt.bar(categorias, montos)

    # Definimos el título del gráfico.
    plt.title("Monto solicitado por categoría")

    # Indicamos qué representa cada eje.
    plt.xlabel("Categoría")
    plt.ylabel("Monto solicitado (S/)")

    # Rotamos las categorías para mejorar su lectura.
    plt.xticks(rotation=25)

    # Ajustamos los elementos dentro de la figura.
    plt.tight_layout()

    # Mostramos el gráfico generado.
    plt.show()


# ---------------------------------------------------------
# GRÁFICO DE DISTRIBUCIÓN DE ESTADOS
# ---------------------------------------------------------

def grafico_distribucion_estados(registros):
    """
    Muestra un gráfico circular con el porcentaje
    que representa cada estado del total de solicitudes.
    """

    # Reutilizamos contar_por_estado() para obtener
    # la cantidad de solicitudes en cada estado.
    resumen = contar_por_estado(registros)

    # Obtenemos los nombres de los estados.
    estados = list(resumen.keys())

    # Obtenemos sus cantidades.
    cantidades = list(resumen.values())

    # Creamos una figura cuadrada porque utilizaremos
    # un gráfico circular.
    plt.figure(figsize=(7, 7))

    # pie() crea un gráfico circular.
    plt.pie(
        cantidades,

        # labels indica el nombre que tendrá cada sección.
        labels=estados,

        # autopct muestra el porcentaje correspondiente
        # a cada sección con un decimal.
        autopct="%1.1f%%",

        # startangle=90 hace que el gráfico
        # comience a dibujarse desde 90 grados.
        startangle=90
    )

    # Establecemos el título del gráfico.
    plt.title("Distribución de solicitudes por estado")

    # Ajustamos automáticamente los márgenes.
    plt.tight_layout()

    # Mostramos el gráfico circular.
    plt.show()


# ---------------------------------------------------------
# PRUEBA DIRECTA DEL ARCHIVO
# ---------------------------------------------------------

# Este bloque solamente se ejecuta si utilizamos:
# python graficos.py
#
# Si graficos.py se importa desde otro archivo,
# este bloque no se ejecutará.
if __name__ == "__main__":

    # obtener_datos() recupera las solicitudes
    # almacenadas actualmente en Google Sheets.
    registros = obtener_datos()

    print("Generando gráficos de Vale Provisional...")

    # Generamos cada gráfico utilizando
    # los mismos registros recuperados de Google Sheets.
    grafico_solicitudes_por_estado(registros)

    grafico_solicitudes_por_area(registros)

    grafico_monto_por_categoria(registros)

    grafico_distribucion_estados(registros)