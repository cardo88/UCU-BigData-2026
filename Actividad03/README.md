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
Actividad03/analisis_salario_ipc.png
```

La imagen tiene dos paneles: arriba compara las variaciones anuales del
salario mínimo y del IPC; abajo muestra el crecimiento real aproximado del
salario. Las barras verdes indican crecimiento por encima del IPC y las rojas
indican pérdida aproximada de poder adquisitivo.

## Cómo se conectan los datos

El XML del salario tiene un valor anual. El IPC tiene observaciones mensuales.
Para obtener una observación anual, el script ordena los registros por fecha y
conserva el último mes disponible de cada año, normalmente diciembre. Esto
permite inspeccionar y reutilizar la transformación sin volver a leer el Excel.

Luego ambas fuentes se unen mediante `año`.

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
corresponde al valor legal del año, mientras que el IPC es mensual. Una
comparación más precisa debería usar la fecha exacta de cada ajuste del salario
mínimo y el IPC correspondiente al mismo período.

Además, la base octubre 2022 = 100 es solamente una escala de referencia: no
significa que los precios fueran de 100 pesos. Las variaciones porcentuales no
dependen de esa escala.

## Script

`actividad03.py`:

1. lee `salario_minimo_clean.parquet` de Actividad 2;
2. lee y normaliza el Excel del IPC;
3. genera `ipc_anual.parquet`;
4. calcula las métricas solicitadas;
5. conecta ambos Parquet por año;
6. genera la gráfica `analisis_salario_ipc.png`;
7. muestra la tabla y una conclusión en la consola.
