import io
import pytest
import matplotlib.pyplot as plt
import graficos
from analisis import MontoInvalido

FUNCIONES=[graficos.grafico_solicitudes_por_estado,graficos.grafico_solicitudes_por_area,
           graficos.grafico_solicitudes_por_categoria,graficos.grafico_monto_por_categoria,
           graficos.grafico_distribucion_estados]


@pytest.mark.parametrize('fn',FUNCIONES)
@pytest.mark.parametrize('vacio',[True,False])
def test_generacion_real_de_imagen(fn,vacio,registros):
    figura=fn([] if vacio else registros,mostrar=False)
    try:
        archivo=io.BytesIO()
        figura.savefig(archivo,format='png')
        assert archivo.getvalue().startswith(b'\x89PNG')
        if vacio:
            assert any(t.get_text()=='Sin datos' for t in figura.axes[0].texts)
        elif fn==graficos.grafico_monto_por_categoria:
            assert sum(b.get_height() for b in figura.axes[0].patches)==550.75
        elif fn!=graficos.grafico_distribucion_estados:
            assert sum(b.get_height() for b in figura.axes[0].patches)==4
    finally:
        plt.close(figura)


def test_grafico_monto_invalido_no_dibuja_cero():
    with pytest.raises(MontoInvalido):
        graficos.grafico_monto_por_categoria([{'Monto':'erróneo'}],mostrar=False)
