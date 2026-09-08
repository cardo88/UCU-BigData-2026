# SQL-00 - Ejercicio 2

## Objetivo

Practicar operaciones de modificación de datos (`INSERT`, `UPDATE`, `DELETE`)
sobre la base del [Ejercicio 1](../ejercicio1/README.md). Se pide:

1. Insertar tres nuevos alumnos en `Students`, usando Majors que ya existen.
2. Actualizar el email de "Jane Smith" a `jsmith@email.com`.
3. Cambiar el `Major` de todos los estudiantes de `Computer Science` a
   `Computer Science & AI`.
4. Eliminar el curso "Introduction to Database Systems".
5. Eliminar el curso `103`.

## Archivos

| Archivo | Descripción |
| --- | --- |
| `ejercicio2.sql` | Los 5 cambios + consultas de verificación. |

La configuración compartida (Docker, script inicial) está en el
[README de SQL-00](../README.md).

## Cómo ejecutar

Desde la carpeta `SQL-00/`, con la base recién recreada:

```bash
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < initial_script_fixed.sql
docker exec -i bigdata-postgres psql -U bigdata -d bigdata_db < ejercicio2/ejercicio2.sql
```

## Decisiones y detalles

### 1. Alumnos nuevos

Los `StudentID` 1..25 ya están ocupados, así que se usan 26, 27 y 28. Los
Majors elegidos (`Biology`, `Mathematics`, `Physics`) ya existían en la tabla
antes de este ejercicio, como pide la consigna. Se eligieron Majors distintos
de `Computer Science` para que el paso 1 y el paso 3 no se pisen.

### 2. Email de Jane Smith

Se filtra por `FirstName = 'Jane' AND LastName = 'Smith'`. En estos datos hay
una sola Jane Smith (`StudentID` 2), así que la actualización afecta 1 fila.

### 3. Renombrar el Major

`UPDATE ... WHERE Major = 'Computer Science'` afecta a 4 estudiantes (John Doe,
Emma Wilson, Grace Moore, Olivia Harris). Tras el cambio no queda nadie con el
valor exacto `Computer Science`; los 4 pasan a `Computer Science & AI`.

### 4. Eliminar "Introduction to Database Systems"

Es el `CourseID` 104. **No** tiene inscripciones en `Enrollments`, así que el
`DELETE` sobre `Courses` funciona directamente (borra 1 fila).

### 5. Eliminar el curso 103 — restricción de clave foránea

El curso 103 ("Physics I") **sí** tiene inscripciones en `Enrollments`. La
clave foránea `Enrollments.CourseID → Courses.CourseID` es `RESTRICT` por
defecto, por lo que borrar el curso directamente falla con:

```
ERROR: update or delete on table "courses" violates foreign key constraint
       "enrollments_courseid_fkey" on table "enrollments"
```

Por eso el script primero borra las inscripciones del curso 103 (8 filas) y
después el curso (1 fila):

```sql
DELETE FROM Enrollments WHERE CourseID = 103;
DELETE FROM Courses     WHERE CourseID = 103;
```

Alternativas que no se usaron aquí: definir la FK con `ON DELETE CASCADE` al
crear la tabla, o ejecutar el borrado en cascada manual como se hizo.

## Resultado de la ejecución

```
INSERT 0 3      -- 3 alumnos nuevos
UPDATE 1        -- email de Jane Smith
UPDATE 4        -- Major Computer Science -> Computer Science & AI
DELETE 1        -- curso 104 (Introduction to Database Systems)
DELETE 8        -- inscripciones del curso 103
DELETE 1        -- curso 103 (Physics I)
```

Verificaciones:

| Verificación | Resultado |
| --- | --- |
| Alumnos 26, 27, 28 | Lucas Green (Biology), Maria Lopez (Mathematics), Tomas Ferrari (Physics) |
| Email de Jane Smith | `jsmith@email.com` |
| Majors `Computer Science%` | `Computer Science & AI` → 4 estudiantes; `Computer Science` → 0 |
| Cursos 103 / 104 | 0 filas (ya no existen) |
