# Actividad 03 - Métricas de Salario Mínimo e IPC

Repositorio: <https://github.com/cardo88/UCU-BigData-2026.git>

## Objetivo

Conectar el Salario Mínimo Nacional (SMN) de Uruguay con el Índice de
Precios al Consumo (IPC) para analizar la evolución nominal del salario y
una aproximación de su **crecimiento real** año a
año, algo que la Actividad02 dejó pendiente al trabajar el SMN de forma
aislada, en pesos corrientes sin ajustar.

## Acciones mínimas de análisis

**Proceso de carga**: Python 3, `pandas`, `pyarrow`, `openpyxl` y
`matplotlib`, sobre el venv del repo. Se combinan dos fuentes:

- **Salario mínimo**: no se vuelve a leer el XML original — se reutiliza
  `Actividad02/salario_minimo_clean.parquet` (ya limpio y tipado por la
  Actividad02), evitando repetir esa lectura/limpieza.
- **IPC**: archivo oficial del INE, *Series históricas IPC — base octubre
  2022* (`IPC gral y variaciones_base 2022.xlsx`), IPC general del Total
  País con serie histórica desde julio de 1937. Es mensual; se resume a un
  valor por año tomando el último mes disponible de cada año (diciembre en
  los años completos).

```bash
source .venv/bin/activate
python -m pip install pandas pyarrow openpyxl matplotlib
python Actividad03/actividad03.py
```

El script (`actividad03.py`) lee ambas fuentes, genera `ipc_anual.parquet`
(IPC resumido a una fila por año), conecta ambos datasets por año, calcula
las métricas, guarda el resultado en `salario_ipc_metricas.parquet` y genera
el gráfico `analisis_salario_ipc.png`.

**Punto clave de calidad de datos — alineación de períodos antes de unir**:
el salario mínimo rige desde el 1° de enero de cada año, así que su
variación interanual cubre aproximadamente el año calendario *anterior*
completo. Compararla directamente contra el IPC de diciembre del mismo año
compararía el ajuste de salario de enero contra una inflación que en su
mayoría todavía no había ocurrido. Por eso, antes de unir las tablas, el año
del IPC se corre un año hacia adelante (columna `año_ipc_base`), de forma
que cada salario se compare contra la inflación del período que realmente
lo precedió. `ipc_anual.parquet` se guarda sin este corrimiento, para poder
inspeccionarlo o reutilizarlo de forma directa; el corrimiento se aplica
solo al armar la tabla conectada.

**Métrica principal**:

```text
crecimiento real aproximado =
((1 + variación del salario) / (1 + variación del IPC) - 1) * 100
```

Positivo: el salario le ganó a los precios. Negativo: los precios le
ganaron al salario.

## Resultados

Se calculan mínimo, máximo y promedio histórico del salario mínimo, la
variación anual del salario y del IPC, y el crecimiento real aproximado por
año. La tabla completa conectada (28 filas x 9 columnas) queda en
`salario_ipc_metricas.parquet` — no se imprime entera en consola por ser
poco legible en una terminal; la consola muestra solo un resumen de
negocio: cuántos años el salario le ganó o le perdió al IPC, el crecimiento
real promedio, y el mejor y el peor año del período.

El gráfico (adjunto en esta entrega como `analisis_salario_ipc.png`) tiene
dos paneles: arriba compara la variación anual del salario mínimo contra la
del IPC; abajo muestra el crecimiento real aproximado, con barras verdes
para los años en que el salario creció por encima de la inflación y rojas
para los años en que perdió poder adquisitivo frente a ella.

## Limitaciones

Es una aproximación a nivel anual, no exacta a nivel de fecha: no usa la
fecha exacta de cada ajuste salarial (que en la práctica podría no ser
siempre el 1° de enero) ni el IPC del mes exacto correspondiente. Además,
la base "octubre 2022 = 100" del IPC es solo una escala de referencia — no
implica que los precios fueran 100 pesos —, y no afecta a las variaciones
porcentuales usadas en el análisis.

## Uso de IA como apoyo

Se utilizó asistencia de IA (Claude, Anthropic) para mejorar la redacción
de este documento y como apoyo en la sintaxis del código. El criterio de
resolución, la decisión de alinear los períodos antes de conectar los
datasets, y la interpretación de los resultados son propios.

---

## Anexo

### A. Archivos adjuntos

Junto a este documento se adjunta, en el zip de entrega:

- `analisis_salario_ipc.png`: gráfico referenciado en la sección de
  Resultados.

### B. Código completo del script

El script no se adjunta en esta entrega — está disponible en el
repositorio del curso:

- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad03/actividad03.py>

### C. Fuente del IPC

Instituto Nacional de Estadística (INE) — Series históricas IPC, base
octubre 2022:
<https://www.gub.uy/instituto-nacional-estadistica/datos-y-estadisticas/estadisticas/series-historicas-ipc-base-octubre-2022100>
