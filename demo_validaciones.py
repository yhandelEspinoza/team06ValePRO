"""Demostración autónoma de validaciones; no importa Flask ni consulta Google Sheets."""
from decimal import Decimal

from analisis import (
    DatosInvalidos, MontoInvalido, agrupar_por_area, calcular_monto_total,
    contar_estado, normalizar_monto, preparar_solicitudes,
)


CASOS = [
    ("Monto válido", normalizar_monto, ("S/ 1.200,50",), 1200.5),
    ("Monto ambiguo", normalizar_monto, ("1,234",), MontoInvalido),
    ("Monto Decimal no finito", normalizar_monto, (Decimal("sNaN"),), MontoInvalido),
    ("Suma válida", calcular_monto_total, ([{"Monto": 10}, {"Monto": "20,50"}],), 30.5),
    ("Monto ausente", calcular_monto_total, ([{"Código": "A"}],), MontoInvalido),
    ("Colección incorrecta", calcular_monto_total, (None,), DatosInvalidos),
    ("Fila incorrecta", preparar_solicitudes, ([{"Código": "A"}, None],), DatosInvalidos),
    ("Estado ausente", contar_estado, ([{}], "SIN ESTADO"), 1),
    ("Área ausente", agrupar_por_area, ([{}],), {"SIN ÁREA": 1}),
]


def main():
    fallos = 0
    for titulo, funcion, argumentos, esperado in CASOS:
        print(f"\n{titulo}")
        print(f"  Entrada: {argumentos!r}")
        print(f"  Función: {funcion.__name__}")
        print(f"  Esperado: {esperado.__name__ if isinstance(esperado, type) else esperado!r}")
        try:
            resultado = funcion(*argumentos)
        except DatosInvalidos as error:
            correcto = isinstance(esperado, type) and type(error) is esperado
            print(f"  Error controlado: {type(error).__name__}: {error}")
        else:
            correcto = not isinstance(esperado, type) and resultado == esperado
            print(f"  Resultado: {resultado!r}")
        print(f"  Verificación: {'OK' if correcto else 'FALLO'}")
        fallos += not correcto
    print(f"\n{len(CASOS) - fallos}/{len(CASOS)} casos correctos. Datos locales; ninguna consulta a Sheets.")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
