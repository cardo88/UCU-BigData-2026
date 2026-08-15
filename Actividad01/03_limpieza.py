# =============================================================================
# PASO 3 - LIMPIEZA: corregir los problemas detectados en el profiling
# =============================================================================
#
# En 02_profiling.py detectamos lo siguiente sobre "name.basics":
#
#   1. birthYear y deathYear quedaron como float64 (ej: 1954.0) en vez de
#      números enteros, porque tienen muchos nulos y pandas usa float
#      para poder representar NaN en columnas numéricas. Como son años,
#      tiene más sentido que sean enteros.
#
#   2. primaryProfession y knownForTitles son strings con varios valores
#      separados por comas (ej: "actor,producer,writer"), no listas reales.
#      Los convertimos a listas de Python para que sea más fácil filtrar
#      y analizar (ej: "¿cuántas personas tienen 'actor' entre sus
#      profesiones?").
#
#   3. primaryName tiene 100 filas sin valor (nulo). Al ser el nombre de
#      la persona, sin nombre la fila no aporta información útil para
#      análisis por nombre, así que esas filas se descartan.
#
#   4. nconst ya lo confirmamos en el profiling como clave primaria válida
#      (sin nulos, sin duplicados), así que no requiere corrección.
#
#   5. No había duplicados de fila completa, así que no hace falta
#      deduplicar.
#
# Este script parte del Parquet "crudo" generado en 01_ingesta.py, aplica
# estas correcciones, y guarda el resultado en un Parquet NUEVO y
# SEPARADO (name_basics_clean.parquet). Así queda trazabilidad: el
# archivo raw (crudo) no se pisa/sobrescribe, y el archivo clean (limpio)
# se puede regenerar en cualquier momento volviendo a correr este script.
#
# Cómo correr este script (parado en la raíz del repo, con el venv activado):
#   python Actividad01/03_limpieza.py
# =============================================================================

import pandas as pd

RUTA_PARQUET_RAW = "Actividad01/name_basics_raw.parquet"
RUTA_PARQUET_CLEAN = "Actividad01/name_basics_clean.parquet"

# --- Lectura del dato crudo ---------------------------------------------------
df = pd.read_parquet(RUTA_PARQUET_RAW, engine="pyarrow")
filas_antes = len(df)
print(f"Filas antes de limpiar: {filas_antes:,}")

# --- Corrección 1: años como enteros (nullable) ------------------------------
# "Int64" (con mayúscula) es el tipo entero "nullable" de pandas: a
# diferencia del int64 normal de Python/NumPy, este SÍ admite valores
# nulos (pd.NA) mezclados con enteros. Así evitamos que 1954 se vea como
# 1954.0, pero seguimos pudiendo representar los años faltantes.
df["birthYear"] = df["birthYear"].astype("Int64")
df["deathYear"] = df["deathYear"].astype("Int64")

# --- Corrección 2: strings separados por comas -> listas reales -------------
# Ejemplo: "actor,producer,writer" -> ["actor", "producer", "writer"]
# Para las filas nulas (NaN), dejamos una lista vacía en vez de romper el
# split. Esto facilita después filtrar por profesión o por título
# (ej: df[df["primaryProfession"].apply(lambda lista: "actor" in lista)]).
def separar_en_lista(valor):
    if pd.isna(valor):
        return []
    return valor.split(",")

df["primaryProfession"] = df["primaryProfession"].apply(separar_en_lista)
df["knownForTitles"] = df["knownForTitles"].apply(separar_en_lista)

# --- Corrección 3: descartar filas sin nombre --------------------------------
# Solo son 100 filas sobre 15.5 millones (0.00%), no afecta el análisis
# general y evita tener registros sin el dato más básico (el nombre).
df = df.dropna(subset=["primaryName"])

filas_despues = len(df)
print(f"Filas después de limpiar: {filas_despues:,}")
print(f"Filas descartadas (sin primaryName): {filas_antes - filas_despues:,}")

# --- Verificación rápida post-limpieza ---------------------------------------
print("\nTipos de datos luego de la limpieza:")
print(df.dtypes)

# --- Guardado del dato limpio -------------------------------------------------
# Nota: las columnas que ahora son listas de Python (primaryProfession,
# knownForTitles) se guardan en Parquet como tipo "list", que es un tipo
# nativo soportado por el formato (no hace falta volver a convertirlas a
# string).
df.to_parquet(RUTA_PARQUET_CLEAN, engine="pyarrow", compression="snappy")
print(f"\nGuardado el dataset limpio en: {RUTA_PARQUET_CLEAN}")
