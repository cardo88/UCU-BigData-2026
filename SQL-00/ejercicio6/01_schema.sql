-- ============================================================
-- Ejercicio 6 - Paso 1: tablas de staging (todo texto)
-- Se cargan tal cual vienen los TSV; el tipado se hace después
-- en 02_transform.sql. Así el COPY nunca falla por un cast.
-- ============================================================

DROP TABLE IF EXISTS stg_name_basics, stg_title_basics, stg_title_ratings;

CREATE TABLE stg_name_basics (
    nconst             text,
    primaryname        text,
    birthyear          text,
    deathyear          text,
    primaryprofession  text,
    knownfortitles     text
);

CREATE TABLE stg_title_basics (
    tconst          text,
    titletype       text,
    primarytitle    text,
    originaltitle   text,
    isadult         text,
    startyear       text,
    endyear         text,
    runtimeminutes  text,
    genres          text
);

CREATE TABLE stg_title_ratings (
    tconst         text,
    averagerating  text,
    numvotes       text
);
