# Reglas de datos

- SOLICITUDES y FIRMAS se leen juntas, sin escrituras; códigos y documentos permanecen como texto.
- Se omiten filas completamente vacías. Filas incompletas permanecen con aviso.
- Códigos repetidos con datos idénticos se cuentan una vez; si sus datos difieren, el dashboard informa error 503.
- Solicitudes sin Código se cuentan sin asociar firmas. Última firma por Código vale prevalece, como en el ZIP original.
- Estados se normalizan a mayúsculas y espacios simples. Los desconocidos entran en el total y el gráfico de estados, sin alterar los cuatro KPI de estados conocidos.
- Se aceptan montos numéricos y formatos 1234.50, 1234,50, 1.234,50, 1,234.50. 1.234 es ambiguo y se rechaza. Blanco o erróneo desactiva los dos KPI monetarios y el gráfico de montos, sin mostrar ceros ficticios. El promedio usa todas las solicitudes si todos los montos son válidos.
- Error de Sheets devuelve 503 sin KPI. La demo usa datos ficticios solo con VALPRO_DEMO=1.
