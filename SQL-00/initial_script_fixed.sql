-- Versión corregida de initial_script.sql.txt
-- El script original tiene 3 errores de sintaxis que impiden cargarlo:
--   1. Falta una coma tras la fila (3, 'Mike', ...) en el INSERT de Students.
--   2. En el INSERT de Courses, la fila (114, 'Astronomy', ...) cierra con ';'
--      y la fila (115, 'Organic Chemistry', ...) queda suelta con coma final.
--   3. Esas dos filas quedan además en el orden equivocado (';' antes de la
--      última fila).
-- Aquí se dejan corregidos para poder crear la base y probar las consultas.

DROP TABLE IF EXISTS Enrollments;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Students;

-- Create the Students table
CREATE TABLE Students (
    StudentID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    DateOfBirth DATE,
    Email VARCHAR(100),
    Major VARCHAR(50)
);

-- Create the Courses table
CREATE TABLE Courses (
    CourseID INT PRIMARY KEY,
    CourseName VARCHAR(100),
    Department VARCHAR(50),
    Credits INT
);

-- Create the Enrollments table to track student enrollments in courses
CREATE TABLE Enrollments (
    EnrollmentID INT PRIMARY KEY,
    StudentID INT,
    CourseID INT,
    EnrollmentDate DATE,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

-- Insert sample data into Students table
INSERT INTO Students (StudentID, FirstName, LastName, DateOfBirth, Email, Major)
VALUES
    (1, 'John', 'Doe', '1995-05-15', 'john.doe@email.com', 'Computer Science'),
    (2, 'Jane', 'Smith', '1998-09-20', 'jane.smith@email.com', 'Mathematics'),
    (3, 'Mike', 'Johnson', '1997-03-10', 'mike.johnson@email.com', 'Engineering'),
    (4, 'Emily', 'Davis', '1999-08-25', 'emily@email.com', 'Biology'),
    (5, 'Daniel', 'Brown', '2000-03-12', 'daniel@email.com', 'Chemistry'),
    (6, 'Alice', 'Smith', '1999-02-15', 'alice.smith@email.com', 'Biology'),
    (7, 'Bob', 'Johnson', '2000-05-20', 'bob.johnson@email.com', 'Chemistry'),
    (8, 'Charlie', 'Brown', '1999-07-10', 'charlie.brown@email.com', 'Biology'),
    (9, 'David', 'Davis', '2000-03-25', 'david.davis@email.com', 'Chemistry'),
    (10, 'Emma', 'Wilson', '2001-01-12', 'emma.wilson@email.com', 'Computer Science'),
    (11, 'Frank', 'Miller', '2000-08-08', 'frank.miller@email.com', 'Engineering'),
    (12, 'Grace', 'Moore', '1999-06-30', 'grace.moore@email.com', 'Computer Science'),
    (13, 'Hannah', 'Anderson', '2000-09-22', 'hannah.anderson@email.com', 'Mathematics'),
    (14, 'Isabella', 'Clark', '1999-11-05', 'isabella.clark@email.com', 'Physics'),
    (15, 'James', 'Thomas', '2001-03-18', 'james.thomas@email.com', 'Engineering'),
    (16, 'Katherine', 'White', '1999-04-27', 'katherine.white@email.com', 'Mathematics'),
    (17, 'Liam', 'Adams', '2000-12-14', 'liam.adams@email.com', 'Physics'),
    (18, 'Mia', 'Roberts', '1999-10-08', 'mia.roberts@email.com', 'Chemistry'),
    (19, 'Noah', 'Taylor', '2000-07-01', 'noah.taylor@email.com', 'Biology'),
    (20, 'Olivia', 'Harris', '1999-05-03', 'olivia.harris@email.com', 'Computer Science'),
    (21, 'Oliver', 'Wright', '2000-11-19', 'oliver.wright@email.com', 'Engineering'),
    (22, 'Sophia', 'Martin', '1999-08-25', 'sophia.martin@email.com', 'Mathematics'),
    (23, 'William', 'Lewis', '2000-02-10', 'william.lewis@email.com', 'Physics'),
    (24, 'Ava', 'Walker', '2000-06-17', 'ava.walker@email.com', 'Chemistry'),
    (25, 'Ethan', 'Anderson', '2001-04-09', 'ethan.anderson@email.com', 'Biology');

-- Insert sample data into Courses table
INSERT INTO Courses (CourseID, CourseName, Department, Credits)
VALUES
    (101, 'Introduction to Computer Science', 'Computer Science', 3),
    (102, 'Calculus I', 'Mathematics', 4),
    (103, 'Physics I', 'Physics', 4),
    (104, 'Introduction to Database Systems', 'Computer Science', 3),
    (105, 'Introduction to Chemistry', 'Chemistry', 3),
    (106, 'Statistics', 'Mathematics', 4),
    (107, 'Literature', 'English', 3),
    (108, 'History', 'History', 3),
    (109, 'Art History', 'Art', 3),
    (110, 'Environmental Science', 'Biology', 4),
    (111, 'Introduction to Psychology', 'Psychology', 3),
    (112, 'Data Structures', 'Computer Science', 4),
    (113, 'Mechanical Engineering', 'Engineering', 4),
    (114, 'Astronomy', 'Physics', 3),
    (115, 'Organic Chemistry', 'Chemistry', 3);

-- Insert sample data into Enrollments table
INSERT INTO Enrollments (EnrollmentID, StudentID, CourseID, EnrollmentDate)
VALUES
    (1, 1, 101, '2023-01-15'),
    (2, 2, 102, '2023-01-20'),
    (3, 3, 101, '2023-01-25'),
    (4, 1, 103, '2023-02-01'),
    (5, 2, 103, '2023-02-05'),
    (9, 6, 101, '2023-02-22'),
    (10, 7, 102, '2023-03-05'),
    (11, 8, 103, '2023-03-10'),
    (12, 9, 101, '2023-03-15'),
    (13, 10, 102, '2023-03-20'),
    (14, 11, 103, '2023-03-25'),
    (15, 12, 101, '2023-03-30'),
    (16, 13, 102, '2023-04-04'),
    (17, 14, 103, '2023-04-09'),
    (18, 15, 101, '2023-04-14'),
    (19, 16, 102, '2023-04-19'),
    (20, 17, 103, '2023-04-24'),
    (21, 18, 101, '2023-04-29'),
    (22, 19, 102, '2023-05-04'),
    (23, 20, 103, '2023-05-09'),
    (24, 21, 101, '2023-05-14'),
    (25, 22, 102, '2023-05-19'),
    (26, 23, 103, '2023-05-24'),
    (27, 24, 101, '2023-05-29'),
    (28, 25, 102, '2023-06-03');
