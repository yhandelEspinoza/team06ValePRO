import importlib
from copy import deepcopy
from flask import template_rendered
import pytest
import app as modulo
from conexion_sheets import ErrorSheets


def test_importaciones():
    for nombre in ['app','analisis','conexion_sheets','graficos','demo']:
        assert importlib.import_module(nombre)
    assert not modulo.app.debug


def capturar(web):
    contexto={}
    def recibe(sender,template,context,**extra):
        contexto.update(context)
    with template_rendered.connected_to(recibe,modulo.app):
        respuesta=web.get('/')
    return respuesta,contexto


def test_dashboard_y_cuatro_series(web):
    response, ctx=capturar(web)
    assert response.status_code==200 and ctx['conexion_correcta']
    assert ctx['indicadores']['total_solicitudes']==4
    assert len(ctx['indicadores'])==7 and ctx['indicadores']['monto_total']==550.75
    for tipo in ['estados','areas','categorias']:
        assert sum(ctx[tipo+'_valores'])==4
        assert len(ctx[tipo+'_labels'])==len(ctx[tipo+'_valores'])
    assert sum(ctx['montos_categoria_valores'])==550.75
    assert response.text.count('class="grafico-plotly"')==4
    assert all(ctx['figuras'][clave]['data'] for clave in ('estados','areas','categorias','montos'))
    for clave in ('estados', 'areas', 'categorias'):
        traza = ctx['figuras'][clave]['data'][0]
        assert sum(traza['values'] if traza['type'] == 'pie' else traza['y']) == 4
    assert sum(ctx['figuras']['montos']['data'][0]['y']) == 550.75
    assert 'id="plotly-data"' in response.text
    assert 'Cache-Control' in response.headers and response.headers['Cache-Control']=='no-store'


def test_fallo_sheets_no_muestra_ceros(web,monkeypatch):
    def fallo():
        raise ErrorSheets('No se puede conectar con Google Sheets.')
    monkeypatch.setattr(modulo,'obtener_datos_dashboard',fallo)
    response,ctx=capturar(web)
    assert response.status_code==503 and not ctx['conexion_correcta']
    assert 'No se puede conectar' in response.text
    assert 'class="contenido-kpi"' not in response.text and 'id="plotly-data"' not in response.text


def test_fallo_interno_no_expone_detalles(web,monkeypatch):
    def fallo():
        raise RuntimeError('SECRETO_DE_PRUEBA_NO_PUBLICAR')
    monkeypatch.setattr(modulo,'obtener_datos_dashboard',fallo)
    response=web.get('/')
    assert response.status_code==500
    assert 'SECRETO_DE_PRUEBA' not in response.text


def test_monto_invalido_conserva_conteos(web,monkeypatch,registros):
    registros[0]['Monto']='erróneo'
    response,ctx=capturar(web)
    assert response.status_code==200 and ctx['indicadores']['total_solicitudes']==4
    assert ctx['indicadores']['monto_total'] is None
    assert ctx['indicadores']['monto_promedio'] is None
    assert ctx['montos_categoria_valores']==[] and not ctx['montos_disponibles']
    assert ctx['figuras']['montos'] is None
    assert 'No disponible' in response.text


def test_vacio_es_exito_no_error(web,monkeypatch):
    monkeypatch.setattr(modulo,'obtener_datos_dashboard',lambda:([],[]))
    response,ctx=capturar(web)
    assert response.status_code==200 and ctx['conexion_correcta']
    assert ctx['indicadores']['total_solicitudes']==0
    assert ctx['indicadores']['monto_total']==0 and ctx['registros']==[]


def test_duplicados_conflictivos_503(web,registros):
    registros.append(dict(registros[0],Monto=888))
    response=web.get('/')
    assert response.status_code==503 and 'mismo Código' in response.text
    assert 'class="contenido-kpi"' not in response.text


def test_demo_nunca_consulta_sheets(web,monkeypatch):
    modulo.app.config['VALPRO_DEMO']=True
    def prohibido():
        pytest.fail('La demo no debe consultar Google')
    monkeypatch.setattr(modulo,'obtener_datos_dashboard',prohibido)
    response=web.get('/')
    assert response.status_code==200 and 'DATOS FICTICIOS' in response.text


def test_firmas_no_mutan_y_ultima_fila():
    solicitudes=[{'Código':'001'},{'Código':'002'},{'Código':''}]
    firmas=[{'Código vale':'001','URL archivo':'https://example.org/a'},
            {'Código vale':'001','URL archivo':'https://example.org/b','ID Firma':'final'},
            {'Código vale':'','URL archivo':'https://example.org/c'}]
    original=deepcopy((solicitudes,firmas))
    resultado=modulo.enriquecer_solicitudes_con_firmas(solicitudes,firmas)
    assert (solicitudes,firmas)==original
    assert len(resultado)==3 and resultado[0]['firma_id']=='final'
    assert resultado[0]['firma_url']=='https://example.org/b'
    assert not resultado[1]['firma_disponible'] and not resultado[2]['firma_disponible']


@pytest.mark.parametrize('url',['javascript:alert(1)','data:text/html,hi','http://example.org','//example.org','https://user:pass@example.org','https://[malformed'])
def test_enlaces_no_seguros(url):
    assert modulo.url_firma_segura(url)==''


def test_escapado_html(web,registros):
    registros[0]['Solicitante']='<script>alert(1)</script>'
    response=web.get('/')
    assert '<script>alert(1)</script>' not in response.text
    assert '&lt;script&gt;' in response.text


@pytest.mark.parametrize('recurso',['css/estilo.css','js/dashboard.js','favicon.svg','vendor/plotly.min.js','vendor/bootstrap-icons/bootstrap-icons.min.css','vendor/bootstrap-icons/fonts/bootstrap-icons.woff2'])
def test_estaticos(web,recurso):
    assert web.get('/static/'+recurso).status_code==200
