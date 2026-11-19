"""Análisis VALPRO, Equipo 06. Funciones puras; políticas en docs/DATOS.md."""
from collections import Counter
from collections.abc import Mapping
from decimal import Decimal
import math
import re


class DatosInvalidos(ValueError):
    """Datos insuficientes o contradictorios para un resultado fiable."""


class MontoInvalido(DatosInvalidos):
    pass


def _validar_registros(registros):
    """Materializa filas y rechaza estructuras que no representan solicitudes."""
    if isinstance(registros, (str, bytes, Mapping)):
        raise DatosInvalidos("Las solicitudes deben ser una colección de registros.")
    try:
        filas = list(registros)
    except TypeError as exc:
        raise DatosInvalidos("Las solicitudes deben ser una colección de registros.") from exc
    for fila in filas:
        if not isinstance(fila, dict):
            raise DatosInvalidos("Se recibió una fila que no es un registro válido.")
        if any(not isinstance(clave, str) or isinstance(valor, (list, tuple, set, Mapping))
               for clave, valor in fila.items()):
            raise DatosInvalidos("Se recibió un campo con tipo de dato no válido.")
    return filas


def texto_limpio(valor):
    return "" if valor is None else str(valor).strip()


def normalizar_estado(valor):
    return " ".join(texto_limpio(valor).upper().split()) or "SIN ESTADO"


def normalizar_monto(valor):
    """Acepta números finitos, 1234.50, 1234,50, 1.234,50 y 1,234.50.

    Un separador único seguido por tres dígitos es ambiguo. Los importes
    desconocidos se rechazan explícitamente, nunca se convierten en cero.
    """
    if isinstance(valor, bool) or valor is None:
        raise MontoInvalido("Monto vacío o no numérico.")
    try:
        if isinstance(valor, (int, float, Decimal)):
            numero = float(valor)
        else:
            texto = re.sub(r"^S/\.?\s*", "", texto_limpio(valor), flags=re.I)
            texto = texto.replace("\u00a0", " ").strip()
            signo = ""
            if texto[:1] in ("+", "-"):
                signo, texto = texto[0], texto[1:]
            if not texto or not re.fullmatch(r"[0-9.,]+", texto):
                raise MontoInvalido("Monto vacío o con formato no reconocido.")
            if "." in texto and "," in texto:
                decimal = "." if texto.rfind(".") > texto.rfind(",") else ","
                miles = "," if decimal == "." else "."
                patron = rf"\d{{1,3}}(?:{re.escape(miles)}\d{{3}})+{re.escape(decimal)}\d{{1,2}}"
                if not re.fullmatch(patron, texto):
                    raise MontoInvalido("Separadores de monto inconsistentes.")
                texto = texto.replace(miles, "").replace(decimal, ".")
            elif "." in texto or "," in texto:
                separador = "." if "." in texto else ","
                if texto.count(separador) > 1:
                    if not re.fullmatch(rf"\d{{1,3}}(?:{re.escape(separador)}\d{{3}})+", texto):
                        raise MontoInvalido("Separadores de monto inconsistentes.")
                    texto = texto.replace(separador, "")
                else:
                    if not re.fullmatch(rf"\d+{re.escape(separador)}\d{{1,2}}", texto):
                        raise MontoInvalido("Monto ambiguo: use dos decimales o un número sin separador de miles.")
                    texto = texto.replace(separador, ".")
            numero = float(Decimal(signo + texto))
    except MontoInvalido:
        raise
    except (OverflowError, ValueError, TypeError) as exc:
        raise MontoInvalido("Monto no numérico o fuera de rango.") from exc
    if not math.isfinite(numero):
        raise MontoInvalido("El monto debe ser finito.")
    return numero


def preparar_solicitudes(registros):
    """Copia filas, omite vacías y repetidas idénticas; rechaza conflictos."""
    resultado, por_codigo, avisos = [], {}, []
    vacias = duplicadas = sin_codigo = 0
    for original in _validar_registros(registros):
        if not any(texto_limpio(v) for v in original.values()):
            vacias += 1
            continue
        registro = {k: "" if v is None else v.strip() if isinstance(v, str) else v
                    for k, v in original.items()}
        registro["Código"] = texto_limpio(registro.get("Código"))
        registro["Estado"] = normalizar_estado(registro.get("Estado"))
        registro["Área"] = texto_limpio(registro.get("Área")) or "SIN ÁREA"
        registro["Categoría"] = texto_limpio(registro.get("Categoría")) or "SIN CATEGORÍA"
        codigo = registro["Código"]
        if codigo and codigo in por_codigo:
            if registro != por_codigo[codigo]:
                raise DatosInvalidos("Hay solicitudes con el mismo Código y datos diferentes. Revise los duplicados en SOLICITUDES.")
            duplicadas += 1
            continue
        if codigo:
            por_codigo[codigo] = registro
        else:
            sin_codigo += 1
        resultado.append(registro)
    if vacias:
        avisos.append(f"Se omitieron {vacias} filas completamente vacías.")
    if duplicadas:
        avisos.append(f"Se contaron una sola vez {duplicadas} filas idénticas con el mismo Código.")
    if sin_codigo:
        avisos.append(f"Hay {sin_codigo} solicitudes sin Código; se conservan sin deduplicar ni asociar firmas.")
    otros = sum(r["Estado"] not in {"PENDIENTE FIRMA", "PENDIENTE JEFE", "APROBADO", "RECHAZADO"} for r in resultado)
    if otros:
        avisos.append(f"Hay {otros} solicitudes con otros estados; aparecen en el total y en el gráfico de estados.")
    return resultado, avisos


def contar_solicitudes(registros):
    return len(_validar_registros(registros))


def contar_por_estado(registros):
    return dict(Counter(normalizar_estado(r.get("Estado")) for r in _validar_registros(registros)))


def contar_estado(registros, estado_buscado):
    return contar_por_estado(registros).get(normalizar_estado(estado_buscado), 0)


def calcular_monto_total(registros):
    total = sum((Decimal(str(normalizar_monto(r.get("Monto")))) for r in _validar_registros(registros)), Decimal(0))
    resultado = float(total)
    if not math.isfinite(resultado):
        raise MontoInvalido("El total de montos excede el rango admitido.")
    return resultado


def calcular_monto_promedio(registros):
    filas = _validar_registros(registros)
    return calcular_monto_total(filas) / len(filas) if filas else 0.0


def _agrupar(registros, campo, vacio):
    return dict(Counter(texto_limpio(r.get(campo)) or vacio for r in _validar_registros(registros)))


def agrupar_por_area(registros):
    return _agrupar(registros, "Área", "SIN ÁREA")


def agrupar_por_categoria(registros):
    return _agrupar(registros, "Categoría", "SIN CATEGORÍA")


def calcular_monto_por_categoria(registros):
    grupos = {}
    for r in _validar_registros(registros):
        categoria = texto_limpio(r.get("Categoría")) or "SIN CATEGORÍA"
        grupos.setdefault(categoria, []).append(r)
    return {categoria: calcular_monto_total(filas) for categoria, filas in grupos.items()}


def _mayor(resumen):
    if not resumen:
        return "-", 0
    clave = max(resumen, key=resumen.get)
    return clave, resumen[clave]


def obtener_estado_predominante(registros):
    return _mayor(contar_por_estado(registros))


def obtener_area_mas_solicitudes(registros):
    return _mayor(agrupar_por_area(registros))


def obtener_categoria_mas_usada(registros):
    return _mayor(agrupar_por_categoria(registros))
