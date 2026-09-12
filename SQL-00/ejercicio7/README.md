# SQL-00 - Ejercicio 7

## Objetivo

Sobre la base `imdb` del [ejercicio 6](../ejercicio6/README.md), modelar los
datos para responder:

1. Películas de un actor determinado y sus ratings.
2. Top 10 de actores con mayor puntaje promedio de películas.
3. Definir acciones de optimización, explicarlas y por qué mejoran.
4. Usar `EXPLAIN` para corroborar que se usan los índices.
5. Una consulta extra de procesamiento intensivo, con valor para quien
   consume películas.

## Limitación de partida

La relación **actor ↔ película** vive en `title.principals`, que **no** se
descargó. Se deriva entonces de `name.known_for_titles` (lista de hasta 4
`tconst` por persona). Implicancias:

- Son los títulos "por los que se conoce" a la persona, **no** su filmografía
  completa.
- No distingue el rol (actuó / dirigió / produjo). Se aproxima "actor" con
  `primary_profession LIKE '%actor%' OR '%actress%'`.
- Los promedios quedan sesgados hacia las películas más famosas de cada
  persona (que suelen ser las mejor puntuadas).

Con `title.principals` importado, el modelo y las consultas serían los mismos
cambiando la tabla puente por una tabla `title_principals(tconst, nconst,
category, characters)` filtrada por `category IN ('actor','actress')`.

## Archivos

| Archivo | Rol |
| --- | --- |
| `01_model.sql` | Tabla puente `name_known_for` (split de `known_for_titles`) + índices. |
| `02_consultas.sql` | Las 3 consultas + variante 2b + vista materializada. |
| `03_explain.sql` | `EXPLAIN (ANALYZE, BUFFERS)` de cada consulta, con y sin índices. |
| `run.sh` | Corre los 3 pasos en orden. |

## Cómo ejecutar

```bash
cd SQL-00/ejercicio7
./run.sh
```

`01_model.sql` tarda ~4 min (arma una tabla puente de 25 M filas).
`02_consultas.sql` corre la consulta 2 "a mano" dos veces (~77 s cada una) a
propósito, para comparar contra la vista materializada.

## 1. Modelo

```
name_known_for(nconst, tconst)          -- PK (nconst, tconst)
   nconst  -> name(nconst)
   tconst  -> title(tconst)
```

Se construye desarmando la lista `name.known_for_titles`:

```sql
CREATE TABLE name_known_for AS
SELECT n.nconst, trim(kf.tconst) AS tconst
FROM name n
CROSS JOIN LATERAL unnest(string_to_array(n.known_for_titles, ',')) AS kf(tconst)
WHERE n.known_for_titles IS NOT NULL;
```

Resultado: **25 319 496** filas (se borran 15 que apuntaban a `tconst`
inexistentes). Índices creados:

| Índice | Sobre | Para |
| --- | --- | --- |
| PK `(nconst, tconst)` | `name_known_for` | join por `nconst`. |
| `ix_nkf_tconst` | `name_known_for(tconst)` | join por `tconst`. |
| `ix_name_primary_name` | `name(primary_name)` | buscar el actor por nombre (consulta 1). |
| `ix_name_actor` (parcial) | `name(nconst) WHERE primary_profession LIKE '%actor%'/'%actress%'` | filtro de rol (consulta 2). |

`ix_rating_num_votes`, `ix_rating_avg`, `ix_title_type`, `ix_title_start_year`
ya venían del ejercicio 6.

## 2. Consulta 1 — películas de un actor y sus ratings

```sql
SELECT n.nconst, n.primary_name, t.primary_title, t.start_year,
       r.average_rating, r.num_votes
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst
LEFT JOIN title_rating r ON r.tconst = t.tconst
WHERE n.primary_name = 'Tom Hanks'
  AND t.title_type = 'movie'
ORDER BY r.num_votes DESC NULLS LAST;
```

Resultado (nota: `primary_name` no es único; para un actor puntual conviene
`WHERE n.nconst = 'nm0000158'`):

| primary_title | start_year | average_rating | num_votes |
| --- | --- | --- | --- |
| Forrest Gump | 1994 | 8.8 | 2 532 406 |
| Cast Away | 2000 | 7.8 | 696 148 |
| Philadelphia | 1993 | 7.7 | 276 699 |
| Big | 1988 | 7.3 | 263 378 |

Solo 4 películas porque `known_for_titles` guarda como mucho 4 títulos.

## 3. Consulta 2 — top 10 actores por puntaje promedio

```sql
SELECT n.nconst, n.primary_name, COUNT(*) AS peliculas,
       ROUND(AVG(r.average_rating),2) AS rating_promedio,
       SUM(r.num_votes) AS votos_totales
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst AND t.title_type = 'movie'
JOIN title_rating r    ON r.tconst  = t.tconst
WHERE n.primary_profession LIKE '%actor%' OR n.primary_profession LIKE '%actress%'
GROUP BY n.nconst, n.primary_name
HAVING COUNT(*) >= 3
ORDER BY rating_promedio DESC, votos_totales DESC
LIMIT 10;
```

Con `HAVING COUNT(*) >= 3` solo, el top se llena de actores con 3 títulos
oscuros votados por decenas de personas con 9.5. La **variante 2b** agrega
`AND r.num_votes >= 50000`: ahí el top pasa a ser gente "conocida por" la
trilogía de *El Señor de los Anillos* (promedio 8.90, ~6.4 M votos sumados),
que es el efecto esperable de `known_for_titles`.

## 4. Acciones de optimización y por qué mejoran

| # | Acción | Por qué mejora |
| --- | --- | --- |
| 1 | **Índice `ix_name_primary_name`** en `name(primary_name)`. | La consulta 1 busca por nombre. Sin índice, `name` (15 M filas) se recorre entero (*Seq Scan*). Con índice, va directo a la fila. Medido: **8 262 ms → 0,8 ms**. |
| 2 | **Índices en la tabla puente** (`PK(nconst,tconst)` + `ix_nkf_tconst`). | Los `JOIN` de `name_known_for` con `name` y con `title` se resuelven siguiendo el índice fila por fila, en vez de cargar y hashear 25 M filas. |
| 3 | **Índice parcial `ix_name_actor`**. | Solo indexa las filas de actores/actrices (~350 k de 15 M). Es mucho más chico y evita evaluar el `LIKE` sobre toda la tabla. El plan de la consulta 2 lo usa. |
| 4 | **Índices de rating** (`ix_rating_num_votes`, `ix_rating_avg`). | La consulta 3 filtra por rango de votos; con el índice lee solo ese tramo (~56 k filas) en vez de las 1,7 M. |
| 5 | **Cambiar `LIKE '%actor%'` por una columna `is_actor boolean`** con índice normal. | Un `LIKE` que empieza con comodín (`%...`) no puede usar un índice común: obliga a mirar cada valor. Una bandera booleana precalculada sí se indexa y se filtra al instante. |
| 6 | **Vista materializada `mv_actor_movie_rating`**. | La consulta 2 agrupa millones de filas cada vez. La vista guarda el resultado ya agregado (2,35 M filas, una por actor) con un índice ordenado por `rating_promedio`. El top 10 pasa a leer 10 filas por índice. Medido: **76 687 ms → 47 ms**. Costo: hay que `REFRESH` cuando cambian los datos → encaja con el refresco diario del dataset. |
| 7 | **Subir `work_mem`**. | En el plan de la consulta 2 los ordenamientos se van a disco (`external merge Disk: 55 MB`). Con más memoria de trabajo, ordena en RAM. Es configuración, no estructura. |
| 8 | **Normalizar `genres`** a una tabla `title_genre`. | La consulta 3 desarma la lista de géneros con `unnest` en cada corrida. Con una tabla `title_genre(tconst, genre)` indexada, el filtro por género es un `JOIN` directo. |
| 9 | **`shm_size: 1gb`** en `docker-compose.yml`. | Con los 64 MB por defecto de `/dev/shm`, las consultas en paralelo fallan con *"No space left on device"*. Con 1 GB, PostgreSQL puede lanzar los *workers* y repartir el trabajo. |

Orden recomendado: primero cargar los datos, después crear los índices (es más
rápido que mantenerlos durante los `INSERT`), y por último `ANALYZE` para que
el planificador tenga estadísticas frescas.

## 5. Corroborar el uso de índices con EXPLAIN

### Consulta 1 — con índice (plan real)

```
Sort  (actual time=0.75..0.75 rows=4)
  ->  Nested Loop Left Join
        ->  Nested Loop
              ->  Nested Loop
                    ->  Index Scan using ix_name_primary_name on name n   <-- usa el índice de nombre
                          Index Cond: (primary_name = 'Tom Hanks')
                    ->  Index Only Scan using name_known_for_pkey on kf    <-- usa la PK de la puente
              ->  Index Scan using title_pkey on title t
        ->  Index Scan using title_rating_pkey on title_rating r
Execution Time: 0.79 ms
```

Todos los accesos son por índice.

### Consulta 1 — forzando sin índices (para ver el "antes")

`SET enable_indexscan = off; SET enable_bitmapscan = off;`

```
Parallel Hash Join
  ->  Parallel Seq Scan on name_known_for kf   (25 M filas)
  ->  Parallel Seq Scan on name n              Rows Removed by Filter: 5 212 164
  ->  Parallel Seq Scan on title t             Rows Removed by Filter: 4 004 607
Execution Time: 8 262 ms
```

Sin índices el motor recorre las tablas enteras: **~10 000× más lento**.

### Consulta 2 — agregación "a mano"

```
Limit
  ->  Sort  (top-N)
        ->  Finalize GroupAggregate   Filter: (count(*) >= 3)
              ->  Gather Merge (Workers: 2)
                    ->  Sort  Sort Method: external merge  Disk: 55 MB   <-- se va a disco
                          ->  Nested Loop  (rows=1 188 716, loops=3)
                                ->  Parallel Hash Join (kf.tconst = t.tconst)
                                      ->  Parallel Seq Scan on name_known_for
                                      ->  Parallel Hash Join (r.tconst = t.tconst)
                                            ->  Parallel Seq Scan on title_rating
                                            ->  Parallel Bitmap Heap Scan on title
                                                  ->  Bitmap Index Scan on ix_title_type   <-- usa índice de tipo
                                ->  Index Scan using ix_name_actor on name n                <-- usa índice parcial
                                      (loops = 8 299 321)
Execution Time: 76 687 ms
```

Se ven usados `ix_title_type` y `ix_name_actor`, pero el plan es caro igual:
8,3 millones de vueltas del *nested loop* y ordenamientos que van a disco.

### Consulta 2 — con la vista materializada

```
Limit  (actual time=6.3..46.7 rows=10)
  ->  Index Scan using ix_mv_actor_rating on mv_actor_movie_rating
        Filter: (peliculas >= 3)
Execution Time: 47 ms
```

Un solo *Index Scan* sobre la vista ordenada. **De ~77 s a ~0,05 s.**

### Consulta 3

```
Nested Loop
  ->  Gather (Workers: 2)
        ->  Nested Loop
              ->  Parallel Bitmap Heap Scan on title_rating r
                    Recheck Cond: (num_votes >= 2000 AND num_votes <= 25000)
                    ->  Bitmap Index Scan on ix_rating_num_votes            <-- usa el índice de votos
              ->  Index Scan using title_pkey on title t
  ->  Function Scan on unnest g
Execution Time: 147 ms
```

Filtra el rango de votos con `ix_rating_num_votes` en vez de recorrer las
1,7 M filas de `title_rating`.

## 6. Consulta 3 (intensiva) — "joyas ocultas" por género

Películas con puntaje alto (`average_rating >= 8.0`) pero **pocos votos**
(entre 2 000 y 25 000): excelentes y todavía poco vistas. Rankeadas por
género.

```sql
SELECT g.genero, t.primary_title, t.start_year, r.average_rating, r.num_votes,
       ROW_NUMBER() OVER (PARTITION BY g.genero
                          ORDER BY r.average_rating DESC, r.num_votes DESC) AS puesto
FROM title_rating r
JOIN title t ON t.tconst = r.tconst
CROSS JOIN LATERAL unnest(string_to_array(t.genres, ',')) AS g(genero)
WHERE t.title_type = 'movie'
  AND t.genres IS NOT NULL
  AND t.start_year <= EXTRACT(YEAR FROM CURRENT_DATE)::int
  AND r.average_rating >= 8.0
  AND r.num_votes BETWEEN 2000 AND 25000
ORDER BY g.genero, puesto;
```

**Valor para el consumidor**: es lo contrario del "top por popularidad".
Devuelve recomendaciones que no aparecen en las listas más vistas —
**1 924 filas / 892 películas** distintas repartidas por género. Corre en
~150 ms usando `ix_rating_num_votes`.

Es "intensiva" porque cruza `title_rating` (1,7 M) con `title` y además
desarma la lista de géneros de cada película (`unnest`), multiplicando filas.

Sesgo observado: muchas películas de cine regional (sobre todo indio), que
tienen puntajes muy altos de una comunidad chica de votantes. Se podría
acotar por región agregando `title.akas`.

## Nota sobre el estado de la base

Este ejercicio **agrega** objetos a la base `imdb` (`name_known_for`,
`mv_actor_movie_rating` e índices). No modifica `name`, `title` ni
`title_rating`. Para volver a foja cero se puede recrear `imdb` con
`../ejercicio6/run.sh`.
