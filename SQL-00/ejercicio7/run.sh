#!/usr/bin/env bash
# ============================================================
# Ejercicio 7 - Modelo + consultas + planes sobre la base 'imdb'.
# Requiere el ejercicio 6 ya corrido (base 'imdb' con name/title/
# title_rating) y el contenedor 'bigdata-postgres' arriba.
#
# Uso:  ./run.sh            (desde SQL-00/ejercicio7/)
# ============================================================
set -euo pipefail
CT=bigdata-postgres
HERE="$(cd "$(dirname "$0")" && pwd)"
PSQL="docker exec -i $CT psql -U bigdata -d imdb -v ON_ERROR_STOP=1 -P pager=off"

echo ">> 1/3  Modelo (tabla puente name_known_for + índices)  [~4 min]"
$PSQL -f - < "$HERE/01_model.sql"

echo ">> 2/3  Consultas + vista materializada  [~3 min: Q2 se corre 'a mano']"
$PSQL -f - < "$HERE/02_consultas.sql"

echo ">> 3/3  Planes EXPLAIN (uso de índices)"
$PSQL -f - < "$HERE/03_explain.sql"

echo ">> Listo."
