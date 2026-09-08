-- ============================================================
-- Ejercicio 1 - Consultas sobre la base del initial_script.sql
-- Base: tablas Students, Courses, Enrollments
-- ============================================================

-- 1. Seleccionar todos los alumnos
SELECT *
FROM Students;

-- 2. Seleccionar únicamente los nombres de los cursos
SELECT CourseName
FROM Courses;

-- 3. Seleccionar los nombres de los estudiantes cuyo Major sea "Computer Science"
SELECT FirstName, LastName
FROM Students
WHERE Major = 'Computer Science';

-- 4. Nombre y cantidad de créditos de los cursos del departamento
--    "Computer Science", ordenados de mayor a menor cantidad de créditos
SELECT CourseName, Credits
FROM Courses
WHERE Department = 'Computer Science'
ORDER BY Credits DESC;
