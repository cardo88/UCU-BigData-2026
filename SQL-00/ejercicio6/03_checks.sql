-- ============================================================
-- Ejercicio 6 - Paso 3: verificaciones de la importación
-- ============================================================

-- Conteo por tabla
SELECT 'name'         AS tabla, count(*) AS filas FROM name
UNION ALL
SELECT 'title',        count(*) FROM title
UNION ALL
SELECT 'title_rating', count(*) FROM title_rating;

-- Títulos por tipo
SELECT title_type, count(*) AS cantidad
FROM title
GROUP BY title_type
ORDER BY cantidad DESC;

-- ¿Cuántos títulos tienen puntaje?
SELECT count(*) AS titulos_con_rating,
       round(100.0 * count(*) / (SELECT count(*) FROM title), 1) AS pct_del_total
FROM title_rating;

-- Top 10 películas por cantidad de votos
SELECT t.primary_title, t.start_year, r.average_rating, r.num_votes
FROM title t
JOIN title_rating r USING (tconst)
WHERE t.title_type = 'movie'
ORDER BY r.num_votes DESC
LIMIT 10;
