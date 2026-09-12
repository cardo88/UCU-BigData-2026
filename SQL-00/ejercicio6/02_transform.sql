-- ============================================================
-- Ejercicio 6 - Paso 2: tablas finales tipadas + índices
-- Parte de las tablas stg_* ya cargadas.
-- ============================================================

DROP TABLE IF EXISTS title_rating, title, name CASCADE;

-- ---------- name (personas) ----------
CREATE TABLE name (
    nconst             text PRIMARY KEY,
    primary_name       text,
    birth_year         smallint,
    death_year         smallint,
    primary_profession text,
    known_for_titles   text
);

INSERT INTO name
SELECT
    nconst,
    primaryname,
    CASE WHEN birthyear ~ '^[0-9]+$' THEN birthyear::smallint END,
    CASE WHEN deathyear ~ '^[0-9]+$' THEN deathyear::smallint END,
    primaryprofession,
    knownfortitles
FROM stg_name_basics
WHERE nconst IS NOT NULL;

-- ---------- title (títulos) ----------
CREATE TABLE title (
    tconst          text PRIMARY KEY,
    title_type      text,
    primary_title   text,
    original_title  text,
    is_adult        boolean,
    start_year      smallint,
    end_year        smallint,
    runtime_minutes integer,
    genres          text
);

INSERT INTO title
SELECT
    tconst,
    titletype,
    primarytitle,
    originaltitle,
    CASE isadult WHEN '1' THEN true WHEN '0' THEN false END,
    CASE WHEN startyear      ~ '^[0-9]+$' THEN startyear::smallint END,
    CASE WHEN endyear        ~ '^[0-9]+$' THEN endyear::smallint END,
    CASE WHEN runtimeminutes ~ '^[0-9]+$' THEN runtimeminutes::integer END,
    genres
FROM stg_title_basics
WHERE tconst IS NOT NULL;

-- ---------- title_rating (puntajes) ----------
CREATE TABLE title_rating (
    tconst         text PRIMARY KEY REFERENCES title(tconst),
    average_rating numeric(3,1),
    num_votes      integer
);

INSERT INTO title_rating
SELECT
    r.tconst,
    CASE WHEN r.averagerating ~ '^[0-9]+(\.[0-9]+)?$' THEN r.averagerating::numeric(3,1) END,
    CASE WHEN r.numvotes      ~ '^[0-9]+$'            THEN r.numvotes::integer END
FROM stg_title_ratings r
WHERE r.tconst IS NOT NULL
  AND EXISTS (SELECT 1 FROM title t WHERE t.tconst = r.tconst);

-- ---------- índices sugeridos en el ejercicio 5 ----------
-- (columnas por las que se filtra / rankea / cruza)
CREATE INDEX ix_title_type       ON title (title_type);
CREATE INDEX ix_title_start_year ON title (start_year);
CREATE INDEX ix_rating_num_votes ON title_rating (num_votes);
CREATE INDEX ix_rating_avg       ON title_rating (average_rating);

-- ---------- limpieza ----------
DROP TABLE stg_name_basics, stg_title_basics, stg_title_ratings;

ANALYZE;
