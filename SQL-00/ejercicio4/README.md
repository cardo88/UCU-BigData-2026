# SQL-00 - Ejercicio 4

## Objetivo

Practicar funciones de agregación con `GROUP BY`. Se pide:

1. Cantidad de alumnos por `Major`.
2. Promedio de créditos por curso.
3. Cantidad de `Enrollments` por año.
4. Para cada estudiante, el total de créditos adquiridos.

## Archivos

| Archivo | Descripción |
| --- | --- |
| `ejercicio4.sql` | Las 4 consultas. Son de solo lectura, no modifican datos. |

La configuración compartida (Docker, script inicial) está en el
[README de SQL-00](../README.md).

## Cómo ejecutar

Desde la carpeta `SQL-00/`, partiendo de la base recreada:

```bash
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < initial_script_fixed.sql
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < ejercicio4/ejercicio4.sql
```

## Decisiones y detalles

### 1. Alumnos por Major

`GROUP BY Major` + `COUNT(*)`. Se ordena por cantidad descendente y luego por
nombre del Major para desempatar.

### 2. Promedio de créditos por curso

Se interpreta como el promedio del campo `Credits` sobre todos los cursos:
`AVG(Credits)` sobre `Courses`, sin agrupar. Se usa `ROUND(..., 2)` porque
`AVG` de enteros devuelve muchos decimales.

### 3. Enrollments por año

El año se extrae de `EnrollmentDate` con `EXTRACT(YEAR FROM ...)`, casteado a
`int` para que se vea limpio. En los datos de ejemplo todas las inscripciones
son de 2023, así que devuelve una sola fila.

### 4. Total de créditos por estudiante

`Students LEFT JOIN Enrollments LEFT JOIN Courses`, `SUM(c.Credits)` agrupado
por estudiante. El `LEFT JOIN` + `COALESCE(SUM(...), 0)` hace que Emily Davis
y Daniel Brown (sin inscripciones) aparezcan con total 0 en vez de quedar
fuera del resultado.

## Resultado esperado

### Consulta 1 — alumnos por Major

| major | cantidad_alumnos |
| --- | --- |
| Biology | 5 |
| Chemistry | 5 |
| Computer Science | 4 |
| Engineering | 4 |
| Mathematics | 4 |
| Physics | 3 |

### Consulta 2 — promedio de créditos

| promedio_creditos |
| --- |
| 3.40 |

15 cursos: 8 con 3 créditos y 7 con 4 créditos → 51 / 15 = 3.40.

### Consulta 3 — Enrollments por año

| anio | cantidad_enrollments |
| --- | --- |
| 2023 | 25 |

### Consulta 4 — total de créditos por estudiante (25 filas)

Extremos de la lista:

| studentid | firstname | lastname | total_creditos |
| --- | --- | --- | --- |
| 2 | Jane | Smith | 8 |
| 1 | John | Doe | 7 |
| 7 | Bob | Johnson | 4 |
| ... | ... | ... | 4 |
| 3 | Mike | Johnson | 3 |
| ... | ... | ... | 3 |
| 4 | Emily | Davis | 0 |
| 5 | Daniel | Brown | 0 |

Jane Smith (Calculus I + Physics I = 4+4) y John Doe (Intro to CS + Physics I =
3+4) son los únicos con más de un curso.
