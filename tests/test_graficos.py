import pytest
import plotly.graph_objects as go
import graficos
from analisis import MontoInvalido

FUNCIONES = [
    graficos.grafico_solicitudes_por_estado,
    graficos.grafico_solicitudes_por_area,
    graficos.grafico_solicitudes_por_categoria,
    graficos.grafico_monto_por_categoria,
    graficos.grafico_distribucion_estados,
]

@pytest.mark.parametrize('fn', FUNCIONES)
@pytest.mark.parametrize('vacio', [True, False])
def test_figuras_plotly_desde_registros(fn, vacio, registros):
    figura = fn([] if vacio else registros)
    assert isinstance(figura, go.Figure)
    assert figura.layout.height == 300
    if vacio:
        assert len(figura.data) == 0
    else:
        assert len(figura.data) == 1
        traza = figura.data[0]
        valores = traza.values if traza.type == 'pie' else traza.y
        esperado = 550.75 if fn == graficos.grafico_monto_por_categoria else 4
        assert sum(valores) == pytest.approx(esperado)
        assert traza.type == ('pie' if fn in (graficos.grafico_solicitudes_por_categoria, graficos.grafico_distribucion_estados) else 'bar')
        assert figura.to_json()


def test_grafico_monto_invalido_no_dibuja_cero():
    with pytest.raises(MontoInvalido):
        graficos.grafico_monto_por_categoria([{'Monto': 'erróneo'}])
