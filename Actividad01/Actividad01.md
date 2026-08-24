# Actividad 01 - Dataset name.basics (IMDb)

Repositorio: <https://github.com/cardo88/UCU-BigData-2026.git>

## Objetivo

Trabajar el dataset público `name.basics` de IMDb (listado de personas:
actores, directores, etc.) end-to-end: cargar el dato crudo, entenderlo
mediante profiling, y entregar una versión limpia y corregida, manteniendo
trazabilidad entre ambas versiones.

## 1. Proceso de carga

**Herramientas usadas**: Python 3, `pandas` y `pyarrow`, dentro de un
entorno virtual del repo (`.venv`). Todo el trabajo se hizo mediante scripts
(no notebook), corridos desde la raíz del repo:

```bash
source .venv/bin/activate
python Actividad01/01_ingesta.py
python Actividad01/02_profiling.py
python Actividad01/03_limpieza.py
```

**Origen del dato**: IMDb distribuye `name.basics` como un TSV comprimido
con gzip (`name.basics.tsv.gz`). El script de ingesta (`01_ingesta.py`) lo
lee directamente comprimido con pandas (`compression="gzip"`), que lo
descomprime al vuelo — no hace falta descomprimirlo a mano.

**Formato de guardado**: el dato se guarda en **Parquet**, no en TSV/CSV,
por ser un formato columnar, tipado y comprimido, más apto para análisis
posterior que un texto plano. Se generan dos archivos separados:

- `name_basics_raw.parquet`: el dato tal cual llegó de IMDb, sin ninguna
  corrección (ingesta, paso 1).
- `name_basics_clean.parquet`: el dato ya corregido (limpieza, paso 3).

Mantener el crudo y el limpio en archivos separados permite trazabilidad:
siempre se puede volver a comparar el dato "tal cual llegó" contra el
"curado", y volver a regenerar la limpieza si cambia el criterio.

Nota: ambos `.parquet` no están versionados en git por su tamaño (cientos
de MB) — se regeneran corriendo los scripts en orden.

## 2. Descripción de los datos

El dataset tiene **15.573.835 filas y 6 columnas** (el número exacto varía
un poco entre descargas porque IMDb lo actualiza todos los días):

| Columna | Contenido | Tipo original |
|---|---|---|
| `nconst` | Identificador único de persona en IMDb (ej: `nm0000001`) | texto |
| `primaryName` | Nombre de la persona | texto |
| `birthYear` | Año de nacimiento | numérico |
| `deathYear` | Año de fallecimiento | numérico |
| `primaryProfession` | Hasta 3 profesiones, separadas por coma | texto |
| `knownForTitles` | Títulos por los que es conocida, separados por coma | texto |

`nconst` funciona como **clave primaria**: tiene tantos valores únicos como
filas y ningún nulo. No se encontraron duplicados de fila completa.

## 3. Calidad de los datos

El profiling (`02_profiling.py`) detectó los siguientes problemas, todos
corregidos en la limpieza (`03_limpieza.py`):

| # | Problema detectado | % afectado | Corrección aplicada |
|---|---|---|---|
| 1 | `birthYear` y `deathYear` quedaron como `float64` (ej: `1954.0`) por los nulos, siendo en realidad años (enteros) | 95,64% / 98,32% nulos | Convertidos a `Int64`, el entero "nullable" de pandas — admite nulos sin forzar todo a float |
| 2 | `primaryProfession` y `knownForTitles` venían como un string con valores separados por coma (ej: `"actor,producer,writer"`), no como una lista real | 20,25% / 12,07% nulos | Convertidos a listas de Python nativas, tipo soportado por Parquet |
| 3 | `primaryName` sin valor en algunas filas | 0,00% (100 filas) | Filas descartadas — sin nombre no aportan al análisis |
| 4 | Duplicados de fila completa | 0% | No requirió acción |
| 5 | Validez de `nconst` como clave primaria | — | Confirmada, no requirió corrección |

**Sobre el tipo `object` en pandas**: las columnas de texto quedan tipadas
como `object` en vez de un tipo "string" dedicado, porque pandas no valida
ni garantiza que todas las celdas sean `str` — es un tipo genérico que en la
práctica casi siempre contiene texto, pero no lo fuerza.

## Los scripts

| Script | Qué hace | Entrada | Salida |
|---|---|---|---|
| `01_ingesta.py` | Lee el TSV comprimido original y lo guarda tal cual en Parquet | `name.basics.tsv.gz` | `name_basics_raw.parquet` |
| `02_profiling.py` | Analiza el Parquet crudo: filas/columnas, tipos, nulos, duplicados, clave primaria | `name_basics_raw.parquet` | solo imprime en consola |
| `03_limpieza.py` | Corrige los problemas detectados en el profiling | `name_basics_raw.parquet` | `name_basics_clean.parquet` |

Cada script tiene comentarios en español explicando línea por línea qué hace
y por qué, pensados para poder releerlos más adelante sin tener que
recordar el contexto.

## Uso de IA como apoyo

Se utilizó asistencia de IA (Claude, Anthropic) para mejorar la redacción de
este documento y como apoyo en la sintaxis del código. El criterio de
resolución, la lógica de cada script y las decisiones sobre cómo tratar cada
problema de calidad de datos son propias.

---

## Anexo

### A. Captura de pantalla

Ver `Screenshot 2026-08-15 at 18.48.41.png` en esta misma carpeta, con la
salida por consola del profiling y la limpieza.

### B. Código completo de los scripts

Los scripts no se adjuntan en esta entrega — están disponibles en el
repositorio del curso, en la carpeta `Actividad01/`:

- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad01/01_ingesta.py>
- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad01/02_profiling.py>
- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad01/03_limpieza.py>
