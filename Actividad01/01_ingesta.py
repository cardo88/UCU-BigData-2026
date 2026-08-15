# =============================================================================
# PASO 1 - INGESTA: leer el dataset original y guardarlo localmente en Parquet
# =============================================================================
#
# Qué hace este script:
#   1. Lee el archivo original "name.basics.tsv.gz" (dataset de nombres de
#      IMDb, comprimido con gzip).
#   2. Lo guarda tal cual (sin corregir nada todavía) en formato Parquet.
#
# Por qué Parquet y no dejar el TSV:
#   - Parquet es un formato columnar (piensa cada columna guardada por
#     separado, no fila por fila como el TSV/CSV). Eso lo hace mucho más
#     rápido de leer cuando después solo necesitás algunas columnas.
#   - Ocupa mucho menos espacio en disco porque comprime los datos.
#   - Guarda el tipo de dato de cada columna (int, float, string, etc.),
#     así no hay que estar "adivinando" tipos cada vez que se lee, como
#     pasa con un CSV/TSV.
#
# Nota sobre el archivo original:
#   IMDb distribuye este dataset comprimido con gzip: "name.basics.tsv.gz".
#   Ojo con Safari: al descargar un ".gz", algunos navegadores (Safari
#   entre ellos) lo descomprimen automáticamente y te dejan el ".tsv" ya
#   descomprimido en el disco, sin que lo pidas. Para este script
#   necesitamos el archivo TODAVÍA comprimido (el ".gz"), porque queremos
#   practicar cómo se lee un archivo comprimido directamente con pandas,
#   sin tener que descomprimirlo a mano antes.
#
#   pandas puede leer un CSV/TSV comprimido sin que vos lo descomprimas:
#   le pasás compression="gzip" y él lo descomprime "al vuelo", en
#   memoria, mientras lo va leyendo.
#
# Cómo correr este script (parado en la raíz del repo, con el venv activado):
#   python Actividad01/01_ingesta.py
# =============================================================================

import pandas as pd

# --- Rutas de entrada y salida -----------------------------------------------
# Se usan rutas relativas a la raíz del repo. Si corrés el script desde
# adentro de Actividad01/, estas rutas van a fallar (no van a encontrar
# el archivo). Por eso siempre hay que pararse en la raíz del repo.
RUTA_ENTRADA = "Actividad01/name.basics.tsv.gz"
RUTA_SALIDA_PARQUET = "Actividad01/name_basics_raw.parquet"

# --- 1. Lectura del archivo original -----------------------------------------
# sep="\t"            -> el archivo está separado por tabs (TSV), no por comas.
# compression="gzip"  -> el archivo está comprimido con gzip. Con este
#                         parámetro, pandas lo descomprime automáticamente
#                         mientras lo lee, sin que haga falta descomprimirlo
#                         a mano ni dejar un ".tsv" suelto en el disco.
# na_values="\\N"      -> en los datasets de IMDb, los valores faltantes/nulos
#                         se representan con el string literal "\N". Le decimos
#                         a pandas que interprete ese texto como un nulo real
#                         (NaN), y no como el string "\N".
# low_memory=False    -> el archivo es grande (>15 millones de filas) y tiene
#                         columnas con tipos mezclados. Con low_memory=False,
#                         pandas lee el archivo completo antes de decidir el
#                         tipo de cada columna, evitando warnings de tipos
#                         inconsistentes (a costa de usar más memoria RAM).
print("Leyendo el archivo original comprimido (puede tardar unos minutos, es grande)...")
df = pd.read_csv(
    RUTA_ENTRADA,
    sep="\t",
    compression="gzip",
    na_values="\\N",
    low_memory=False,
)

print(f"Archivo leído. Filas: {len(df):,} | Columnas: {df.shape[1]}")

# --- 2. Guardado en formato Parquet ------------------------------------------
# engine="pyarrow"       -> librería que sabe escribir/leer Parquet.
# compression="snappy"   -> algoritmo de compresión rápido y liviano, es el
#                            estándar por defecto en el ecosistema Parquet
#                            (buen balance entre velocidad y tamaño final).
#
# Importante: este parquet es el dato "crudo" (raw), tal cual vino el
# archivo original, sin ninguna corrección. Sirve como respaldo/punto de
# partida antes de limpiar nada. La limpieza se hace en el paso 3
# (03_limpieza.py), que genera un parquet aparte ya corregido.
df.to_parquet(RUTA_SALIDA_PARQUET, engine="pyarrow", compression="snappy")

print(f"Guardado como Parquet en: {RUTA_SALIDA_PARQUET}")
