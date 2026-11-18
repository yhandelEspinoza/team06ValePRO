"""Datos de exposición inequívocamente ficticios. Nunca sustituyen un fallo real."""
from copy import deepcopy

_SOLICITUDES = [
    {"Código": "DEMO-001", "Solicitante": "Persona de ejemplo A", "Estado": "PENDIENTE FIRMA", "Monto": "S/ 120,50", "Área": "Sistemas", "Categoría": "Movilidad", "Uso previsto": "Ejemplo ficticio de transporte", "Registro": "2026-01-10"},
    {"Código": "DEMO-002", "Solicitante": "Persona de ejemplo B", "Estado": "PENDIENTE JEFE", "Monto": 200, "Área": "Administración", "Categoría": "Materiales", "Uso previsto": "Ejemplo ficticio de materiales", "Registro": "2026-01-11"},
    {"Código": "DEMO-003", "Solicitante": "Persona de ejemplo C", "Estado": "APROBADO", "Monto": "150.25", "Área": "Sistemas", "Categoría": "Movilidad", "Uso previsto": "Ejemplo ficticio de traslado", "Registro": "2026-01-12"},
    {"Código": "DEMO-004", "Solicitante": "Persona de ejemplo D", "Estado": "RECHAZADO", "Monto": 80, "Área": "Logística", "Categoría": "Servicios", "Uso previsto": "Ejemplo ficticio de servicio", "Registro": "2026-01-13"},
]
_FIRMAS = [{"Código vale": "DEMO-003", "ID Firma": "FICTICIA-01", "URL archivo": "", "Tipo": "Demostración", "Estado": "FICTICIO"}]


def obtener_datos_demo():
    return deepcopy(_SOLICITUDES), deepcopy(_FIRMAS)
