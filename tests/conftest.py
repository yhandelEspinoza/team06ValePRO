import pytest
from demo import obtener_datos_demo


@pytest.fixture
def registros():
    return obtener_datos_demo()[0]


@pytest.fixture
def web(monkeypatch, registros):
    import app as modulo
    modulo.app.config.update(TESTING=True, VALPRO_DEMO=False)
    monkeypatch.setattr(modulo, 'obtener_datos_dashboard', lambda: (registros, []))
    return modulo.app.test_client()
