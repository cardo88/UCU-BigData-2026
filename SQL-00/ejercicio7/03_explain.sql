-- ============================================================
-- Ejercicio 7 - Paso 3: EXPLAIN para corroborar el uso de índices
-- Correr contra la base imdb con el modelo (01) y la vista (02) creados.
-- ============================================================

-- ------------------------------------------------------------
-- Q1 - plan real: debe verse "Index Scan using ix_name_primary_name"
-- y luego Index Scan por las PK de name_known_for / title / title_rating
-- ------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT n.nconst, n.primary_name, t.primary_title, t.start_year, r.average_rating, r.num_votes
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst
LEFT JOIN title_rating r ON r.tconst = t.tconst
WHERE n.primary_name = 'Tom Hanks'
  AND t.title_type = 'movie'
ORDER BY r.num_votes DESC NULLS LAST;

-- ------------------------------------------------------------
-- Q1 - contraste: apagando los índices el motor cae a Seq Scan
-- sobre name (15 M), name_known_for (25 M) y title (12 M).
-- Sirve para ver el "antes".
-- ------------------------------------------------------------
SET enable_indexscan = off;
SET enable_bitmapscan = off;

EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT n.nconst, n.primary_name, t.primary_title, r.average_rating, r.num_votes
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst
LEFT JOIN title_rating r ON r.tconst = t.tconst
WHERE n.primary_name = 'Tom Hanks'
  AND t.title_type = 'movie'
ORDER BY r.num_votes DESC NULLS LAST;

RESET enable_indexscan;
RESET enable_bitmapscan;

-- ------------------------------------------------------------
-- Q2 - plan real de la consulta agregada "a mano"
-- Se ve el uso de ix_name_actor (índice parcial) y ix_title_type,
-- pero también los puntos caros (nested loop de millones de vueltas,
-- sorts que van a disco). Ver README.
-- ------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT n.nconst, n.primary_name, COUNT(*) AS peliculas,
       ROUND(AVG(r.average_rating),2) AS rating_promedio, SUM(r.num_votes) AS votos_totales
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst AND t.title_type = 'movie'
JOIN title_rating r    ON r.tconst  = t.tconst
WHERE n.primary_profession LIKE '%actor%' OR n.primary_profession LIKE '%actress%'
GROUP BY n.nconst, n.primary_name
HAVING COUNT(*) >= 3
ORDER BY rating_promedio DESC, votos_totales DESC
LIMIT 10;

-- ------------------------------------------------------------
-- Q2 - plan usando la vista materializada: "Index Scan using
-- ix_mv_actor_rating" y listo. De ~77 s a ~0,05 s.
-- ------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT *
FROM mv_actor_movie_rating
WHERE peliculas >= 3
ORDER BY rating_promedio DESC, votos_totales DESC
LIMIT 10;
