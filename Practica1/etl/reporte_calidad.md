# Reporte de Calidad de Datos - Venta_online_c.csv

| Validación | Resultado | Estado |
|---|---|---|
| Total de filas leidas | 6500 | ✅ OK |
| Valores nulos (total en todas las columnas) | 0 | ✅ OK |
| Filas duplicadas (exactas) | 0 | ✅ OK |
| Id_cliente duplicados | 0 | ✅ OK |
| Genero fuera de dominio {0,1} | 0 | ✅ OK |
| MetodoPago fuera de dominio {0,1,2} | 0 | ✅ OK |
| Navegador fuera de dominio {0..4} | 0 | ✅ OK |
| Boletin fuera de dominio {0,1} | 0 | ✅ OK |
| Vale fuera de dominio {0,1} | 0 | ✅ OK |
| Fechas invalidas / no parseables (formato DD.MM.YY) | 0 | ✅ OK |
| Fechas fuera del anio 2021 | 0 | ✅ OK |
| Edad fuera de rango [0,120] | 0 | ✅ OK |
| Venta_total <= 0 | 0 | ✅ OK |
| MontoCompra <= 0 | 0 | ✅ OK |
| Tiempo <= 0 | 0 | ✅ OK |
| N_Compras = 0 pero Venta_total > 0 (inconsistencia) | 0 | ✅ OK |
| MontoCompra > Venta_total (inconsistencia) | 0 | ✅ OK |
