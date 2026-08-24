# Actividad 01 - name.basics (IMDb)

Trabajo sobre el dataset `name.basics` de IMDb (listado de personas: actores,
directores, etc.). El objetivo de la actividad es:

1. Almacenar el dato localmente en formato Parquet.
2. Entender el dataset: hacer profiling y corregir los errores encontrados.
3. Guardar el dato ya limpio en otra estructura (otro Parquet, separado del crudo).

## Cómo correr esto

Hace falta el venv del repo activado (ver `doc/preparar_venv.md`), con
`pandas` y `pyarrow` instalados. Todos los comandos se corren **parado en la
raíz del repo** (`UCU-BigData-2026/`), no desde adentro de `Actividad01/`,
porque los scripts usan rutas relativas a la raíz:

```bash
source .venv/bin/activate
python Actividad01/01_ingesta.py
python Actividad01/02_profiling.py
python Actividad01/03_limpieza.py
```

Hay que correrlos en ese orden, porque cada uno depende del archivo que
generó el anterior.

## Los scripts

| Script | Qué hace | Entrada | Salida |
|---|---|---|---|
| `01_ingesta.py` | Lee el TSV comprimido original y lo guarda tal cual en Parquet (sin corregir nada) | `name.basics.tsv.gz` | `name_basics_raw.parquet` |
| `02_profiling.py` | Analiza el Parquet crudo: filas/columnas, tipos, nulos, duplicados, clave primaria | `name_basics_raw.parquet` | solo imprime en consola, no genera archivos |
| `03_limpieza.py` | Corrige los problemas detectados en el profiling y guarda un Parquet nuevo | `name_basics_raw.parquet` | `name_basics_clean.parquet` |

Cada script tiene comentarios en español explicando línea por línea qué hace
y por qué. Están pensados para poder volver a leerlos más adelante sin tener
que recordar el contexto.

Los archivos `.parquet` generados (`name_basics_raw.parquet` y
`name_basics_clean.parquet`) no están versionados en git por su tamaño
(cientos de MB) — se regeneran corriendo los scripts.

## Sobre el archivo original

IMDb distribuye este dataset comprimido con gzip: `name.basics.tsv.gz`.
`01_ingesta.py` lo lee directamente comprimido, usando el parámetro
`compression="gzip"` de pandas, que lo descomprime "al vuelo" mientras lo
va leyendo — no hace falta descomprimirlo a mano antes.

Ojo si descargás el archivo de nuevo: algunos navegadores (Safari, por
ejemplo) descomprimen automáticamente los `.gz` al descargarlos, dejando
un `.tsv` suelto en vez del `.tsv.gz`. Si eso pasa, hay que volver a
comprimirlo (o descargarlo de una forma que no lo descomprima) para que
el script lo pueda usar tal como está pensado.

## Resultado del profiling (paso 2)

Corrida sobre las **15.573.835 filas** y **6 columnas** del dataset
(el número exacto de filas varía un poco entre descargas porque IMDb
actualiza este dataset todos los días):

| Columna | Tipo original | Nulos | % Nulos |
|---|---|---|---|
| `nconst` | object (texto) | 0 | 0.00% |
| `primaryName` | object (texto) | 100 | 0.00% |
| `birthYear` | float64 | 14.894.435 | 95.64% |
| `deathYear` | float64 | 15.311.901 | 98.32% |
| `primaryProfession` | object (texto) | 3.153.951 | 20.25% |
| `knownForTitles` | object (texto) | 1.879.546 | 12.07% |

Otros hallazgos:

- **Duplicados de fila completa**: 0.
- **Clave primaria**: `nconst` es válida como clave primaria — tiene
  tantos valores únicos como filas, y ningún nulo. Es el identificador
  de persona de IMDb (ej: `nm0000001`).

### Por qué `object` no siempre es lo mismo que "string"

En pandas, `object` es un tipo genérico: significa "cada celda es un
objeto de Python cualquiera", que en la práctica casi siempre es un
`str`, pero pandas no lo valida ni lo garantiza. Pandas no tiene (por
defecto) un tipo específico para texto como sí tiene para números
(`int64`, `float64`), así que todo texto cae en `object`.

## Problemas detectados y corregidos (paso 3)

| # | Problema | Corrección aplicada |
|---|---|---|
| 1 | `birthYear` y `deathYear` quedaron como `float64` (ej: `1954.0`) por los nulos, pero son años (enteros) | Convertidos a `Int64`, el entero "nullable" de pandas, que admite nulos sin forzar a float |
| 2 | `primaryProfession` y `knownForTitles` son un string con varios valores separados por coma (ej: `"actor,producer,writer"`), no una lista real | Convertidos a listas de Python (`["actor", "producer", "writer"]`), tipo `list` nativo de Parquet |
| 3 | `primaryName` tiene 100 filas sin valor | Esas 100 filas (0.00% del total) se descartan, porque sin nombre no aportan al análisis |
| 4 | — | `nconst` ya era válido como clave primaria, no requirió corrección |
| 5 | — | No había duplicados de fila completa, no hizo falta deduplicar |

El resultado (`name_basics_clean.parquet`) queda en un archivo **separado**
del crudo (`name_basics_raw.parquet`), para mantener trazabilidad entre el
dato "tal cual llegó" y el dato "curado".
