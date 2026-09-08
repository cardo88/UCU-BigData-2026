# SQL-00 - Ejercicio 1

## Objetivo

Practicar consultas `SELECT` básicas sobre la base de datos provista en
`initial_script.sql`. Se pide:

1. Seleccionar todos los alumnos.
2. Seleccionar únicamente los nombres de los cursos.
3. Seleccionar los nombres de los estudiantes cuyo `Major` sea
   "Computer Science".
4. Listar el nombre y la cantidad de créditos de los cursos del departamento
   "Computer Science", ordenados de mayor a menor.

La configuración compartida (Docker, script inicial) está descrita en el
[README de SQL-00](../README.md).

## Archivos

| Archivo | Descripción |
| --- | --- |
| `ejercicio1.sql` | Las 4 consultas pedidas. |
| `../initial_script_fixed.sql` | Versión corregida del script inicial (ver errores abajo). |

## Modelo de datos

- **Students** (`StudentID`, `FirstName`, `LastName`, `DateOfBirth`, `Email`, `Major`)
- **Courses** (`CourseID`, `CourseName`, `Department`, `Credits`)
- **Enrollments** (`EnrollmentID`, `StudentID` → Students, `CourseID` → Courses, `EnrollmentDate`)

## Errores encontrados en `initial_script.sql.txt`

El script original no se puede ejecutar tal cual. Se detectaron tres problemas:

1. **Students**: falta la coma al final de la fila
   `(3, 'Mike', 'Johnson', ...)`, por lo que el `INSERT` queda partido.
2. **Courses**: la fila `(114, 'Astronomy', 'Physics', 3);` cierra el
   `INSERT` con `;` y deja la fila `(115, 'Organic Chemistry', ...)` suelta,
   además con una coma final sobrante.
3. Como consecuencia del punto anterior, esas dos filas quedan en el orden
   equivocado (el `;` aparece antes de la última fila).

`initial_script_fixed.sql` corrige los tres puntos y agrega `DROP TABLE IF
EXISTS` al inicio para poder recargar la base cuantas veces haga falta. Con la
corrección se cargan 25 estudiantes, 15 cursos y 25 inscripciones.

## Cómo ejecutar

Desde la carpeta `SQL-00/`, con los contenedores levantados
(`docker compose up -d`):

```bash
# 1. Crear la base y cargar los datos
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < initial_script_fixed.sql

# 2. Ejecutar las consultas del ejercicio
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < ejercicio1/ejercicio1.sql
```

También se puede entrar a la consola interactiva y pegar las consultas:

```bash
docker exec -it bigdata-postgres psql -U bigdata -d bigdata_db
```

## Consultas y resultados

### 1. Todos los alumnos

```sql
SELECT *
FROM Students;
```

Devuelve las 25 filas de la tabla `Students` con todas sus columnas.

### 2. Solo los nombres de los cursos

```sql
SELECT CourseName
FROM Courses;
```

| coursename |
| --- |
| Introduction to Computer Science |
| Calculus I |
| Physics I |
| Introduction to Database Systems |
| Introduction to Chemistry |
| Statistics |
| Literature |
| History |
| Art History |
| Environmental Science |
| Introduction to Psychology |
| Data Structures |
| Mechanical Engineering |
| Astronomy |
| Organic Chemistry |

15 filas.

### 3. Nombres de estudiantes con Major "Computer Science"

```sql
SELECT FirstName, LastName
FROM Students
WHERE Major = 'Computer Science';
```

| firstname | lastname |
| --- | --- |
| John | Doe |
| Emma | Wilson |
| Grace | Moore |
| Olivia | Harris |

4 filas.

### 4. Cursos del departamento "Computer Science" por créditos (desc)

```sql
SELECT CourseName, Credits
FROM Courses
WHERE Department = 'Computer Science'
ORDER BY Credits DESC;
```

| coursename | credits |
| --- | --- |
| Data Structures | 4 |
| Introduction to Computer Science | 3 |
| Introduction to Database Systems | 3 |

3 filas.

## Notas

- El punto 3 pide "los nombres", por eso se seleccionan `FirstName` y
  `LastName`. Si se quisiera un solo campo se puede usar
  `SELECT FirstName || ' ' || LastName AS nombre_completo`.
- PostgreSQL no distingue mayúsculas en los identificadores sin comillas, por
  eso las columnas aparecen en minúscula en la salida (`coursename`,
  `firstname`, etc.).
- Los dos cursos con 3 créditos quedan en orden arbitrario entre sí; si se
  necesita un orden estable se puede agregar `, CourseName` al `ORDER BY`.
