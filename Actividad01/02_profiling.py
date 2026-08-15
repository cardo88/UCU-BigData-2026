# =============================================================================
# PASO 2 - PROFILING: entender el dataset antes de corregir nada
# =============================================================================
#
# "Profiling" (o "perfilado de datos") significa analizar un dataset para
# entender su forma y calidad antes de usarlo: cuántas filas y columnas
# tiene, qué tipo de dato tiene cada columna, cuántos valores faltan,
# si hay filas duplicadas, y si existe una columna que sirva como
# "clave primaria" (un identificador único por fila, sin repetidos ni nulos).
#
# Este script NO modifica ni corrige nada, solo reporta cómo está el dato
# tal cual llegó. Las correcciones se hacen después, en 03_limpieza.py,
# una vez que sabemos qué hay que corregir.
#
# Se lee directamente el Parquet generado en el paso 1 (01_ingesta.py),
# porque es mucho más rápido de leer que el TSV original.
#
# Cómo correr este script (parado en la raíz del repo, con el venv activado):
#   python Actividad01/02_profiling.py
# =============================================================================

import pandas as pd

RUTA_PARQUET_RAW = "Actividad01/name_basics_raw.parquet"

# --- Lectura -----------------------------------------------------------------
df = pd.read_parquet(RUTA_PARQUET_RAW, engine="pyarrow")

# --- 1. Cantidad de filas y columnas -----------------------------------------
# df.shape devuelve una tupla (filas, columnas).
print("Shape:", df.shape)
print(f"Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")

# --- 2. Tipos de datos por columna -------------------------------------------
# df.dtypes muestra qué tipo de dato interpretó pandas para cada columna
# (por ejemplo: object para texto, float64/int64 para números, etc.).
# "object" en pandas generalmente significa texto (string), pero en
# realidad es un tipo genérico que puede contener cualquier objeto de
# Python (no solo strings). Ver README.md para más detalle sobre esto.
print("\nTipos de datos:")
print(df.dtypes)

# --- 3. Completitud: cuántos valores nulos tiene cada columna ----------------
# Un valor "nulo" (NaN / None) representa un dato faltante. Acá calculamos,
# por columna: cuántos nulos tiene en total, y qué porcentaje representa
# sobre el total de filas.
print("\nNulos por columna:")
nulos = df.isnull().sum()
pct_nulos = (nulos / len(df) * 100).round(2)
completitud = pd.DataFrame({"nulos": nulos, "pct_nulos": pct_nulos})
print(completitud)

# --- 4. Duplicados exactos (fila completa idéntica a otra) ------------------
# df.duplicated() marca True en las filas que son un duplicado exacto de
# otra fila anterior (todas las columnas iguales). .sum() cuenta cuántas
# filas están en esa situación.
print("\nDuplicados exactos (fila completa):", df.duplicated().sum())

# --- 5. Clave primaria candidata: nconst -------------------------------------
# "nconst" es el identificador único de cada persona en IMDb (ej: nm0000001).
# Para que una columna sea una clave primaria válida tiene que cumplir DOS
# condiciones:
#   a) Ser única: no puede haber dos filas con el mismo valor.
#   b) No tener nulos: toda fila tiene que tener un valor en esa columna.
print("\nValores únicos en nconst:", df["nconst"].nunique())
print("Total de filas:", len(df))
print(
    "nconst es clave primaria (único y sin nulos):",
    df["nconst"].is_unique and df["nconst"].isnull().sum() == 0,
)

# Si hubiera nconst duplicados, acá se listarían todas las filas
# involucradas (keep=False mantiene todas las copias, no solo la repetida).
dup_nconst = df[df.duplicated(subset="nconst", keep=False)]
print("Filas con nconst duplicado:", len(dup_nconst))

# --- Notas sobre columnas "compuestas" ---------------------------------------
# primaryProfession y knownForTitles son columnas de texto que en realidad
# contienen VARIOS valores separados por comas dentro de un mismo string,
# por ejemplo: "actor,producer,writer". No son listas reales de Python,
# son un solo string con comas adentro. Esto se corrige en 03_limpieza.py,
# convirtiéndolas en listas reales para que sean más fáciles de analizar
# (por ejemplo, para contar cuántas personas son "actor").
