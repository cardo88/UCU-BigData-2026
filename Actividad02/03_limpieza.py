# =============================================================================
# PASO 3 - LIMPIEZA: corregir los problemas detectados en el profiling
# =============================================================================
#
# En 02_profiling.py detectamos lo siguiente sobre "salario_minimo_raw":
#
#   1. "año" viene como texto con formato decimal, ej: "1991,0", en vez
#      de como el entero 1991. Hay que sacarle la coma y quedarnos con
#      la parte entera.
#
#   2. "valor" viene como texto con COMA como separador decimal
#      (convención uruguaya), ej: "118,0", en vez de PUNTO como espera
#      Python/pandas por defecto. Hay que reemplazar la coma por un
#      punto antes de convertir a número.
#
#   3. No había nulos ni duplicados (confirmado en el profiling), así
#      que no hace falta descartar ni deduplicar filas.
#
#   4. El dataset no viene ordenado explícitamente por año en el XML,
#      así que lo ordenamos para que cualquier análisis posterior
#      (evolución en el tiempo, variación interanual) sea correcto.
#
# Este script parte del Parquet "crudo" generado en 01_ingesta.py, aplica
# estas correcciones, y guarda el resultado en un Parquet NUEVO y
# SEPARADO (salario_minimo_clean.parquet), para mantener trazabilidad
# entre el dato "tal cual llegó" y el dato "curado".
#
# Cómo correr este script (parado en la raíz del repo, con el venv activado):
#   python Actividad02/03_limpieza.py
# =============================================================================

import pandas as pd

RUTA_PARQUET_RAW = "Actividad02/salario_minimo_raw.parquet"
RUTA_PARQUET_CLEAN = "Actividad02/salario_minimo_clean.parquet"

# --- Lectura del dato crudo ---------------------------------------------------
df = pd.read_parquet(RUTA_PARQUET_RAW, engine="pyarrow")
filas_antes = len(df)
print(f"Filas antes de limpiar: {filas_antes:,}")

# --- Corrección 1: año como entero --------------------------------------------
# "1991,0" -> "1991" -> 1991 (int). Partimos el string por la coma y nos
# quedamos con la parte antes de la coma (la parte entera).
df["año"] = df["año"].str.split(",").str[0].astype(int)

# --- Corrección 2: valor como número decimal, con punto en vez de coma ------
# "118,0" -> "118.0" -> 118.0 (float). Reemplazamos la coma decimal por
# un punto, que es el separador que entiende Python al convertir a float.
df["valor"] = df["valor"].str.replace(",", ".", regex=False).astype(float)

# --- Corrección 3: ordenar por año --------------------------------------------
# El XML no garantiza un orden. Para que la evolución en el tiempo se
# pueda graficar/analizar correctamente, ordenamos de año más viejo a
# más nuevo y reseteamos el índice.
df = df.sort_values("año").reset_index(drop=True)

filas_despues = len(df)
print(f"Filas después de limpiar: {filas_despues:,}")

# --- Verificación rápida post-limpieza ---------------------------------------
print("\nTipos de datos luego de la limpieza:")
print(df.dtypes)

print("\nRango de años:", df["año"].min(), "-", df["año"].max())
print(
    "Duplicados de año tras la limpieza:",
    df.duplicated(subset="año").sum(),
)

# --- Guardado del dato limpio -------------------------------------------------
df.to_parquet(RUTA_PARQUET_CLEAN, engine="pyarrow", compression="snappy")
print(f"\nGuardado el dataset limpio en: {RUTA_PARQUET_CLEAN}")
