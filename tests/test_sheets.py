from unittest.mock import Mock
import pytest
import requests
import gspread
from google.auth.exceptions import RefreshError
import conexion_sheets as sheets

CABECERA=['Código','Estado','Monto','Área','Categoría','DNI / CE']


def test_una_conexion_una_consulta_y_preserva_identificadores(monkeypatch):
    cliente=Mock()
    archivo=cliente.open_by_key.return_value
    archivo.values_batch_get.return_value={'valueRanges':[
        {'values':[CABECERA,['001','APROBADO','200.25','Sistemas','Movilidad','00123456']]},
        {'values':[['Código vale','URL archivo'],['001','https://example.org/firma']]},
    ]}
    servicio=Mock(return_value=cliente)
    monkeypatch.setattr(sheets.gspread,'service_account',servicio)
    solicitudes,firmas=sheets.obtener_datos_dashboard()
    servicio.assert_called_once_with(filename=str(sheets.RUTA_CREDENCIALES),scopes=sheets.READONLY_SCOPES)
    cliente.set_timeout.assert_called_once_with((5,15))
    cliente.open_by_key.assert_called_once()
    archivo.values_batch_get.assert_called_once_with(["'SOLICITUDES'","'FIRMAS'"],params={'valueRenderOption':'FORMATTED_VALUE'})
    assert solicitudes[0]['Código']=='001' and solicitudes[0]['DNI / CE']=='00123456'
    assert solicitudes[0]['Monto']=='200.25' and firmas[0]['Código vale']=='001'
    assert all('readonly' in scope for scope in sheets.READONLY_SCOPES)


@pytest.mark.parametrize('fn,hoja',[(sheets.obtener_datos,'SOLICITUDES'),(sheets.obtener_solicitudes,'SOLICITUDES'),(sheets.obtener_firmas,'FIRMAS')])
def test_funciones_compatibles(monkeypatch,fn,hoja):
    leer=Mock(return_value=([{'ejemplo':1}],))
    monkeypatch.setattr(sheets,'_leer_hojas',leer)
    assert fn()==[{'ejemplo':1}]
    leer.assert_called_once_with([hoja])


def test_filas_cortas_y_hojas_vacias():
    assert sheets._registros([], 'SOLICITUDES')==[]
    assert sheets._registros([CABECERA], 'SOLICITUDES')==[]
    fila=sheets._registros([CABECERA,['001']], 'SOLICITUDES')[0]
    assert fila['Monto']=='' and fila['Código']=='001'


@pytest.mark.parametrize('valores',[
    [['Código','Código']], [['Código','Estado']],
    [CABECERA,['001','','','','','','extra']],
    [CABECERA+[''],['001','','','','','','extra']],
])
def test_esquema_invalido(valores):
    with pytest.raises(sheets.ErrorSheets):
        sheets._registros(valores,'SOLICITUDES')


@pytest.mark.parametrize('error,fragmento',[
    (FileNotFoundError('secreto'),'credenciales'),
    (ValueError('secreto'),'autenticar'),
    (RefreshError('secreto'),'autenticar'),
    (PermissionError('secreto'),'lector'),
    (requests.Timeout('secreto'),'tiempo permitido'),
    (requests.ConnectionError('secreto'),'conectar'),
    (gspread.exceptions.SpreadsheetNotFound('secreto'),'identificador'),
])
def test_errores_comprensibles_sin_detalles(monkeypatch,error,fragmento):
    monkeypatch.setattr(sheets.gspread,'service_account',Mock(side_effect=error))
    with pytest.raises(sheets.ErrorSheets) as exc:
        sheets.obtener_datos_dashboard()
    assert fragmento in str(exc.value) and 'secreto' not in str(exc.value)


@pytest.mark.parametrize('status,fragmento',[(400,'nombres'),(401,'acceso'),(403,'permisos'),(429,'límite'),(500,'disponible')])
def test_api_error(monkeypatch,status,fragmento):
    response=Mock(status_code=status)
    response.json.return_value={'error':{'code':status,'message':'secreto','status':'ERROR'}}
    archivo=Mock()
    archivo.values_batch_get.side_effect=gspread.exceptions.APIError(response)
    monkeypatch.setattr(sheets,'conectar_archivo',lambda:archivo)
    with pytest.raises(sheets.ErrorSheets) as exc:
        sheets.obtener_datos_dashboard()
    assert fragmento in str(exc.value) and 'secreto' not in str(exc.value)


def test_respuesta_incompleta(monkeypatch):
    archivo=Mock()
    archivo.values_batch_get.return_value={'valueRanges':[]}
    monkeypatch.setattr(sheets,'conectar_archivo',lambda:archivo)
    with pytest.raises(sheets.ErrorSheets,match='incompleta'):
        sheets.obtener_datos_dashboard()
