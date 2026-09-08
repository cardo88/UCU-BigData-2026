# SQL-00 - Ejercicio 3

## Objetivo

Practicar `JOIN` y detección de filas sin correspondencia. Se pide:

1. Lista de todos los estudiantes y los nombres de los cursos en los que están
   inscriptos, **incluyendo** a los que no están en ningún curso.
2. Los nombres de los estudiantes que **no** están inscriptos a ningún curso
   (si los hay).
3. Lista **únicamente** de los estudiantes que están inscriptos a algún curso.

## Archivos

| Archivo | Descripción |
| --- | --- |
| `ejercicio3.sql` | Las 3 consultas. Son de solo lectura, no modifican datos. |

La configuración compartida (Docker, script inicial) está en el
[README de SQL-00](../README.md).

## Cómo ejecutar

Desde la carpeta `SQL-00/`. Conviene partir de la base recreada (el ejercicio 2
borra cursos e inscripciones):

```bash
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < initial_script_fixed.sql
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < ejercicio3/ejercicio3.sql
```

## Decisiones y detalles

### 1. Estudiantes + cursos, incluyendo los que no tienen ninguno

`LEFT JOIN` desde `Students`: se conserva toda fila de `Students` aunque no
tenga match. Se encadena un segundo `LEFT JOIN` a `Courses` para traer el
nombre del curso. Los alumnos sin inscripción salen con `CourseName` en `NULL`
(celda vacía en `psql`).

Un alumno con varias inscripciones aparece en varias filas (John Doe y Jane
Smith, con 2 cursos cada uno).

### 2. Estudiantes sin ninguna inscripción

Mismo `LEFT JOIN` a `Enrollments`, filtrando `WHERE e.EnrollmentID IS NULL`:
se quedan solo las filas de `Students` que no encontraron pareja. Se filtra por
`EnrollmentID` porque es la PK de `Enrollments` y nunca es `NULL` salvo cuando
no hubo match.

Equivalente con `NOT EXISTS`:

```sql
SELECT StudentID, FirstName, LastName
FROM Students s
WHERE NOT EXISTS (SELECT 1 FROM Enrollments e WHERE e.StudentID = s.StudentID);
```

### 3. Solo estudiantes con al menos una inscripción

`INNER JOIN` con `Enrollments` (descarta a los que no tienen) + `DISTINCT`
para no repetir a quien tiene más de una inscripción. Es el complemento exacto
de la consulta 2.

## Resultado esperado

### Consulta 1 — 27 filas

Las 25 filas de `Students` más las inscripciones extra de John Doe y Jane Smith
(2 cursos cada uno = +2). Emily Davis (4) y Daniel Brown (5) aparecen con
`CourseName` vacío.

```
 studentid | firstname | lastname |            coursename
-----------+-----------+----------+----------------------------------
         1 | John      | Doe      | Introduction to Computer Science
         1 | John      | Doe      | Physics I
         2 | Jane      | Smith    | Calculus I
         2 | Jane      | Smith    | Physics I
         3 | Mike      | Johnson  | Introduction to Computer Science
         4 | Emily     | Davis    |
         5 | Daniel    | Brown    |
         6 | Alice     | Smith    | Introduction to Computer Science
        ...
        25 | Ethan     | Anderson | Calculus I
(27 rows)
```

### Consulta 2 — 2 filas

| studentid | firstname | lastname |
| --- | --- | --- |
| 4 | Emily | Davis |
| 5 | Daniel | Brown |

### Consulta 3 — 23 filas

Los `StudentID` 1, 2, 3 y 6..25 (todos menos el 4 y el 5).
