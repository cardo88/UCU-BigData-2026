# Actividad 02 - Salario Mínimo Nacional (Datos Abiertos Uruguay)

Trabajo sobre el indicador **10454 - Salario Mínimo Nacional (SMN)**, publicado
en el portal de [Datos Abiertos de Uruguay](https://catalogodatos.gub.uy/).
El objetivo de la actividad es:

1. Descargar un dataset de datos abiertos y almacenarlo localmente en el
   formato adecuado (Parquet).
2. Hacer profiling del dato: entenderlo desde el punto de vista técnico
   (tipos, nulos, duplicados, clave primaria) y desde el punto de vista de
   negocio (qué representa el indicador, en qué unidad está, qué se puede y
   no se puede comparar con él).
3. Ir más allá de máximos/mínimos: como es una serie de tiempo que crece
   año a año, entender **cómo** crece (ritmo, aceleración/desaceleración) y
   visualizarlo en un gráfico.

## Sobre los archivos descargados

Al descargar el indicador desde el portal se bajan dos archivos:

| Archivo | Qué es |
|---|---|
| `metadatos_indicador-10454.json` | **Metadatos**, no datos. Es la ficha técnica del indicador: qué mide, quién lo calcula, en qué unidad está, qué representa cada columna. No tiene ninguna fila de datos. |
| `10454_salario_minimo_nacional_-smn-.xml` | **Los datos**. A pesar de que el archivo de metadatos es un `.json`, el dato real viene en formato **XML**, no CSV: un `<Fila>` por año, cada una con `<año>` y `<valor>`. |

Este punto vale la pena aclararlo porque a primera vista, por tener un
`.json` al lado, uno podría asumir que ahí están los datos (o que el otro
archivo es un `.csv`). Conviene siempre abrir los archivos y mirar su
contenido real antes de asumir el formato por la extensión o por lo que
dice el nombre.

## Cómo correr esto

Hace falta el venv del repo activado (ver `doc/preparar_venv.md`), con
`pandas`, `pyarrow` y `matplotlib` instalados (`pip install matplotlib` si
no lo tenés — no viene en el venv original de la Actividad01). Todos los
comandos se corren **parado en la raíz del repo** (`UCU-BigData-2026/`),
no desde adentro de `Actividad02/`, porque los scripts usan rutas
relativas a la raíz:

```bash
source .venv/bin/activate
pip install matplotlib   # una sola vez, si no lo tenés ya
python Actividad02/01_ingesta.py
python Actividad02/02_profiling.py
python Actividad02/03_limpieza.py
python Actividad02/04_analisis_crecimiento.py
```

Hay que correrlos en ese orden, porque cada uno depende del archivo que
generó el anterior.

## Los scripts

| Script | Qué hace | Entrada | Salida |
|---|---|---|---|
| `01_ingesta.py` | Lee el XML original y lo guarda tal cual (año/valor como texto) en Parquet | `10454_salario_minimo_nacional_-smn-.xml` | `salario_minimo_raw.parquet` |
| `02_profiling.py` | Analiza el Parquet crudo: filas/columnas, tipos, nulos, duplicados, clave primaria, y resume el contexto de negocio a partir del JSON de metadatos | `salario_minimo_raw.parquet` | solo imprime en consola |
| `03_limpieza.py` | Corrige el formato numérico (coma decimal uruguaya, año como texto) y ordena por año | `salario_minimo_raw.parquet` | `salario_minimo_clean.parquet` |
| `04_analisis_crecimiento.py` | Calcula variación interanual, CAGR y genera el gráfico de evolución | `salario_minimo_clean.parquet` | `salario_minimo_analisis.parquet`, `evolucion_salario_minimo.png` |

Cada script tiene comentarios en español explicando línea por línea qué
hace y por qué, siguiendo el mismo criterio que en `Actividad01/`.

Los archivos `.parquet` y el `.png` generados no están versionados en git
(se regeneran corriendo los scripts).

## Resultado del profiling (paso 2)

El dataset tiene **28 filas** (una por año, 1991-2018) y **2 columnas**:

| Columna | Tipo tal cual llegó | Problema detectado |
|---|---|---|
| `año` | texto (`object`) | Viene como `"1991,0"` en vez de `1991` (entero) |
| `valor` | texto (`object`) | Viene como `"118,0"` en vez de `118.0`, con **coma** como separador decimal (convención uruguaya), no punto |

Otros hallazgos:

- **Nulos**: 0 en ambas columnas.
- **Duplicados de fila completa**: 0.
- **Clave primaria**: `año` es válida como clave primaria — 28 valores
  únicos para 28 filas, sin nulos. Tiene sentido: un indicador anual
  no debería tener dos valores para el mismo año.

### Entendiendo el negocio (a partir del JSON de metadatos)

El JSON de metadatos (`metadatos_indicador-10454.json`) es lo que permite
entender qué significa realmente el número, más allá de la tabla:

- **Qué es**: el Salario Mínimo Nacional (SMN) es el piso legal por debajo
  del cual no puede estar ninguna remuneración en Uruguay (Ley 10449,
  Decreto 1534/969).
- **Quién lo fija**: el Ministerio de Trabajo y Seguridad Social (MTSS).
- **Unidad**: "pesos corrientes" — es decir, el valor **nominal** de cada
  año, **sin ajustar por inflación**. Esto es central para cualquier
  análisis: los $118 de 1991 y los $13.430 de 2018 no son directamente
  comparables en poder de compra, porque hubo inflación acumulada entre
  medio. Estos datos sirven para ver la evolución del monto legal
  nominal, no el poder adquisitivo real (para eso habría que deflactar
  la serie con un índice de precios, por ejemplo el IPC del INE).
- **Corte temporal**: cada valor corresponde al 1° de enero del año en
  cuestión, no es un promedio anual.

## Problemas detectados y corregidos (paso 3)

| # | Problema | Corrección aplicada |
|---|---|---|
| 1 | `año` es texto con formato decimal (`"1991,0"`) | Se corta en la coma y se convierte a `int` |
| 2 | `valor` es texto con coma decimal (`"118,0"`) | Se reemplaza la coma por punto y se convierte a `float` |
| 3 | El XML no garantiza orden | Se ordena por `año` ascendente |
| 4 | — | No había nulos ni duplicados, no hizo falta descartar ni deduplicar filas |

El resultado (`salario_minimo_clean.parquet`) queda en un archivo
**separado** del crudo (`salario_minimo_raw.parquet`), para mantener
trazabilidad entre el dato "tal cual llegó" y el dato "curado".

## Análisis de crecimiento (paso 4)

La consigna original pide mirar máximos y mínimos, pero en una serie que
**siempre crece** (como un salario mínimo nominal, que legalmente nunca
puede bajar), el mínimo es casi siempre el primer año y el máximo el
último — no aportan un hallazgo de negocio por sí solos. Lo que sí
aporta valor es entender el **ritmo** de crecimiento:

- **Mínimo**: $118 (1991). **Máximo**: $13.430 (2018). Serie
  monótonamente creciente: nunca bajó de un año a otro en todo el
  período.
- **CAGR 1991-2018 (tasa de crecimiento anual compuesta): 19,17% por
  año.** Es la forma correcta de resumir en un solo número el
  crecimiento de una serie que se compone año a año (como interés
  compuesto), a diferencia del promedio simple de las variaciones
  interanuales (20,50%), que un salto puntual grande puede distorsionar
  hacia arriba.
- **Mayor salto interanual: +94,92% en 1992** (de $118 a $230). Saltos
  así suelen reflejar decisiones puntuales de política salarial del
  MTSS, no una tendencia que se repita todos los años — de hecho, se ve
  en el gráfico que el ritmo de crecimiento fue mucho más alto y volátil
  en los años 90 y con el salto de 2005 (+65,06%), y se estabilizó en un
  crecimiento más moderado y constante (10%-13% anual) a partir de 2013.

El gráfico `evolucion_salario_minimo.png` muestra esto en dos paneles:
arriba, el nivel del SMN en pesos corrientes; abajo, la variación
interanual (%) año a año, con una línea punteada marcando el CAGR de
todo el período como referencia.

### Sobre el CAGR: por qué no es simplemente el promedio de los % anuales

El CAGR se calcula como:

```
CAGR = (valor_final / valor_inicial) ^ (1 / cantidad_de_años) - 1
```

A diferencia del promedio simple (que suma todos los % anuales y divide
entre la cantidad de años), el CAGR tiene en cuenta que el crecimiento
de un año se aplica sobre una base que ya incluye el crecimiento de los
años anteriores (igual que el interés compuesto). Por eso es la métrica
estándar para resumir el crecimiento de una serie financiera o salarial
a lo largo de varios años en un solo número representativo.
