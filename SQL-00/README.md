# SQL-00 - Práctica de SQL

Serie de 7 ejercicios de SQL sobre una base de datos académica de ejemplo
(alumnos, cursos e inscripciones), corriendo en PostgreSQL 16 dentro de Docker.

## Estructura de la carpeta

| Ruta | Descripción |
| --- | --- |
| `docker-compose.yml` | Levanta PostgreSQL 16 (`bigdata-postgres`) y pgAdmin (`bigdata-pgadmin`). |
| `use.md` | Comandos para levantar, conectarse y apagar los contenedores. |
| `initial_script.sql.txt` | Script original provisto por la cátedra (**tiene errores de sintaxis**). |
| `initial_script_fixed.sql` | Versión corregida del script inicial. Es la que se usa para (re)crear la base. |
| `ejercicioN/` | Carpeta por ejercicio: `ejercicioN.sql` + `README.md` + capturas. |
| `imdbws/` | Datasets `.tsv.gz` de IMDb usados a partir del ejercicio 5 (no versionados). |

## Modelo de datos

- **Students** (`StudentID`, `FirstName`, `LastName`, `DateOfBirth`, `Email`, `Major`)
- **Courses** (`CourseID`, `CourseName`, `Department`, `Credits`)
- **Enrollments** (`EnrollmentID`, `StudentID` → Students, `CourseID` → Courses, `EnrollmentDate`)

## Errores del `initial_script.sql.txt` original

El script provisto no se puede ejecutar tal cual. `initial_script_fixed.sql`
corrige:

1. **Students**: falta la coma al final de la fila `(3, 'Mike', 'Johnson', ...)`.
2. **Courses**: la fila `(114, 'Astronomy', 'Physics', 3);` cierra el `INSERT`
   con `;` y deja la fila `(115, 'Organic Chemistry', ...)` suelta, con una
   coma final sobrante.
3. Esas dos filas quedan además en el orden equivocado.

Además se agregó `DROP TABLE IF EXISTS` al inicio para poder recargar la base
cuantas veces haga falta. Con la corrección se cargan **25 estudiantes, 15
cursos y 25 inscripciones**.

## Puesta en marcha

Desde esta carpeta (`SQL-00/`):

```bash
# Levantar los contenedores
docker compose up -d

# (Re)crear la base con datos limpios
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < initial_script_fixed.sql
```

Cada ejercicio parte de la base recién recreada. Para correr un ejercicio:

```bash
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < ejercicioN/ejercicioN.sql
```

O entrar a la consola interactiva:

```bash
docker exec -it bigdata-postgres psql -U bigdata -d bigdata_db
```

El mismo PostgreSQL aloja dos bases: `bigdata_db` (ejercicios 1–4) e `imdb`
(ejercicio 6, datasets de IMDb). Son independientes.

## Ejercicios

| # | Tema | Carpeta |
| --- | --- | --- |
| 1 | Consultas `SELECT` básicas | [ejercicio1/](ejercicio1/README.md) |
| 2 | `INSERT`, `UPDATE`, `DELETE` y restricciones de clave foránea | [ejercicio2/](ejercicio2/README.md) |
| 3 | `LEFT`/`INNER JOIN`, estudiantes sin inscripciones | [ejercicio3/](ejercicio3/README.md) |
| 4 | Agregaciones con `GROUP BY` (`COUNT`, `AVG`, `SUM`) | [ejercicio4/](ejercicio4/README.md) |
| 5 | Metadata de IMDb: modelo conceptual, transaccional vs analítico, qué indexar, particionamiento, visualización | [ejercicio5/](ejercicio5/README.md) |
| 6 | Importar los 3 datasets de IMDb a una base nueva `imdb` (`\copy` + tipado + índices) | [ejercicio6/](ejercicio6/README.md) |
| 7 | Modelar y consultar actor↔película; optimización, vista materializada y `EXPLAIN` | [ejercicio7/](ejercicio7/README.md) |
