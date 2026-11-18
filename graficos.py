"""Gráficos Matplotlib. Las funciones devuelven Figure y permiten no abrir ventanas."""
import matplotlib.pyplot as plt
from analisis import contar_por_estado, agrupar_por_area, agrupar_por_categoria, calcular_monto_por_categoria


def _barras(resumen, titulo, eje, ylabel, mostrar):
    figura, ax = plt.subplots(figsize=(9, 5))
    ax.bar(list(resumen), list(resumen.values()))
    ax.set(title=titulo, xlabel=eje, ylabel=ylabel)
    ax.tick_params(axis='x', labelrotation=25)
    if not resumen:
        ax.text(.5, .5, 'Sin datos', ha='center', transform=ax.transAxes)
    figura.tight_layout()
    if mostrar:
        plt.show()
    return figura


def grafico_solicitudes_por_estado(registros, mostrar=True):
    return _barras(contar_por_estado(registros), 'Solicitudes por estado', 'Estado', 'Cantidad de solicitudes', mostrar)


def grafico_solicitudes_por_area(registros, mostrar=True):
    return _barras(agrupar_por_area(registros), 'Solicitudes por área', 'Área', 'Cantidad de solicitudes', mostrar)


def grafico_solicitudes_por_categoria(registros, mostrar=True):
    return _barras(agrupar_por_categoria(registros), 'Solicitudes por categoría', 'Categoría', 'Cantidad de solicitudes', mostrar)


def grafico_monto_por_categoria(registros, mostrar=True):
    return _barras(calcular_monto_por_categoria(registros), 'Monto solicitado por categoría', 'Categoría', 'Monto solicitado (S/)', mostrar)


def grafico_distribucion_estados(registros, mostrar=True):
    resumen = contar_por_estado(registros)
    figura, ax = plt.subplots(figsize=(7, 7))
    if resumen:
        ax.pie(list(resumen.values()), labels=list(resumen), autopct='%1.1f%%', startangle=90)
    else:
        ax.text(.5, .5, 'Sin datos', ha='center', transform=ax.transAxes)
    ax.set_title('Distribución de solicitudes por estado')
    figura.tight_layout()
    if mostrar:
        plt.show()
    return figura


if __name__ == '__main__':
    import os
    from analisis import preparar_solicitudes
    from conexion_sheets import obtener_datos
    from demo import obtener_datos_demo
    datos = obtener_datos_demo()[0] if os.environ.get('VALPRO_DEMO') == '1' else obtener_datos()
    registros, avisos = preparar_solicitudes(datos)
    for aviso in avisos:
        print(aviso)
    for funcion in (grafico_solicitudes_por_estado, grafico_solicitudes_por_area,
                    grafico_solicitudes_por_categoria, grafico_monto_por_categoria,
                    grafico_distribucion_estados):
        funcion(registros)
