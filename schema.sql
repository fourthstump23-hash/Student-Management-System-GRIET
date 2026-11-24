-- Student Management System Database Schema & Initial Data
-- DBMS Lab Project for GRIET (Gokaraju Rangaraju Institute of Engineering and Technology)

CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Drop tables in reverse order of foreign key dependencies if re-running
DROP TABLE IF EXISTS Student_Performance;
DROP TABLE IF EXISTS Grades;
DROP TABLE IF EXISTS Enrollment;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Students;

-- 1. Students Table
CREATE TABLE Students(
  student_id INT PRIMARY KEY,
  name VARCHAR(50),
  class VARCHAR(20),
  email VARCHAR(50),
  phone VARCHAR(15),
  dob DATE
);

-- 2. Courses Table
CREATE TABLE Courses (
  course_id INT PRIMARY KEY,
  course_name VARCHAR(50),
  credits INT,
  instructor VARCHAR(50)
);

-- 3. Enrollment Table
CREATE TABLE Enrollment (
  enroll_id INT PRIMARY KEY,
  student_id INT,
  course_id INT,
  semester VARCHAR(10),
  FOREIGN KEY (student_id) REFERENCES Students(student_id),
  FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

-- 4. Grades Table
CREATE TABLE Grades (
  grade_id INT PRIMARY KEY,
  enroll_id INT,
  marks INT,
  grade CHAR(2),
  FOREIGN KEY (enroll_id) REFERENCES Enrollment(enroll_id)
);

-- 5. Student Performance Summary Table
CREATE TABLE Student_Performance (
  student_id INT PRIMARY KEY,
  student_name VARCHAR(50),
  avg_marks DECIMAL(5,2)
);

-- Initial Data Seeding
INSERT INTO Students VALUES
(1,'Rahul Sharma','CSE-A','rahul@griet.in','9876543210','2004-05-10'),
(2,'Ananya Rao','CSE-A','ananya@griet.in','8765432109','2003-09-14'),
(3,'Kiran Reddy','CSE-B','kiran@griet.in','9988776655','2004-01-25'),
(4,'Sneha Patel','CSE-B','sneha@griet.in','9876123456','2003-07-30');

INSERT INTO Courses VALUES
(101,'Database Systems',4,'Dr. Ramesh'),
(102,'Operating Systems',3,'Prof. Lakshmi'),
(103,'Computer Networks',3,'Dr. Anil Kumar'),
(104,'Software Engineering',4,'Prof. Kavitha');

INSERT INTO Enrollment VALUES
(1,1,101,'Sem-5'),
(2,2,102,'Sem-5'),
(3,3,103,'Sem-5'),
(4,4,104,'Sem-5'),
(5,1,102,'Sem-5'),
(6,2,101,'Sem-5');

INSERT INTO Grades VALUES
(1,1,92,'A'),
(2,2,85,'B'),
(3,3,78,'C'),
(4,4,88,'B'),
(5,5,90,'A'),
(6,6,80,'B');

-- Populate Student_Performance Table
INSERT INTO Student_Performance (student_id, student_name, avg_marks)
SELECT s.student_id, s.name, AVG(g.marks) FROM Students s
JOIN Enrollment e ON s.student_id = e.student_id
JOIN Grades g ON g.enroll_id = e.enroll_id
GROUP BY s.student_id, s.name;
