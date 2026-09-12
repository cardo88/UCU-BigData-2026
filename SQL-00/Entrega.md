# SQL-00 - Entrega de la práctica de SQL

Repositorio: <https://github.com/cardo88/UCU-BigData-2026.git>
Carpeta: [`SQL-00/`](.)

## Objetivo general

Este documento reúne los 7 ejercicios de la práctica de SQL: qué pedía cada
uno, qué hice para resolverlo, las decisiones que tomé cuando la consigna
dejaba margen, y evidencia de que las consultas corren y devuelven lo
esperado (capturas de pantalla para los ejercicios 1 a 4, y salida de
consola/tablas de resultados para los ejercicios 5 a 7, que trabajan con
datasets mucho más grandes de IMDb).

Cada ejercicio tiene también su propio `README.md` dentro de
`SQL-00/ejercicioN/` con el detalle completo.

## Puesta en marcha (común a todos los ejercicios)

Los ejercicios 1 a 4 usan el `initial_script` de ejemplo corriendo en PostgreSQL dentro de Docker:

```bash
cd SQL-00
docker compose up -d
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < initial_script_fixed.sql
```

El script original compartido en la webasignatura (`initial_script.sql.txt`) tiene
errores de sintaxis: a la tabla `Students` le falta una coma en una fila, y
en `Courses` un `;` está puesto antes de la última fila en vez de al final. 
Corregí esos errores en `initial_script_fixed.sql` (agregando también un `DROP TABLE IF EXISTS` al
principio para poder recrear la base las veces que hiciera falta). Con la
versión corregida quedan cargados 25 estudiantes, 15 cursos y 25
inscripciones.

Los ejercicios 5 a 7 trabajan sobre los datasets públicos de IMDb, en una
base separada (`imdb`) dentro del mismo Postgres.

---

## Ejercicio 1 — Consultas SELECT básicas

**Objetivo:** seleccionar todos los alumnos, listar solo los nombres de los
cursos, filtrar estudiantes de "Computer Science" y listar cursos de ese
departamento ordenados por créditos.

Las cuatro consultas están en [`ejercicio1/ejercicio1.sql`](ejercicio1/ejercicio1.sql).
No hay mayor complejidad acá más allá de tener claro el modelo (`Students`,
`Courses`, `Enrollments`).

**Evidencia:**

![SELECT * FROM Students](ejercicio1/Screenshot%202026-09-01%20at%2019.19.42.png)
*Consulta 1 — los 25 alumnos.*

![Nombres de cursos](ejercicio1/Screenshot%202026-09-01%20at%2019.19.55.png)
*Consulta 2 — solo `CourseName`, 15 filas.*

![Alumnos de Computer Science](ejercicio1/Screenshot%202026-09-01%20at%2019.20.07.png)
*Consulta 3 — 4 alumnos con `Major = 'Computer Science'`.*

![Cursos de Computer Science por créditos](ejercicio1/Screenshot%202026-09-01%20at%2019.20.20.png)
*Consulta 4 — cursos del departamento, ordenados de mayor a menor crédito.*

---

## Ejercicio 2 — INSERT, UPDATE, DELETE

**Objetivo:** insertar tres alumnos nuevos, actualizar el email de "Jane
Smith", renombrar el Major "Computer Science" a "Computer Science & AI",
borrar el curso "Introduction to Database Systems" y borrar el curso 103.

Script: [`ejercicio2/ejercicio2.sql`](ejercicio2/ejercicio2.sql).

El punto que requirió pensar un poco más fue el último: el curso 103
("Physics I") tiene inscripciones asociadas en `Enrollments`, y la clave
foránea es `RESTRICT` por defecto, así que intentar borrarlo directo tira
error de violación de FK. Antes de borrar el curso, borré las 8
inscripciones de ese curso en `Enrollments`. Para los tres alumnos nuevos usé
los `StudentID` 26, 27 y 28 (los del 1 al 25 ya estaban ocupados) con Majors
que ya existían en la tabla (Biology, Mathematics, Physics), evitando
`Computer Science` a propósito para no mezclarlo con el paso del renombre.

**Evidencia:**

![Insert de 3 alumnos](ejercicio2/Screenshot%202026-09-01%20at%2019.28.25.png)
*Paso 1 — alta de los alumnos 26, 27 y 28.*

![Update de email](ejercicio2/Screenshot%202026-09-01%20at%2019.29.02.png)
*Paso 2 — email de Jane Smith actualizado a `jsmith@email.com`.*

![Update de Major](ejercicio2/Screenshot%202026-09-01%20at%2019.29.28.png)
*Paso 3 — "Computer Science" → "Computer Science & AI" (4 filas afectadas).*

![Delete de curso sin inscripciones](ejercicio2/Screenshot%202026-09-01%20at%2019.29.40.png)
*Paso 4 — baja de "Introduction to Database Systems" (curso 104).*

![Delete de curso 103 con FK](ejercicio2/Screenshot%202026-09-01%20at%2019.31.58.png)
*Paso 5 — primero se borran las inscripciones del curso 103 y después el curso, para no violar la clave foránea.*

---

## Ejercicio 3 — JOINs y estudiantes sin inscripciones

**Objetivo:** listar estudiantes con sus cursos incluyendo a los que no
tienen ninguno, encontrar los estudiantes sin ninguna inscripción, y listar
solo los que sí tienen al menos una.

Script: [`ejercicio3/ejercicio3.sql`](ejercicio3/ejercicio3.sql).

Usé `LEFT JOIN` desde `Students` para la primera consulta (así no se pierden
los alumnos sin cursos), el mismo `LEFT JOIN` filtrando
`WHERE EnrollmentID IS NULL` para la segunda, e `INNER JOIN` con `DISTINCT`
para la tercera (para no repetir a un alumno con más de una inscripción).
Emily Davis y Daniel Brown resultaron ser los dos únicos alumnos sin
inscripciones.

**Evidencia:**

![Estudiantes y cursos con LEFT JOIN](ejercicio3/Screenshot%202026-09-01%20at%2019.50.12.png)
*Consulta 1 — 27 filas; Emily Davis y Daniel Brown aparecen con curso vacío.*

![Estudiantes sin inscripciones](ejercicio3/Screenshot%202026-09-01%20at%2019.51.07.png)
*Consulta 2 — los 2 alumnos sin ninguna inscripción.*

![Estudiantes con al menos una inscripción](ejercicio3/Screenshot%202026-09-01%20at%2019.51.23.png)
*Consulta 3 — 23 filas, el complemento exacto de la anterior.*

---

## Ejercicio 4 — Agregaciones con GROUP BY

**Objetivo:** alumnos por Major, promedio de créditos por curso, cantidad de
inscripciones por año y total de créditos adquiridos por estudiante.

Script: [`ejercicio4/ejercicio4.sql`](ejercicio4/ejercicio4.sql).

Para el total de créditos por estudiante encadené
`Students LEFT JOIN Enrollments LEFT JOIN Courses` y usé
`COALESCE(SUM(...), 0)`, de nuevo para que los dos alumnos sin inscripciones
no queden afuera del resultado sino que aparezcan con 0 créditos.

**Evidencia:**

![Alumnos por Major](ejercicio4/Screenshot%202026-09-01%20at%2019.56.12.png)
*Consulta 1 — cantidad de alumnos agrupada por Major.*

![Promedio de créditos](ejercicio4/Screenshot%202026-09-01%20at%2019.56.24.png)
*Consulta 2 — promedio de créditos de los 15 cursos (3.40).*

![Inscripciones por año](ejercicio4/Screenshot%202026-09-01%20at%2019.56.35.png)
*Consulta 3 — todas las inscripciones son de 2023.*

![Créditos totales por estudiante](ejercicio4/Screenshot%202026-09-01%20at%2019.56.48.png)
*Consulta 4 — total de créditos por estudiante, con Emily Davis y Daniel Brown en 0.*

---

## Ejercicio 5 — Metadata de IMDb (ejercicio conceptual)

**Objetivo:** analizar la metadata pública de IMDb y razonar sobre modelo
transaccional vs. analítico, qué conviene indexar, particionamiento y
visualización, sin escribir SQL.

Documento completo: [`ejercicio5/README.md`](ejercicio5/README.md).

Se trabajaron 3 archivos de los que publica IMDb (`datasets.imdbws.com`):
`name.basics`, `title.basics` y `title.ratings` (15.6 M, 12.8 M y 1.7 M
filas respectivamente). Con esos tres se puede modelar título, persona y
puntaje, pero no la relación actor↔película (es informacion se enucentra en otro archivo llamado `title.principals`).

Las conclusiones principales del análisis:

- Es un caso claramente **analítico** (el dataset se rehace entero cada día
  y se consulta para agregar, no hay transacciones que aplicar).
- Conviene indexar las claves (`tconst`, `nconst`), las columnas de filtro
  habituales (`titleType`, `startYear`) y las de ranking (`numVotes`,
  `averageRating`).
- El campo `genres` viene como lista separada por comas en una sola celda:
  mientras no se separe a una tabla propia, no se puede indexar de forma
  útil.
- Particionar por `titleType` tiene sentido porque el 77 % de las filas son
  `tvEpisode`, y separarlas evita que una consulta sobre películas las
  tenga que descartar una por una.
- Las decisiones de diseño cambian según el rol (analista, ingeniero de
  datos, DBA, científico de datos, modelador) aunque el modelo conceptual de
  base (entidades, claves, relaciones) sea el mismo para todos.

---

## Ejercicio 6 — Importar los datasets de IMDb

**Objetivo:** descargar los tres datasets de IMDb e importarlos a una base
relacional.

Scripts: [`ejercicio6/01_schema.sql`](ejercicio6/01_schema.sql),
[`02_transform.sql`](ejercicio6/02_transform.sql),
[`03_checks.sql`](ejercicio6/03_checks.sql), orquestados por
[`run.sh`](ejercicio6/run.sh). Detalle completo en
[`ejercicio6/README.md`](ejercicio6/README.md).

Elegí importar por código (`\copy` de `psql`) en vez del asistente de
DBeaver porque son cerca de 30 millones de filas en total y `\copy` es más
rápido y reproducible (si se ejecuta `./run.sh` de nuevo deja la base igual). La
importación se hizo en dos pasos: primero cargar todo como `text` en tablas
de *staging* (así el `COPY` nunca falla por un dato con formato raro), y
después tipar y limpiar con `INSERT ... SELECT` hacia las tablas finales
(`name`, `title`, `title_rating`), validando cada campo numérico con una
expresión regular antes de castear. Al final se crean los índices sugeridos
en el análisis del ejercicio 5.

**Resultado de la importación** (se ejecuta con `cd SQL-00/ejercicio6 && ./run.sh`):

| tabla | filas |
| --- | --- |
| `name` | 15 636 492 |
| `title` | 12 770 115 |
| `title_rating` | 1 711 899 |

Las tres cantidades coinciden entre el `COPY` crudo y el `INSERT` tipado: no
se perdió ninguna fila en la limpieza. Como chequeo adicional, la consulta
de verificación en `03_checks.sql` trae el top 10 de películas por
`num_votes`:

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

Esta tabla es la salida real de `03_checks.sql` corriendo contra la base
`imdb` ya importada, y queda como evidencia de que el `JOIN` entre `title` y
`title_rating` funciona y de que `num_votes`/`average_rating` quedaron bien
tipados (son números coherentes entre sí y ordenan correctamente de mayor a
menor).

**Evidencia:**

![run.sh](ejercicio6/Screenshot%202026-09-12%20at%2016.08.39.png)
*`./run.sh` corriendo / terminando sin errores.*

![Conteo de filas](ejercicio6/Screenshot%202026-09-12%20at%2016.08.55.png)
*Conteo de filas por tabla (`name`, `title`, `title_rating`).*

![Resultado del top 10 de películas por votos](ejercicio6/Screenshot%202026-09-12%20at%2016.09.03.png)
*Resultado del top 10 de películas por votos (`03_checks.sql`).*

---

## Ejercicio 7 — Modelo actor↔película, optimización y EXPLAIN

**Objetivo:** sobre la base `imdb` del ejercicio 6, responder películas de
un actor y su rating, el top 10 de actores por puntaje promedio, definir
optimizaciones y verificarlas con `EXPLAIN`, y agregar una consulta propia
de procesamiento intensivo.

Scripts: [`ejercicio7/01_model.sql`](ejercicio7/01_model.sql),
[`02_consultas.sql`](ejercicio7/02_consultas.sql),
[`03_explain.sql`](ejercicio7/03_explain.sql), orquestados por
[`run.sh`](ejercicio7/run.sh). Detalle completo en
[`ejercicio7/README.md`](ejercicio7/README.md).

**Limitación de partida:** no descargué `title.principals` (la tabla real de
actor↔película), así que armé la relación a partir de
`name.known_for_titles` (hasta 4 títulos por persona, aproximando "actor"
con `primary_profession LIKE '%actor%'/'%actress%'`). Esto lo dejo explícito
porque sesga los resultados hacia los títulos más famosos de cada persona.

**Optimización:** identifiqué y medí varias mejoras, entre ellas:

- Un índice sobre `name(primary_name)` bajó la consulta 1 de **8 262 ms a
  0,8 ms** (de recorrer 15 millones de filas a un `Index Scan` directo).
- Una vista materializada (`mv_actor_movie_rating`) con el ranking ya
  agregado bajó la consulta 2 (top 10 actores) de **~77 s a 47 ms**.
- Verifiqué con `EXPLAIN (ANALYZE, BUFFERS)` que los planes realmente usan
  los índices creados, comparando además contra el plan forzado sin
  índices (`SET enable_indexscan = off`) para ver la diferencia real.

**Consulta propia:** "joyas ocultas" por género — películas con
`average_rating >= 8.0` pero pocos votos (entre 2 000 y 25 000), rankeadas
por género con `ROW_NUMBER() OVER (PARTITION BY genero ...)`. Da 1 924 filas
/ 892 películas distintas y ejecuta en ~150 ms apoyándose en el índice de
`num_votes`. El valor para alguien que consume películas es encontrar buenas
películas que todavía no son masivas, lo contrario de un ranking por
popularidad.

**Evidencia:**

![Paso 1/3 - modelo](ejercicio7/Screenshot%202026-09-12%20at%2019.31.10.png)
*Paso 1/3 — creación de la tabla puente `name_known_for` (25 319 511 filas, 15 borradas por `tconst` inexistente) e índices.*

![Paso 2/3 - consultas y vista materializada](ejercicio7/Screenshot%202026-09-12%20at%2019.31.34.png)
*Paso 2/3 — consulta 1 (películas de Tom Hanks), consulta 2 sin y con filtro de votos (se ve el sesgo hacia la trilogía de El Señor de los Anillos), y creación de la vista materializada (2 347 935 filas).*

![Consulta propia - joyas ocultas](ejercicio7/Screenshot%202026-09-12%20at%2019.31.41.png)
*Consulta propia — "joyas ocultas" por género (ejemplo del género Action).*

![EXPLAIN consulta 1 con índices](ejercicio7/Screenshot%202026-09-12%20at%2019.31.54.png)
*`EXPLAIN` de la consulta 1 con índices — todo por `Index Scan`, Execution Time: 2.222 ms.*

![EXPLAIN consulta 1 sin índices](ejercicio7/Screenshot%202026-09-12%20at%2019.32.03.png)
*`EXPLAIN` de la consulta 1 forzando sin índices (el "antes") — `Seq Scan` sobre las tablas, Execution Time: 6 985.870 ms.*

![EXPLAIN consulta 2 a mano](ejercicio7/Screenshot%202026-09-12%20at%2019.32.21.png)
*`EXPLAIN` de la consulta 2 "a mano", sin la vista materializada — sort a disco, Execution Time: 36 698.848 ms.*

![EXPLAIN consulta 2 con vista materializada](ejercicio7/Screenshot%202026-09-12%20at%2019.32.33.png)
*`EXPLAIN` de la consulta 2 usando la vista materializada (el "después") — `Index Scan` directo, Execution Time: 112.518 ms.*

---

## Conclusiones

Los ejercicios 1 a 4 cubren lo básico de SQL (`SELECT`, `INSERT/UPDATE/DELETE`,
`JOIN`, `GROUP BY`) sobre una base chica y controlada, donde el desafío
estuvo en corregir el script inicial y manejar bien los casos de `NULL`
(alumnos sin cursos) y la restricción de clave foránea al borrar. 

Los
ejercicios 5 a 7 escalan esas mismas ideas a un dataset real de decenas de
millones de filas (IMDb), donde recién ahí se nota la diferencia entre tener
o no tener el índice correcto: la misma consulta pasó de más de un minuto a
menos de 50 milisegundos según cómo estuviera modelada y optimizada.

## Uso de IA como apoyo

Para estos ejercicios conté con el apoyo de IA (Claude, Anthropic).
