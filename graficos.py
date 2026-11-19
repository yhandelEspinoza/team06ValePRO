"""Figuras Plotly creadas exclusivamente desde los registros analizados en Python."""
import plotly.graph_objects as go
from analisis import contar_por_estado, agrupar_por_area, agrupar_por_categoria, calcular_monto_por_categoria

PALETA = ['#2563eb', '#0ea5e9', '#7c3aed', '#16a34a', '#d97706', '#dc2626', '#0891b2']
COLORES_ESTADO = {'PENDIENTE FIRMA': '#d97706', 'PENDIENTE JEFE': '#0ea5e9',
                  'APROBADO': '#16a34a', 'RECHAZADO': '#dc2626'}


def _base(figura, circular=False):
    figura.update_layout(
        template='plotly_white', margin=dict(l=38, r=12, t=12, b=38),
        height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Segoe UI, Arial, sans-serif', color='#64748b'),
        showlegend=circular,
        legend=dict(orientation='h', y=-0.12, x=0, font=dict(size=11)),
    )
    if not circular:
        figura.update_xaxes(showgrid=False, automargin=True)
        figura.update_yaxes(rangemode='tozero', gridcolor='#eef2f7', automargin=True)
    return figura


def _barras(resumen, etiqueta, dinero=False, estados=False):
    if not resumen:
        return _base(go.Figure())
    nombres, valores = list(resumen), list(resumen.values())
    figura = go.Figure(go.Bar(x=nombres, y=valores))
    figura.update_traces(
        marker_color=[COLORES_ESTADO.get(n, PALETA[i % len(PALETA)]) if estados else PALETA[i % len(PALETA)] for i,n in enumerate(nombres)],
        marker_cornerradius=8,
        hovertemplate='%{x}<br>S/ %{y:,.2f}<extra></extra>' if dinero else '%{x}<br>%{y} solicitudes<extra></extra>',
    )
    if dinero:
        figura.update_yaxes(tickprefix='S/ ')
    else:
        figura.update_yaxes(dtick=1)
    figura.update_xaxes(title_text=etiqueta)
    figura.update_yaxes(title_text='Monto (S/)' if dinero else 'Solicitudes')
    return _base(figura)


def grafico_solicitudes_por_estado(registros):
    return _barras(contar_por_estado(registros), 'Estado', estados=True)


def grafico_solicitudes_por_area(registros):
    return _barras(agrupar_por_area(registros), 'Área')


def grafico_solicitudes_por_categoria(registros):
    """Gráfico circular de solicitudes agrupadas por categoría."""
    resumen = agrupar_por_categoria(registros)
    if not resumen:
        return _base(go.Figure(), circular=True)
    figura = go.Figure(go.Pie(labels=list(resumen), values=list(resumen.values()),
                             hole=0.64, marker_colors=PALETA))
    figura.update_traces(textinfo='none', hovertemplate='%{label}: %{value} solicitudes (%{percent})<extra></extra>')
    return _base(figura, circular=True)


def grafico_monto_por_categoria(registros):
    return _barras(calcular_monto_por_categoria(registros), 'Categoría', dinero=True)


def grafico_distribucion_estados(registros):
    """Vista alternativa existente del selector por estado."""
    resumen = contar_por_estado(registros)
    if not resumen:
        return _base(go.Figure(), circular=True)
    figura = go.Figure(go.Pie(labels=list(resumen), values=list(resumen.values()), hole=0.64,
                             marker_colors=[COLORES_ESTADO.get(k, PALETA[i % len(PALETA)]) for i,k in enumerate(resumen)]))
    figura.update_traces(textinfo='none', hovertemplate='%{label}: %{value} solicitudes (%{percent})<extra></extra>')
    return _base(figura, circular=True)


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
        figura = funcion(registros)
        print(funcion.__name__, '→', len(figura.data), 'trazas Plotly')
