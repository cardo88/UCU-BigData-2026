-- ============================================================
-- Ejercicio 4 - Agregaciones (GROUP BY)
-- Parte de la base recreada con ../initial_script_fixed.sql
-- (todas las consultas son de solo lectura, no modifican datos)
-- ============================================================

-- 1. Cantidad de alumnos por Major
SELECT Major,
       COUNT(*) AS cantidad_alumnos
FROM Students
GROUP BY Major
ORDER BY cantidad_alumnos DESC, Major;

-- 2. Promedio de créditos por curso
--    (promedio del campo Credits sobre todos los cursos)
SELECT ROUND(AVG(Credits), 2) AS promedio_creditos
FROM Courses;

-- 3. Cantidad de Enrollments por año (año tomado de EnrollmentDate)
SELECT EXTRACT(YEAR FROM EnrollmentDate)::int AS anio,
       COUNT(*) AS cantidad_enrollments
FROM Enrollments
GROUP BY anio
ORDER BY anio;

-- 4. Para cada estudiante, el total de créditos adquiridos
--    (suma de Credits de los cursos en los que está inscripto).
--    LEFT JOIN para que los estudiantes sin inscripciones aparezcan con 0.
SELECT s.StudentID,
       s.FirstName,
       s.LastName,
       COALESCE(SUM(c.Credits), 0) AS total_creditos
FROM Students s
LEFT JOIN Enrollments e ON e.StudentID = s.StudentID
LEFT JOIN Courses      c ON c.CourseID  = e.CourseID
GROUP BY s.StudentID, s.FirstName, s.LastName
ORDER BY total_creditos DESC, s.StudentID;
