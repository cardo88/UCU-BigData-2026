#!/usr/bin/env bash
# ============================================================
# Ejercicio 6 - Importar los datasets de IMDb a una base nueva
# 'imdb' en el PostgreSQL del docker-compose de SQL-00.
# NO toca 'bigdata_db' (ejercicios 1-4).
#
# Uso:  ./run.sh        (desde SQL-00/ejercicio6/)
# Requisitos: contenedor 'bigdata-postgres' corriendo y los
#             .tsv.gz en SQL-00/imdbws/
# ============================================================
set -euo pipefail

CT=bigdata-postgres
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="$(cd "$HERE/.." && pwd)/imdbws"
PSQL="docker exec -i $CT psql -U bigdata -v ON_ERROR_STOP=1"

echo ">> 1/5  Creando base 'imdb' (drop + create)"
$PSQL -d postgres -c "DROP DATABASE IF EXISTS imdb;" -c "CREATE DATABASE imdb;"

echo ">> 2/5  Tablas de staging"
$PSQL -d imdb < "$HERE/01_schema.sql"

# Carga con FORMAT csv + QUOTE/ESCAPE en un caracter que no aparece
# (backspace) para que NO interprete comillas ni backslashes de los
# títulos; NULL '\N' convierte el nulo de IMDb.
load () {
  local file="$1" table="$2"
  echo ">> 3/5  Cargando $table  (<- $file)"
  gzcat "$DATA/$file" | $PSQL -d imdb -c \
    "\copy $table FROM STDIN WITH (FORMAT csv, DELIMITER E'\t', QUOTE E'\b', ESCAPE E'\b', NULL '\N', HEADER true)"
}
load name.basics.tsv.gz   stg_name_basics
load title.basics.tsv.gz  stg_title_basics
load title.ratings.tsv.gz stg_title_ratings

echo ">> 4/5  Tipando tablas finales + índices"
$PSQL -d imdb < "$HERE/02_transform.sql"

echo ">> 5/5  Verificaciones"
$PSQL -d imdb < "$HERE/03_checks.sql"

echo ">> Listo. Conectarse con:  docker exec -it $CT psql -U bigdata -d imdb"
