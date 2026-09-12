-- ============================================================
-- Ejercicio 7 - Paso 2: las consultas pedidas
-- Base: imdb, con el modelo del paso 1 (01_model.sql) ya creado.
-- ============================================================

-- ------------------------------------------------------------
-- Consulta 1: películas de un actor determinado y sus ratings
-- ------------------------------------------------------------
-- primary_name NO es único (hay varias personas con el mismo
-- nombre). Para un actor puntual conviene filtrar por nconst;
-- acá se deja por nombre como pide la consigna.
SELECT n.nconst,
       n.primary_name,
       t.primary_title,
       t.start_year,
       r.average_rating,
       r.num_votes
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst
LEFT JOIN title_rating r ON r.tconst = t.tconst
WHERE n.primary_name = 'Tom Hanks'
  AND t.title_type = 'movie'
ORDER BY r.num_votes DESC NULLS LAST;

-- ------------------------------------------------------------
-- Consulta 2: top 10 actores por puntaje promedio de películas
-- ------------------------------------------------------------
SELECT n.nconst,
       n.primary_name,
       COUNT(*)                        AS peliculas,
       ROUND(AVG(r.average_rating), 2) AS rating_promedio,
       SUM(r.num_votes)                AS votos_totales
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst AND t.title_type = 'movie'
JOIN title_rating r    ON r.tconst  = t.tconst
WHERE n.primary_profession LIKE '%actor%'
   OR n.primary_profession LIKE '%actress%'
GROUP BY n.nconst, n.primary_name
HAVING COUNT(*) >= 3          -- descarta actores con 1-2 pelis y promedio inflado
ORDER BY rating_promedio DESC, votos_totales DESC
LIMIT 10;

-- Variante 2b: además exigir películas realmente vistas (masa de votos).
-- Sin esto, el top se llena de gente con 3 títulos oscuros votados por
-- decenas de personas con 9.5.
SELECT n.nconst,
       n.primary_name,
       COUNT(*)                        AS peliculas,
       ROUND(AVG(r.average_rating), 2) AS rating_promedio,
       SUM(r.num_votes)                AS votos_totales
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst AND t.title_type = 'movie'
JOIN title_rating r    ON r.tconst  = t.tconst
WHERE (n.primary_profession LIKE '%actor%' OR n.primary_profession LIKE '%actress%')
  AND r.num_votes >= 50000
GROUP BY n.nconst, n.primary_name
HAVING COUNT(*) >= 3
ORDER BY rating_promedio DESC, votos_totales DESC
LIMIT 10;

-- ------------------------------------------------------------
-- Optimización de la consulta 2: vista materializada
-- (ver README, sección "Acciones de optimización")
-- ------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS mv_actor_movie_rating;
CREATE MATERIALIZED VIEW mv_actor_movie_rating AS
SELECT n.nconst,
       n.primary_name,
       COUNT(*)                        AS peliculas,
       ROUND(AVG(r.average_rating), 2) AS rating_promedio,
       SUM(r.num_votes)                AS votos_totales
FROM name n
JOIN name_known_for kf ON kf.nconst = n.nconst
JOIN title t           ON t.tconst  = kf.tconst AND t.title_type = 'movie'
JOIN title_rating r    ON r.tconst  = t.tconst
WHERE n.primary_profession LIKE '%actor%'
   OR n.primary_profession LIKE '%actress%'
GROUP BY n.nconst, n.primary_name;

CREATE INDEX ix_mv_actor_rating
    ON mv_actor_movie_rating (rating_promedio DESC, votos_totales DESC);

ANALYZE mv_actor_movie_rating;

-- Con la vista, la consulta 2 pasa a ser instantánea:
SELECT *
FROM mv_actor_movie_rating
WHERE peliculas >= 3
ORDER BY rating_promedio DESC, votos_totales DESC
LIMIT 10;

-- Refrescar cuando cambie el dataset (fuera de hora, junto con la ingesta):
--   REFRESH MATERIALIZED VIEW mv_actor_movie_rating;

-- ------------------------------------------------------------
-- Consulta 3 (procesamiento intensivo): "joyas ocultas" por género
-- ------------------------------------------------------------
-- Películas muy bien puntuadas pero con relativamente pocos votos:
-- recomendaciones que el público masivo todavía no descubrió.
-- Recorre title_rating (1.7 M) + title y desarma la lista de géneros.
SELECT g.genero,
       t.primary_title,
       t.start_year,
       r.average_rating,
       r.num_votes,
       ROW_NUMBER() OVER (PARTITION BY g.genero
                          ORDER BY r.average_rating DESC, r.num_votes DESC) AS puesto
FROM title_rating r
JOIN title t ON t.tconst = r.tconst
CROSS JOIN LATERAL unnest(string_to_array(t.genres, ',')) AS g(genero)
WHERE t.title_type = 'movie'
  AND t.genres IS NOT NULL
  AND t.start_year <= EXTRACT(YEAR FROM CURRENT_DATE)::int   -- excluir no estrenadas
  AND r.average_rating >= 8.0
  AND r.num_votes BETWEEN 2000 AND 25000
ORDER BY g.genero, puesto;
