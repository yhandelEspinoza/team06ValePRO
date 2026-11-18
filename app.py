"""Dashboard VALPRO: lectura, análisis y presentación; sin escrituras a Sheets."""
import os
from datetime import datetime
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from flask import Flask, render_template
from conexion_sheets import ErrorSheets, obtener_datos_dashboard
from analisis import (
    DatosInvalidos, MontoInvalido, texto_limpio, preparar_solicitudes,
    contar_solicitudes, contar_estado, calcular_monto_total,
    calcular_monto_promedio, contar_por_estado, agrupar_por_area,
    agrupar_por_categoria, calcular_monto_por_categoria,
    obtener_estado_predominante, obtener_area_mas_solicitudes,
    obtener_categoria_mas_usada,
)

app = Flask(__name__)
app.config["VALPRO_DEMO"] = os.environ.get("VALPRO_DEMO", "0") == "1"


def url_firma_segura(valor):
    url = texto_limpio(valor)
    try:
        partes = urlsplit(url)
        if partes.scheme == "https" and partes.hostname and not partes.username and not partes.password:
            return url
    except ValueError:
        pass
    return ""


def indexar_firmas(firmas):
    """Conserva la regla previa: última fila por Código vale, no por fecha."""
    indice = {}
    for firma in firmas:
        codigo = texto_limpio(firma.get("Código vale"))
        if codigo:
            indice[codigo] = firma
    return indice


def enriquecer_solicitudes_con_firmas(solicitudes, firmas):
    indice = indexar_firmas(firmas)
    resultado = []
    for solicitud in solicitudes:
        registro = dict(solicitud)
        firma = indice.get(texto_limpio(solicitud.get("Código")), {})
        url = url_firma_segura(firma.get("URL archivo"))
        registro.update(
            firma_disponible=bool(url), firma_url=url,
            firma_tipo=texto_limpio(firma.get("Tipo")),
            firma_estado=texto_limpio(firma.get("Estado")) if firma else "PENDIENTE",
            firma_registro=texto_limpio(firma.get("Registro")),
            firma_id=texto_limpio(firma.get("ID Firma")),
        )
        resultado.append(registro)
    return resultado


@app.after_request
def cabeceras_privacidad(respuesta):
    respuesta.headers["Cache-Control"] = "no-store"
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "SAMEORIGIN"
    respuesta.headers["Referrer-Policy"] = "same-origin"
    return respuesta


@app.route("/")
def dashboard():
    contexto = dict(
        error=None, conexion_correcta=False, modo_demo=app.config["VALPRO_DEMO"],
        avisos=[], registros=[], indicadores={}, destacados={},
        estados_labels=[], estados_valores=[], areas_labels=[], areas_valores=[],
        categorias_labels=[], categorias_valores=[],
        montos_categoria_labels=[], montos_categoria_valores=[],
        montos_disponibles=False,
        ultima_actualizacion=datetime.now(ZoneInfo("America/Lima")).strftime("%d/%m/%Y %H:%M:%S (Lima)"),
    )
    status = 200
    try:
        if app.config["VALPRO_DEMO"]:
            from demo import obtener_datos_demo
            solicitudes, firmas = obtener_datos_demo()
        else:
            solicitudes, firmas = obtener_datos_dashboard()
        solicitudes, avisos = preparar_solicitudes(solicitudes)
        indicadores = {
            "total_solicitudes": contar_solicitudes(solicitudes),
            "pendiente_firma": contar_estado(solicitudes, "PENDIENTE FIRMA"),
            "pendiente_jefe": contar_estado(solicitudes, "PENDIENTE JEFE"),
            "aprobadas": contar_estado(solicitudes, "APROBADO"),
            "rechazadas": contar_estado(solicitudes, "RECHAZADO"),
            "monto_total": None, "monto_promedio": None,
        }
        montos = {}
        try:
            total = calcular_monto_total(solicitudes)
            promedio = calcular_monto_promedio(solicitudes)
            montos = calcular_monto_por_categoria(solicitudes)
            indicadores.update(monto_total=total, monto_promedio=promedio)
            contexto["montos_disponibles"] = True
        except MontoInvalido:
            avisos.append("Hay montos vacíos, incorrectos o ambiguos. El total, promedio y gráfico de montos no están disponibles hasta revisar esos datos; los conteos sí se muestran.")
        codigos_firma = [texto_limpio(f.get("Código vale")) for f in firmas if texto_limpio(f.get("Código vale"))]
        if len(codigos_firma) != len(set(codigos_firma)):
            avisos.append("Hay varias firmas para un mismo vale: se muestra la última fila de FIRMAS, conforme a la regla existente.")
        if any(texto_limpio(f.get("URL archivo")) and not url_firma_segura(f.get("URL archivo")) for f in firmas):
            avisos.append("Hay enlaces de firma inválidos o sin HTTPS; no se habilitó su apertura.")
        destacados = {}
        for funcion, clave, cantidad in [
            (obtener_estado_predominante, "estado_predominante", "cantidad_estado"),
            (obtener_area_mas_solicitudes, "area_principal", "cantidad_area"),
            (obtener_categoria_mas_usada, "categoria_principal", "cantidad_categoria"),
        ]:
            destacados[clave], destacados[cantidad] = funcion(solicitudes)
        for prefijo, datos in [
            ("estados", contar_por_estado(solicitudes)),
            ("areas", agrupar_por_area(solicitudes)),
            ("categorias", agrupar_por_categoria(solicitudes)),
            ("montos_categoria", montos),
        ]:
            contexto[prefijo + "_labels"] = list(datos)
            contexto[prefijo + "_valores"] = list(datos.values())
        contexto.update(conexion_correcta=True, avisos=avisos, indicadores=indicadores,
                        destacados=destacados,
                        registros=enriquecer_solicitudes_con_firmas(solicitudes, firmas))
    except (ErrorSheets, DatosInvalidos) as exc:
        contexto["error"] = str(exc)
        status = 503
        app.logger.warning("Dashboard no disponible: %s", type(exc).__name__)
    except Exception as exc:
        # No publicar respuestas de API, rutas, datos administrativos ni secretos.
        app.logger.error("Fallo interno del dashboard: %s", type(exc).__name__)
        contexto["error"] = "No se pudo preparar el dashboard. Contacte al responsable de VALPRO."
        status = 500
    return render_template("dashboard.html", **contexto), status


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("VALPRO_PORT", "5000")), debug=False)
