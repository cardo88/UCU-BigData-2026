# Actividad 03 - Métricas de salario mínimo e IPC

## Objetivo

Esta actividad conecta el Salario Mínimo Nacional (SMN) de Uruguay con el
Índice de Precios al Consumo (IPC) para analizar la evolución nominal y una
aproximación del crecimiento real del salario.

Se calculan:

- mínimo histórico del salario mínimo;
- máximo histórico del salario mínimo;
- promedio del salario mínimo;
- variación anual del salario mínimo;
- variación anual del IPC;
- crecimiento real aproximado del salario mínimo descontando el IPC.

El IPC se resume por año usando el último mes disponible de cada año. En los
años completos ese registro corresponde a diciembre; no se usan los valores de
enero por defecto.

## Fuentes

### Salario mínimo nacional

La fuente original es el indicador 10454 de Datos Abiertos de Uruguay. El
archivo descargado es un XML, pero no se vuelve a leer directamente en esta
actividad.

Actividad 2 realiza la ingesta y limpieza, y genera:

```text
Actividad02/salario_minimo_clean.parquet
```

Ese Parquet contiene las columnas `año` y `valor`, ya convertidas a tipos
numéricos y ordenadas. Reutilizarlo evita repetir en Actividad 3 la lectura y
limpieza del XML.

### IPC

Se utiliza el archivo oficial del Instituto Nacional de Estadística:

[Series históricas IPC - base octubre 2022](https://www.gub.uy/instituto-nacional-estadistica/datos-y-estadisticas/estadisticas/series-historicas-ipc-base-octubre-2022100)

Archivo utilizado:

```text
Actividad03/IPC gral y variaciones_base 2022.xlsx
```

El Excel corresponde al IPC general del Total País, con base octubre 2022 =
100 y serie histórica desde julio de 1937. La fila 7 contiene los encabezados
reales; las filas anteriores son la portada y títulos del documento.

## Orden de ejecución

Los comandos se ejecutan desde la raíz del repositorio, con el entorno virtual
activado:

```bash
source .venv/bin/activate
```

Si todavía no se generó el Parquet limpio del salario, ejecutar primero la
Actividad 2:

```bash
python Actividad02/01_ingesta.py
python Actividad02/03_limpieza.py
```

Para la Actividad 3 se necesitan `pandas`, `pyarrow` y `openpyxl`:

```bash
python -m pip install pandas pyarrow openpyxl matplotlib
python Actividad03/actividad03.py
```

El script también muestra un mensaje claro si no encuentra el Parquet limpio.
Al ejecutarse genera el archivo intermedio:

```text
Actividad03/ipc_anual.parquet
```

Ese archivo contiene una fila por año y es el que se conecta con
`salario_minimo_clean.parquet`.

El script también genera:

```text
Actividad03/salario_ipc_metricas.parquet
Actividad03/analisis_salario_ipc.png
```

`salario_ipc_metricas.parquet` es la tabla completa ya conectada (salario,
IPC, variaciones y crecimiento real por año) — es el resultado final para
consultar o reutilizar después, y por eso **no** se imprime entera en
consola (28 filas x 9 columnas no se leen cómodo en una terminal). La
consola solo muestra un resumen de negocio: cuántos años el salario le ganó
o le perdió al IPC, el crecimiento real promedio, y el mejor/peor año.

`analisis_salario_ipc.png` tiene dos paneles: arriba compara las
variaciones anuales del salario mínimo y del IPC; abajo muestra el
crecimiento real aproximado del salario. Las barras verdes indican
crecimiento por encima del IPC y las rojas indican pérdida aproximada de
poder adquisitivo.

## Cómo se conectan los datos

El XML del salario tiene un valor anual. El IPC tiene observaciones mensuales.
Para obtener una observación anual, el script ordena los registros por fecha y
conserva el último mes disponible de cada año, normalmente diciembre. Esto
permite inspeccionar y reutilizar la transformación sin volver a leer el Excel.

### Alineación de los períodos antes de unir

El salario mínimo rige desde el **1° de enero** de cada año (ver README de
Actividad 2). Su variación interanual —`salario[N] / salario[N-1] - 1`— cubre
entonces el período entre el 1° de enero de `N-1` y el 1° de enero de `N`, es
decir, aproximadamente el **año calendario `N-1` completo**.

Si esa variación se comparara contra el IPC de diciembre del año `N` (como se
hacía en una primera versión de este script), se estaría comparando el ajuste
de salario de enero contra una inflación que en su mayor parte todavía no
había ocurrido cuando se fijó ese salario. Por eso, antes de unir, el año del
IPC se corre un año hacia adelante: la fila que en `ipc_anual.parquet` dice
"año 1990" (variación de precios de diciembre de 1989 a diciembre de 1990) se
une con el salario del "año 1991" (variación de salario de enero de 1990 a
enero de 1991), que cubre aproximadamente el mismo período.

`ipc_anual.parquet` se guarda **sin** este corrimiento (con el año real de
cada observación), para que se pueda inspeccionar o reutilizar de forma
directa. El corrimiento se aplica únicamente al armar la tabla unida
(`datos`), donde la columna `año_ipc_base` deja explícito qué año de IPC
quedó asociado a cada fila.

La métrica principal es:

```text
crecimiento real aproximado =
((1 + variación del salario) / (1 + variación del IPC) - 1) * 100
```

Interpretación:

- valor positivo: el salario creció por encima de los precios;
- valor negativo: los precios crecieron por encima del salario;
- valor cercano a cero: ambos crecieron aproximadamente al mismo ritmo.

## Limitaciones

Esta métrica es una aproximación. El salario mínimo de la fuente es anual y
corresponde al valor legal vigente desde el 1° de enero, mientras que el IPC
es mensual. El corrimiento de un año descrito arriba alinea los períodos a
nivel anual, pero sigue siendo una aproximación de calendario: no usa la
fecha exacta de cada ajuste salarial (que en la práctica podría no ser
siempre el 1° de enero) ni el IPC del mes exacto correspondiente.

Además, la base octubre 2022 = 100 es solamente una escala de referencia: no
significa que los precios fueran de 100 pesos. Las variaciones porcentuales no
dependen de esa escala.

## Script

`actividad03.py`:

1. lee `salario_minimo_clean.parquet` de Actividad 2;
2. lee y normaliza el Excel del IPC;
3. genera `ipc_anual.parquet`;
4. calcula las métricas solicitadas (mínimo, máximo, promedio del salario);
5. conecta ambos Parquet por año (alineando los períodos, ver arriba) y
   calcula la variación interanual y el crecimiento real aproximado;
6. guarda la tabla conectada en `salario_ipc_metricas.parquet`;
7. genera la gráfica `analisis_salario_ipc.png`;
8. muestra en consola solo el resumen de negocio (años con ganancia/pérdida
   real, promedio, mejor y peor año) — la tabla completa queda en el
   Parquet del punto 6, no se imprime entera.
