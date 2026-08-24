# Actividad 02 - Profiling del Salario Mínimo Nacional (Datos Abiertos Uruguay)

Repositorio: <https://github.com/cardo88/UCU-BigData-2026.git>

## Objetivo

Descargar un dataset de datos abiertos (indicador **10454 - Salario Mínimo
Nacional**, publicado en el portal de [Datos Abiertos de Uruguay](https://catalogodatos.gub.uy/)),
almacenarlo localmente en formato Parquet, y hacer su **profiling**: entenderlo
tanto desde el punto de vista técnico (tipos, nulos, duplicados, clave
primaria) como desde el punto de vista de negocio (qué representa el
indicador, en qué unidad está, qué se puede y no se puede comparar con él).
Adicionalmente, se analiza el **ritmo de crecimiento** de la serie a lo
largo del tiempo.

## Acciones mínimas de análisis

**Proceso de carga**: Python 3, `pandas`, `pyarrow` y `matplotlib`, sobre el
venv del repo. Al descargar el indicador se obtienen dos archivos: un JSON
de **metadatos** (ficha técnica, sin filas de datos) y el archivo de
**datos** real, que —a pesar de estar al lado de un `.json`— viene en
formato **XML** (`10454_salario_minimo_nacional_-smn-.xml`), un `<Fila>`
por año con `<año>` y `<valor>`. Se guarda en Parquet, separando siempre
crudo de limpio:

```bash
source .venv/bin/activate
python Actividad02/01_ingesta.py             # XML -> salario_minimo_raw.parquet
python Actividad02/02_profiling.py           # análisis técnico + de negocio
python Actividad02/03_limpieza.py            # -> salario_minimo_clean.parquet
python Actividad02/04_analisis_crecimiento.py # CAGR + gráfico
```

**Profiling técnico**: el dataset tiene **28 filas** (una por año,
1991-2018) y **2 columnas**. Ambas llegan como texto (`object`), con
formato numérico uruguayo (coma decimal): `año` como `"1991,0"` y `valor`
como `"118,0"`. Sin nulos ni duplicados. `año` es válida como clave
primaria (28 valores únicos para 28 filas).

**Profiling de negocio** (a partir del JSON de metadatos): el SMN es el
piso legal de remuneración en Uruguay (Ley 10449), fijado por el MTSS, y
está expresado en **pesos corrientes** — valor **nominal**, sin ajustar por
inflación. Esto es clave para el análisis: los $118 de 1991 y los $13.430
de 2018 no son comparables en poder de compra sin deflactar la serie (por
ejemplo, con el IPC del INE).

**Calidad de datos y corrección** (paso 3): se corrigió el formato numérico
(coma → punto, texto → `int`/`float`) y se ordenó la serie por año, ya que
el XML no garantiza orden. No hubo nulos ni duplicados que tratar. El
resultado se guarda en un Parquet separado del crudo, manteniendo
trazabilidad.

## Resultados

La consigna original sugiere mirar máximos y mínimos, pero en
una serie que **siempre crece** (un salario mínimo nominal no puede bajar
por ley), el mínimo es casi siempre el primer año y el máximo el último —
no aportan un hallazgo por sí solos. El valor agregado del análisis está en
entender el **ritmo** de crecimiento:

- **Mínimo**: $118 (1991) — **Máximo**: $13.430 (2018). Serie
  monótonamente creciente en todo el período.
- **CAGR 1991-2018: 19,17% anual.** Es la métrica correcta para resumir el
  crecimiento compuesto de una serie año a año, a diferencia del promedio
  simple de variaciones interanuales (20,50%), que un salto puntual grande
  distorsiona hacia arriba.
- **Mayor salto interanual: +94,92% en 1992** (de $118 a $230). Se observa
  en el gráfico que el ritmo fue más alto y volátil en los años 90 y con el
  salto de 2005 (+65,06%), estabilizándose en 10%-13% anual desde 2013.

El gráfico de la evolución (adjunto en esta entrega como
`evolucion_salario_minimo.png`) muestra esto en dos paneles: arriba, el
nivel del SMN en pesos corrientes; abajo, la variación interanual (%) año a
año, con una línea punteada marcando el CAGR del período completo como
referencia.

## Uso de IA como apoyo

Se utilizó asistencia de IA (Claude, Anthropic) para mejorar la redacción
de este documento y como apoyo en la sintaxis del código. El criterio de
resolución, el análisis de negocio y las decisiones sobre cómo tratar cada
problema de calidad de datos son propios.

---

## Anexo

### A. Archivos adjuntos

Junto a este documento se adjunta, en el zip de entrega:

- `evolucion_salario_minimo.png`: gráfico referenciado en la sección de
  Resultados.

### B. Código completo de los scripts

Los scripts no se adjuntan en esta entrega — están disponibles en el
repositorio del curso, en la carpeta `Actividad02/`:

- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad02/01_ingesta.py>
- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad02/02_profiling.py>
- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad02/03_limpieza.py>
- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad02/04_analisis_crecimiento.py>

### C. Sobre el CAGR (por qué no es el promedio simple de los % anuales)

```
CAGR = (valor_final / valor_inicial) ^ (1 / cantidad_de_años) - 1
```

A diferencia del promedio simple, el CAGR tiene en cuenta que el
crecimiento de un año se aplica sobre una base que ya incluye el
crecimiento de los años anteriores (igual que el interés compuesto). Es la
métrica estándar para resumir el crecimiento de una serie financiera o
salarial en un solo número representativo.
