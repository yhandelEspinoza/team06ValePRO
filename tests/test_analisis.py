from copy import deepcopy
from decimal import Decimal
import pytest
from analisis import *


@pytest.mark.parametrize('valor,esperado', [
    (200,200), (200.25,200.25), ('200.25',200.25), ('200,25',200.25),
    ('S/ 1.200,50',1200.5), ('S/ 1,200.50',1200.5), ('S/. 1200',1200),
    ('1.234.567',1234567), ('1,234,567',1234567), ('0',0), ('0.00',0),
    (' -20,50 ',-20.5), (Decimal('1.25'),1.25), ('s/ 1.50',1.5),
])
def test_montos_validos(valor, esperado):
    assert normalizar_monto(valor) == esperado


@pytest.mark.parametrize('valor', [None, '', ' ', 'abc', True, False, float('nan'), float('inf'),
    '-inf', 'NaN', '1.234', '1,234', '1.2.3', '1,23,4.50', '1 2', 'S/ ', [], {}, '1e20'])
def test_montos_invalidos_no_se_convierten_en_cero(valor):
    with pytest.raises(MontoInvalido):
        normalizar_monto(valor)


def test_siete_kpi(registros):
    assert contar_solicitudes(registros) == 4
    for estado in ['PENDIENTE FIRMA','PENDIENTE JEFE','APROBADO','RECHAZADO']:
        assert contar_estado(registros, estado) == 1
    assert calcular_monto_total(registros) == 550.75
    assert calcular_monto_promedio(registros) == 137.6875
    assert calcular_monto_total([{'Monto':.1},{'Monto':.2}]) == .3


def test_estado_consistente():
    filas = [{'Estado':' pendiente   jefe '},{'Estado':'PENDIENTE JEFE'}, {'Estado':None}, {'Estado':'EN RENDICIÓN'}]
    assert contar_estado(filas, ' pendiente jefe ') == 2
    assert contar_por_estado(filas) == {'PENDIENTE JEFE':2,'SIN ESTADO':1,'EN RENDICIÓN':1}


def test_agrupaciones_coinciden(registros):
    assert agrupar_por_area(registros) == {'Sistemas':2,'Administración':1,'Logística':1}
    assert agrupar_por_categoria(registros) == {'Movilidad':2,'Materiales':1,'Servicios':1}
    assert calcular_monto_por_categoria(registros) == {'Movilidad':270.75,'Materiales':200,'Servicios':80}
    assert sum(calcular_monto_por_categoria(registros).values()) == calcular_monto_total(registros)


def test_vacios():
    assert contar_solicitudes([]) == 0
    assert contar_estado([], 'APROBADO') == 0
    assert calcular_monto_total([]) == calcular_monto_promedio([]) == 0
    for fn in [contar_por_estado, agrupar_por_area, agrupar_por_categoria, calcular_monto_por_categoria]:
        assert fn([]) == {}
    for fn in [obtener_estado_predominante, obtener_area_mas_solicitudes, obtener_categoria_mas_usada]:
        assert fn([]) == ('-',0)


def test_filas_incompletas_y_sin_mutar():
    originales=[{}, {'Código':'001','Monto':0,'Estado':None}, {'Monto':10}, {'Monto':10}]
    copia=deepcopy(originales)
    filas, avisos = preparar_solicitudes(originales)
    assert originales == copia
    assert len(filas)==3 and filas[0]['Estado']=='SIN ESTADO'
    assert filas[0]['Área']=='SIN ÁREA' and filas[0]['Categoría']=='SIN CATEGORÍA'
    assert len(avisos) >= 2


def test_duplicado_identico_se_cuenta_una_vez(registros):
    filas, avisos=preparar_solicitudes(registros+[dict(registros[0])])
    assert len(filas)==4 and any('una sola vez' in a for a in avisos)


def test_duplicado_conflictivo_no_se_elige(registros):
    with pytest.raises(DatosInvalidos, match='mismo Código'):
        preparar_solicitudes(registros+[dict(registros[0], Monto=999)])


def test_monto_invalido_impide_total_parcial():
    for fn in [calcular_monto_total, calcular_monto_promedio, calcular_monto_por_categoria]:
        with pytest.raises(MontoInvalido):
            fn([{'Monto':5},{'Monto':'incorrecto'}])


def test_total_fuera_de_rango():
    with pytest.raises(MontoInvalido):
        calcular_monto_total([{'Monto':1e308},{'Monto':1e308}])


@pytest.mark.parametrize('fn', [
    preparar_solicitudes, contar_solicitudes, contar_por_estado,
    calcular_monto_total, calcular_monto_promedio, agrupar_por_area,
    agrupar_por_categoria, calcular_monto_por_categoria,
    obtener_estado_predominante, obtener_area_mas_solicitudes,
    obtener_categoria_mas_usada,
])
@pytest.mark.parametrize('entrada', [None, 'texto', {'Monto': 5}, [None], [{'Área': []}]])
def test_estructura_invalida_se_rechaza(fn, entrada):
    with pytest.raises(DatosInvalidos):
        fn(entrada)


def test_contar_estado_rechaza_filas_invalidas():
    with pytest.raises(DatosInvalidos):
        contar_estado([None], 'APROBADO')


def test_campos_ausentes_tienen_reglas_explicitas():
    filas, avisos = preparar_solicitudes([{'Código': 'A', 'Monto': 10}])
    assert filas[0]['Estado'] == 'SIN ESTADO'
    assert filas[0]['Área'] == 'SIN ÁREA'
    assert filas[0]['Categoría'] == 'SIN CATEGORÍA'
    assert calcular_monto_total(filas) == 10
    assert any('otros estados' in aviso for aviso in avisos)
    with pytest.raises(MontoInvalido):
        calcular_monto_total([{'Código': 'B'}])


def test_decimal_snan_es_error_de_monto_controlado():
    with pytest.raises(MontoInvalido):
        normalizar_monto(Decimal('sNaN'))
