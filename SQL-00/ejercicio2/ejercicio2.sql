-- ============================================================
-- Ejercicio 2 - INSERT / UPDATE / DELETE
-- Parte de la base recreada con ../initial_script_fixed.sql
-- ============================================================

-- 1. Insertar tres nuevos alumnos, usando Majors que ya existen en la tabla
--    (Biology, Mathematics, Physics). Los StudentID 1..25 ya están ocupados.
INSERT INTO Students (StudentID, FirstName, LastName, DateOfBirth, Email, Major)
VALUES
    (26, 'Lucas',  'Green',  '2001-02-11', 'lucas.green@email.com',  'Biology'),
    (27, 'Maria',  'Lopez',  '2000-10-30', 'maria.lopez@email.com',  'Mathematics'),
    (28, 'Tomas',  'Ferrari','2001-06-05', 'tomas.ferrari@email.com','Physics');

-- 2. Actualizar el email de 'Jane Smith'
UPDATE Students
SET Email = 'jsmith@email.com'
WHERE FirstName = 'Jane' AND LastName = 'Smith';

-- 3. Renombrar el Major 'Computer Science' a 'Computer Science & AI'
--    para todos los estudiantes que lo tengan.
UPDATE Students
SET Major = 'Computer Science & AI'
WHERE Major = 'Computer Science';

-- 4. Eliminar el curso 'Introduction to Database Systems' (CourseID 104).
--    No tiene inscripciones asociadas, se borra directo.
DELETE FROM Courses
WHERE CourseName = 'Introduction to Database Systems';

-- 5. Eliminar el curso 103 ('Physics I').
--    Este curso SÍ tiene inscripciones en Enrollments y la FK es RESTRICT,
--    así que primero hay que borrar esas inscripciones o el DELETE falla con
--    "violates foreign key constraint". Se borran las inscripciones y luego
--    el curso.
DELETE FROM Enrollments
WHERE CourseID = 103;

DELETE FROM Courses
WHERE CourseID = 103;

-- ------------------------------------------------------------
-- Verificaciones
-- ------------------------------------------------------------

-- 1. Los tres alumnos nuevos
SELECT StudentID, FirstName, LastName, Email, Major
FROM Students
WHERE StudentID IN (26, 27, 28);

-- 2. Email de Jane Smith
SELECT FirstName, LastName, Email
FROM Students
WHERE FirstName = 'Jane' AND LastName = 'Smith';

-- 3. Ya no debe quedar nadie con Major 'Computer Science' exacto;
--    sí con 'Computer Science & AI'
SELECT Major, COUNT(*) AS cantidad
FROM Students
WHERE Major LIKE 'Computer Science%'
GROUP BY Major;

-- 4 y 5. Los cursos 103 y 104 ya no existen
SELECT CourseID, CourseName, Department, Credits
FROM Courses
WHERE CourseID IN (103, 104)
   OR CourseName = 'Introduction to Database Systems';
