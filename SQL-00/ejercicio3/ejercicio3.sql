-- ============================================================
-- Ejercicio 3 - JOINs y estudiantes sin inscripciones
-- Parte de la base recreada con ../initial_script_fixed.sql
-- (todas las consultas son de solo lectura, no modifican datos)
-- ============================================================

-- 1. Todos los estudiantes y los nombres de los cursos en los que están
--    inscriptos, incluyendo a los que no están en ningún curso.
--    LEFT JOIN desde Students: los alumnos sin inscripción aparecen con
--    CourseName en NULL.
SELECT s.StudentID,
       s.FirstName,
       s.LastName,
       c.CourseName
FROM Students s
LEFT JOIN Enrollments e ON e.StudentID = s.StudentID
LEFT JOIN Courses      c ON c.CourseID  = e.CourseID
ORDER BY s.StudentID, c.CourseName;

-- 2. Nombres de los estudiantes que NO están inscriptos a ningún curso.
--    Mismo LEFT JOIN, pero filtrando las filas sin match en Enrollments.
SELECT s.StudentID,
       s.FirstName,
       s.LastName
FROM Students s
LEFT JOIN Enrollments e ON e.StudentID = s.StudentID
WHERE e.EnrollmentID IS NULL
ORDER BY s.StudentID;

-- 3. Lista únicamente de los estudiantes que están inscriptos a algún curso.
--    INNER JOIN + DISTINCT para no repetir a quien tiene varias inscripciones.
SELECT DISTINCT s.StudentID,
       s.FirstName,
       s.LastName
FROM Students s
JOIN Enrollments e ON e.StudentID = s.StudentID
ORDER BY s.StudentID;
