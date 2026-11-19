# Validaciones de `analisis.py` y demostración

Las funciones operan sobre datos locales y no escriben en Google Sheets. `DatosInvalidos` indica una colección, fila o campo con estructura incorrecta. `MontoInvalido` indica un importe ausente, ambiguo, no numérico o fuera de rango. Una lista de solicitudes vacía es válida: sus conteos y montos son cero, sus agrupaciones son diccionarios vacíos y sus destacados devuelven `('-', 0)`. Un monto ausente en una solicitud existente **no** es cero: se rechaza.

## Auditoría de funciones públicas

| Función | Vacío y campos ausentes | Tipos y montos incorrectos |
| --- | --- | --- |
| `texto_limpio` | `None` → `""` | Convierte valores escalares a texto; utilidad de normalización. |
| `normalizar_estado` | vacío → `SIN ESTADO` | Reutiliza `texto_limpio`; un estado desconocido permanece distinguible. |
| `normalizar_monto` | vacío → `MontoInvalido` | Rechaza booleanos, formatos ambiguos, no finitos y `Decimal('sNaN')`. |
| `preparar_solicitudes` | omite filas vacías; completa estado/área/categoría; conserva ausencia de código con aviso | Rechaza colección, fila o campo estructuralmente inválido y duplicados contradictorios. No muta la entrada. |
| `contar_solicitudes` | colección vacía → 0 | Valida filas antes de contar. |
| `contar_por_estado` | vacío → `{}`; estado ausente → `SIN ESTADO` | Valida filas. |
| `contar_estado` | vacío → 0; busca estado normalizado | Hereda validación de `contar_por_estado`. |
| `calcular_monto_total` | colección vacía → 0; monto ausente → `MontoInvalido` | Valida filas e importes; rechaza suma no finita. |
| `calcular_monto_promedio` | colección vacía → 0; monto ausente → `MontoInvalido` | Valida filas antes de dividir y reutiliza el total validado. |
| `agrupar_por_area` | vacío → `{}`; área ausente → `SIN ÁREA` | Valida filas mediante `_agrupar`. |
| `agrupar_por_categoria` | vacío → `{}`; categoría ausente → `SIN CATEGORÍA` | Valida filas mediante `_agrupar`. |
| `calcular_monto_por_categoria` | vacío → `{}`; categoría ausente → `SIN CATEGORÍA` | Valida filas y cada monto; no publica subtotales parciales si hay un importe inválido. |
| `obtener_estado_predominante` | vacío → `('-', 0)` | Hereda validación de conteo por estado. |
| `obtener_area_mas_solicitudes` | vacío → `('-', 0)` | Hereda validación de agrupación por área. |
| `obtener_categoria_mas_usada` | vacío → `('-', 0)` | Hereda validación de agrupación por categoría. |

`_validar_registros`, `_agrupar` y `_mayor` son auxiliares internos. El `try/except` de `_validar_registros` traduce una colección no iterable a `DatosInvalidos`; el de `normalizar_monto` traduce fallos de conversión a `MontoInvalido`. Los errores de lógica inesperados no se silencian.

## Funciones para asignar al equipo

Asigne una fila a cada integrante disponible; escriban sus nombres en la última columna. Las parejas agrupan funciones relacionadas y permiten explicar dos funciones por persona. La octava pareja incluye el auxiliar interno `_mayor`, que puede explicarse junto con la función que lo utiliza.

| Pareja | Función 1 | Función 2 | Integrante |
| --- | --- | --- | --- |
| 1 | `texto_limpio` | `normalizar_estado` | Por asignar |
| 2 | `normalizar_monto` | `calcular_monto_total` | Por asignar |
| 3 | `preparar_solicitudes` | `contar_solicitudes` | Por asignar |
| 4 | `contar_por_estado` | `contar_estado` | Por asignar |
| 5 | `calcular_monto_promedio` | `calcular_monto_por_categoria` | Por asignar |
| 6 | `agrupar_por_area` | `obtener_area_mas_solicitudes` | Por asignar |
| 7 | `agrupar_por_categoria` | `obtener_categoria_mas_usada` | Por asignar |
| 8 | `obtener_estado_predominante` | `_mayor` (auxiliar) | Por asignar |

## Demostración en terminal

Desde la raíz del proyecto, con el entorno virtual ya instalado:

**Windows PowerShell**

```powershell
.\.venv\Scripts\python.exe demo_validaciones.py
.\.venv\Scripts\python.exe -m pytest -q
```

**Ubuntu**

```bash
venv/bin/python demo_validaciones.py
venv/bin/python -m pytest -q
```

El primer comando imprime para cada caso la entrada, función, resultado esperado, resultado real o excepción controlada y `OK`/`FALLO`. Termina con código 1 si hay una discrepancia. Solo usa `analisis.py` y datos escritos dentro del archivo: no importa `conexion_sheets.py`, no requiere credenciales y no modifica datos. Muestre un monto ambiguo, un monto ausente y una fila inválida para explicar el uso de `try/except`; compare con un caso válido y con los valores explícitos de estado/área ausentes.
