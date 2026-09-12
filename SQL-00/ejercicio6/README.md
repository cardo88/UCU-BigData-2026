# SQL-00 - Ejercicio 6

## Objetivo

- Descargar los datasets de personas, títulos y puntajes de IMDb.
- Importarlos a una base de datos relacional.
- Se puede hacer con el asistente de importación de la herramienta (DBeaver) o
  con código.

## Qué se hizo acá

Los 3 `.tsv.gz` ya estaban descargados en [`../imdbws/`](../imdbws) (ejercicio
5). Se importan a una **base nueva `imdb`** dentro del mismo PostgreSQL del
`docker-compose` de SQL-00, con un script de `psql` (`\copy`). La base
`bigdata_db` de los ejercicios 1–4 **no se toca**.

Se eligió la vía por código (no el asistente de DBeaver) porque son ~30 M de
filas y el `\copy` de PostgreSQL es la forma más rápida y reproducible. El
resultado es el mismo: las 3 tablas quedan en una base relacional, accesibles
también desde DBeaver conectándose a `localhost:5432 / imdb`.

## Archivos

| Archivo | Rol |
| --- | --- |
| `01_schema.sql` | Tablas de *staging* (`stg_*`), todas las columnas `text`. |
| `02_transform.sql` | Tablas finales tipadas (`name`, `title`, `title_rating`) + índices; borra el staging. |
| `03_checks.sql` | Consultas de verificación (conteos, top 10). |
| `run.sh` | Orquesta todo: crea la base, carga y transforma. |

## Cómo ejecutar

Con el contenedor `bigdata-postgres` corriendo (`docker compose up -d` desde
`SQL-00/`):

```bash
cd SQL-00/ejercicio6
./run.sh
```

Tarda unos minutos (la carga de `name.basics` es la más lenta). Al terminar:

```bash
docker exec -it bigdata-postgres psql -U bigdata -d imdb
```

Desde **DBeaver**: nueva conexión PostgreSQL a `localhost` : `5432`, base
`imdb`, usuario/clave `bigdata` / `bigdata`.

## Cómo se importa (decisiones)

### 1. Staging en `text`, después tipar

Se cargan primero tablas `stg_*` con **todas las columnas `text`**. Así el
`COPY` nunca falla por un valor que no castea. El tipado y la limpieza se hacen
en `02_transform.sql` con `INSERT ... SELECT`.

### 2. Opciones del `\copy`

```
\copy stg_title_basics FROM STDIN WITH
  (FORMAT csv, DELIMITER E'\t', QUOTE E'\b', ESCAPE E'\b', NULL '\N', HEADER true)
```

- `FORMAT csv` + `DELIMITER E'\t'`: archivo separado por tabuladores.
- `QUOTE E'\b'` y `ESCAPE E'\b'` (backspace): un carácter que **no aparece** en
  los datos. Con esto `COPY` no interpreta comillas ni `\` dentro de los
  títulos (p. ej. `Rock 'n' Roll`, rutas con `\`), que con `FORMAT text`
  romperían la importación.
- `NULL '\N'`: el nulo de IMDb (la cadena literal `\N`) entra como `NULL` real.
- `HEADER true`: saltea la fila de encabezados.
- El archivo se descomprime al vuelo: `gzcat archivo.tsv.gz | psql ... \copy`.

### 3. Tipado y limpieza (`02_transform.sql`)

| Campo original | Queda como | Regla |
| --- | --- | --- |
| `startYear`, `endYear`, `birthYear`, `deathYear` | `smallint` | solo si son dígitos, si no `NULL`. |
| `runtimeMinutes` | `integer` | ídem (hay valores > 32767). |
| `isAdult` | `boolean` | `'1'`→true, `'0'`→false, otro→`NULL`. |
| `averageRating` | `numeric(3,1)` | valida formato numérico. |
| `numVotes` | `integer` | solo dígitos. |
| `genres`, `primaryProfession`, `knownForTitles` | `text` | se dejan como lista separada por coma (normalizar queda para más adelante). |

El chequeo con expresión regular (`~ '^[0-9]+$'`) evita que una fila con dato
sucio corte toda la carga.

### 4. Modelo resultante

```
name(nconst PK, primary_name, birth_year, death_year,
     primary_profession, known_for_titles)

title(tconst PK, title_type, primary_title, original_title,
      is_adult, start_year, end_year, runtime_minutes, genres)

title_rating(tconst PK -> title.tconst, average_rating, num_votes)
```

`title_rating.tconst` es clave foránea a `title`. Se cargan solo las filas de
rating cuyo `tconst` existe en `title` (`WHERE EXISTS ...`), para que la FK no
falle si hubiera un puntaje sin título.

### 5. Índices

Los sugeridos en el análisis del ejercicio 5, sobre las columnas por las que
se filtra o rankea:

- `title(title_type)` — filtrar por películas/series.
- `title(start_year)` — filtrar por año / rango.
- `title_rating(num_votes)` y `title_rating(average_rating)` — rankings.

Las PK (`tconst`, `nconst`) ya crean su índice. Los índices se crean **después**
de cargar, que es más rápido que mantenerlos durante el `INSERT`.

## Resultado de la importación

### Conteo por tabla

| tabla | filas |
| --- | --- |
| `name` | 15 636 492 |
| `title` | 12 770 115 |
| `title_rating` | 1 711 899 |

Las 3 filas de `COPY` coinciden con las de los `INSERT` tipados: no se perdió
ni descartó ninguna fila. Las 1 711 899 filas de rating entraron todas (todos
los `tconst` de puntaje existen en `title`, la FK no rechazó nada).

### Títulos por tipo

| title_type | cantidad |
| --- | --- |
| tvEpisode | 9 872 639 |
| short | 1 155 771 |
| movie | 756 293 |
| video | 330 921 |
| tvSeries | 304 793 |
| tvMovie | 155 992 |
| tvMiniSeries | 72 713 |
| tvSpecial | 59 837 |
| videoGame | 50 104 |
| tvShort | 11 051 |
| tvPilot | 1 |

### Títulos con puntaje

1 711 899 títulos con rating = **13.4 %** del total.

### Top 10 películas por votos

| primary_title | start_year | average_rating | num_votes |
| --- | --- | --- | --- |
| The Shawshank Redemption | 1994 | 9.3 | 3 235 135 |
| The Dark Knight | 2008 | 9.1 | 3 223 561 |
| Inception | 2010 | 8.8 | 2 865 804 |
| Fight Club | 1999 | 8.8 | 2 658 342 |
| Interstellar | 2014 | 8.7 | 2 602 917 |
| Forrest Gump | 1994 | 8.8 | 2 532 406 |
| Pulp Fiction | 1994 | 8.8 | 2 465 441 |
| The Matrix | 1999 | 8.7 | 2 276 089 |
| The Godfather | 1972 | 9.2 | 2 253 879 |
| The Lord of the Rings: The Fellowship of the Ring | 2001 | 8.9 | 2 234 846 |

La importación completa (carga + tipado + índices) tardó del orden de un par de
minutos.
