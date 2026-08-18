# =============================================================================
# PASO 2 - PROFILING: entender el dataset antes de corregir nada
# =============================================================================
#
# "Profiling" significa analizar un dataset para entender su forma y
# calidad antes de usarlo: cuántas filas y columnas tiene, qué tipo de
# dato tiene cada columna, cuántos valores faltan, si hay filas
# duplicadas, y si existe una clave primaria (identificador único por
# fila, sin repetidos ni nulos).
#
# Este script NO modifica ni corrige nada, solo reporta cómo está el dato
# tal cual llegó. Las correcciones se hacen después, en 03_limpieza.py.
#
# Se lee directamente el Parquet generado en el paso 1 (01_ingesta.py).
#
# Cómo correr este script (parado en la raíz del repo, con el venv activado):
#   python Actividad02/02_profiling.py
# =============================================================================

import pandas as pd

RUTA_PARQUET_RAW = "Actividad02/salario_minimo_raw.parquet"

# --- Lectura -----------------------------------------------------------------
df = pd.read_parquet(RUTA_PARQUET_RAW, engine="pyarrow")

# --- 1. Cantidad de filas y columnas -----------------------------------------
print("Shape:", df.shape)
print(f"Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")

# --- 2. Tipos de datos por columna -------------------------------------------
# Como en el paso 1 guardamos año/valor tal cual venían del XML (texto),
# acá deberían aparecer las dos columnas como "object" (string), aunque
# lógicamente año es un entero y valor es un número decimal. Ese
# desajuste entre "tipo lógico" y "tipo real" es justamente lo que hay
# que detectar en el profiling.
print("\nTipos de datos:")
print(df.dtypes)

# --- 3. Vista de los primeros y últimos valores -------------------------------
# Sirve para "ver con los propios ojos" el formato real de los datos,
# en vez de asumirlo. Acá se nota a simple vista el problema de formato:
# "1991,0" en vez de 1991, y "118,0" en vez de 118.0 (coma en vez de
# punto decimal, convención uruguaya).
print("\nPrimeras filas:")
print(df.head())
print("\nÚltimas filas:")
print(df.tail())

# --- 4. Completitud: cuántos valores nulos tiene cada columna ----------------
print("\nNulos por columna:")
nulos = df.isnull().sum()
pct_nulos = (nulos / len(df) * 100).round(2)
completitud = pd.DataFrame({"nulos": nulos, "pct_nulos": pct_nulos})
print(completitud)

# --- 5. Duplicados exactos (fila completa idéntica a otra) ------------------
print("\nDuplicados exactos (fila completa):", df.duplicated().sum())

# --- 6. Clave primaria candidata: año ----------------------------------------
# Un indicador anual como este debería tener, como mucho, un valor por
# año. "año" es candidata natural a clave primaria: única y sin nulos.
print("\nValores únicos en año:", df["año"].nunique())
print("Total de filas:", len(df))
print(
    "año es clave primaria (único y sin nulos):",
    df["año"].is_unique and df["año"].isnull().sum() == 0,
)

# --- 7. Problemas de formato detectados (para corregir en el paso 3) --------
# Con .str.contains buscamos, dentro del texto de cada columna, el
# patrón de "coma decimal" (una coma seguida de dígitos). Como todo el
# dataset usa esa convención, el conteo debería dar igual a la cantidad
# total de filas.
print("\nFilas con 'año' en formato coma decimal (ej: '1991,0'):")
print(df["año"].str.contains(",", regex=False).sum(), "de", len(df))
print("Filas con 'valor' en formato coma decimal (ej: '118,0'):")
print(df["valor"].str.contains(",", regex=False).sum(), "de", len(df))

# --- 8. Entendiendo el negocio: qué mide este indicador ----------------------
# Este dataset no se entiende solo mirando números: hace falta leer el
# JSON de metadatos que lo acompaña (metadatos_indicador-10454.json),
# que en Datos Abiertos Uruguay viene junto al archivo de datos y explica
# qué es el indicador, quién lo calcula y en qué unidad está expresado.
#
# Resumen de esos metadatos (ver el JSON para el texto completo):
#   - Qué es: Salario Mínimo Nacional (SMN), el piso legal por debajo del
#     cual no puede estar ninguna remuneración en Uruguay (Ley 10449 /
#     Decreto 1534/969).
#   - Quién lo fija: el Ministerio de Trabajo y Seguridad Social (MTSS).
#   - Unidad: "Pesos corrientes", es decir, el valor NOMINAL de cada año,
#     SIN ajustar por inflación. Esto es clave para el análisis: no se
#     puede comparar el poder de compra real del salario de 1991 contra
#     el de 2018 usando estos números tal cual, porque los pesos de cada
#     año valen distinto (hubo inflación acumulada en el medio).
#   - Corte temporal: el valor de cada año corresponde al 1° de enero de
#     ese año (no es un promedio anual).
print(
    "\nNota de negocio: 'valor' está en pesos corrientes (nominales), "
    "no ajustados por inflación. Sirve para ver la evolución del monto "
    "legal, pero no para comparar poder de compra real entre años sin "
    "un ajuste adicional (ej: por IPC)."
)
