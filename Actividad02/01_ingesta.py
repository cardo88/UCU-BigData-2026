# =============================================================================
# PASO 1 - INGESTA: leer el dataset original y guardarlo localmente en Parquet
# =============================================================================
#
# Qué hace este script:
#   1. Lee el archivo original "10454_salario_minimo_nacional_-smn-.xml"
#      (indicador "Salario Mínimo Nacional" de Datos Abiertos Uruguay, un
#      año y un valor por fila).
#   2. Lo guarda tal cual (sin corregir nada todavía) en formato Parquet.
#
# Sobre el archivo original:
#   A pesar de que el nombre del archivo de metadatos es un ".json", el
#   dato en sí (las filas con año/valor) viene en un ".xml", no en un CSV.
#   El JSON (metadatos_indicador-10454.json) no tiene los datos: describe
#   el indicador (qué mide, quién lo publica, en qué unidad, etc.), así
#   que lo usamos como documentación, no como fuente de datos.
#
#   El XML tiene esta forma (un <Fila> por año):
#     <Filas>
#       <Fila><año>1991,0</año> <valor>118,0</valor></Fila>
#       ...
#     </Filas>
#
#   Dos cosas raras que se ven ya en el XML crudo, a propósito NO las
#   corregimos en este paso (eso es trabajo del profiling y la limpieza):
#     - El año viene como "1991,0" (con coma y un ",0" de más), no como
#       el entero 1991. Es porque el sistema que exportó el dato trató
#       la columna "año" como un número decimal en vez de un entero.
#     - Los valores usan COMA como separador decimal ("118,0"), que es
#       la convención uruguaya/rioplatense, no el punto ("118.0") que
#       usan Python/pandas por defecto. Si se leyera "118,0" como float
#       directamente, fallaría o daría un resultado incorrecto.
#
# Por qué Parquet y no dejar el XML:
#   - Parquet es un formato columnar: guarda cada columna por separado,
#     no fila por fila como el XML. Es mucho más rápido de leer y ocupa
#     menos espacio en disco.
#   - Guarda el tipo de dato de cada columna, así no hay que "adivinar"
#     tipos cada vez que se lee el archivo.
#   - En este dataset en particular (28 filas) el ahorro de espacio no
#     se nota, pero practicamos el mismo flujo que se usaría con un
#     dataset de millones de filas (ver Actividad01).
#
# Cómo correr este script (parado en la raíz del repo, con el venv activado):
#   python Actividad02/01_ingesta.py
# =============================================================================

import xml.etree.ElementTree as ET

import pandas as pd

# --- Rutas de entrada y salida -----------------------------------------------
# Rutas relativas a la raíz del repo. Si corrés el script desde adentro de
# Actividad02/, estas rutas van a fallar. Por eso siempre hay que pararse
# en la raíz del repo.
RUTA_ENTRADA = "Actividad02/10454_salario_minimo_nacional_-smn-.xml"
RUTA_SALIDA_PARQUET = "Actividad02/salario_minimo_raw.parquet"

# --- 1. Lectura y parseo del XML ---------------------------------------------
# ElementTree es la librería estándar de Python para leer XML (no hace
# falta instalar nada extra). tree.getroot() da el nodo raíz (<Filas>);
# iterar sobre él da cada <Fila> hija.
print("Leyendo el archivo XML original...")
tree = ET.parse(RUTA_ENTRADA)
raiz = tree.getroot()

# Armamos una lista de diccionarios, uno por <Fila>, leyendo el texto TAL
# CUAL viene en el XML (como string), sin convertir ni corregir nada
# todavía. Esto es a propósito: el paso de ingesta solo trae el dato
# crudo a Parquet, no lo corrige (eso es tarea de 02_profiling.py y
# 03_limpieza.py).
filas = []
for fila in raiz:
    filas.append(
        {
            "año": fila.find("año").text,
            "valor": fila.find("valor").text,
        }
    )

df = pd.DataFrame(filas)
print(f"Archivo leído. Filas: {len(df):,} | Columnas: {df.shape[1]}")

# --- 2. Guardado en formato Parquet ------------------------------------------
# engine="pyarrow"       -> librería que sabe escribir/leer Parquet.
# compression="snappy"   -> algoritmo de compresión rápido y liviano, es el
#                            estándar por defecto en el ecosistema Parquet.
#
# Importante: este parquet es el dato "crudo" (raw), con año y valor
# todavía como texto (strings), tal cual vinieron del XML. La conversión
# a tipos numéricos correctos se hace en el paso 3 (03_limpieza.py).
df.to_parquet(RUTA_SALIDA_PARQUET, engine="pyarrow", compression="snappy")

print(f"Guardado como Parquet en: {RUTA_SALIDA_PARQUET}")
