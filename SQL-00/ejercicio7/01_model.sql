-- ============================================================
-- Ejercicio 7 - Paso 1: modelar la relación persona <-> título
-- Base: imdb (creada en el ejercicio 6).
--
-- No se descargó title.principals, así que la relación
-- actor-película se deriva de name.known_for_titles
-- (lista de hasta 4 tconst por persona). Limitación: son los
-- títulos "por los que se la conoce", no el elenco completo,
-- y no distingue el rol (actuó / dirigió / etc.).
-- ============================================================

DROP MATERIALIZED VIEW IF EXISTS mv_actor_movie_rating;
DROP TABLE IF EXISTS name_known_for;

-- Tabla puente: una fila por (persona, título conocido)
CREATE TABLE name_known_for AS
SELECT n.nconst,
       trim(kf.tconst) AS tconst
FROM name n
CROSS JOIN LATERAL unnest(string_to_array(n.known_for_titles, ',')) AS kf(tconst)
WHERE n.known_for_titles IS NOT NULL;

-- Quitar referencias a títulos que no están en title (por las dudas)
DELETE FROM name_known_for kf
WHERE NOT EXISTS (SELECT 1 FROM title t WHERE t.tconst = kf.tconst);

ALTER TABLE name_known_for ADD PRIMARY KEY (nconst, tconst);
ALTER TABLE name_known_for ADD FOREIGN KEY (nconst) REFERENCES name(nconst);
ALTER TABLE name_known_for ADD FOREIGN KEY (tconst) REFERENCES title(tconst);

-- Índices para los joins de las consultas
CREATE INDEX ix_nkf_tconst ON name_known_for (tconst);
-- (el índice por nconst ya lo da la PK, que empieza con nconst)

-- Buscar personas por nombre (consulta 1)
CREATE INDEX ix_name_primary_name ON name (primary_name);

-- Filtro "es actor/actriz" (consulta 2). Índice parcial: solo indexa
-- las filas que cumplen la condición -> más chico y más rápido.
CREATE INDEX ix_name_actor ON name (nconst)
WHERE primary_profession LIKE '%actor%' OR primary_profession LIKE '%actress%';

ANALYZE name_known_for;
ANALYZE name;
