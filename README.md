# Student Management System - GRIET
### Department of Computer Science & Engineering &bull; DBMS Laboratory Project
**Gokaraju Rangaraju Institute of Engineering and Technology (GRIET)**

A complete, full-stack **Student Management System (SMS)** web application designed for the Database Management Systems (DBMS) laboratory curriculum. Built with **Python Flask**, **MySQL (via `mysql-connector-python`)**, and a modern, responsive frontend powered by **HTML5, CSS3, JavaScript, Jinja2 templates, and Chart.js**.

---

## 🏛️ Project Features

- **College Branding**: Official site header configured as `"Student Management System - GRIET"`.
- **Dashboard Analytics**:
  - Live metric counters for Students, Courses, Enrollments, and Grades.
  - Interactive **Chart.js** visualization displaying average marks per course.
  - **First-run verification**: Matches expected baseline averages (*Database Systems: 86.0*, *Operating Systems: 87.5*, *Computer Networks: 78.0*, *Software Engineering: 88.0*).
- **Full CRUD Management**:
  - **Students**: Create, View, Edit, and Delete student records (`SELECT * FROM Students;`).
  - **Courses**: Create, View, Edit, and Delete academic courses (`SELECT * FROM Courses;`).
  - **Enrollments**: Enroll students in courses with semester tracking (`INNER JOIN` between Students, Courses, and Enrollment).
  - **Grades**: Record marks and letter grades, with automatic performance synchronization.
- **Foreign Key Constraint Enforcement**:
  - Foreign keys are strictly enforced across `Enrollment` and `Grades`.
  - User-friendly alert banners with actionable explanations (e.g., attempting to delete a student with active enrollments or courses with registered students will not crash; it displays a friendly MySQL Error 1451 handler).
- **SQL Lab Demonstration Boxes**:
  - Every page and report features an interactive, styled code panel displaying the exact SQL query executed, with a one-click **Copy SQL** button for lab viva demonstrations.
- **Client-Side Live Search**:
  - Real-time search filters on every table across all columns with zero latency.
- **Analytical Lab Reports (8 Queries)**:
  - Dedicated tabbed interface executing all 8 required lab queries:
    1. **Course Averages** (`JOIN` + `GROUP BY`): Average marks per course.
    2. **Top Performers** (`WHERE marks > 85 ORDER BY marks DESC`): High-scoring students.
    3. **Courses per Student** (`COUNT()` + `GROUP BY`): Course load per student.
    4. **Grade 'A' Achievers** (`WHERE grade = 'A'`): High-grade filtering.
    5. **Student Averages Ranked** (`AVG()` + `ORDER BY AvgMarks DESC`): Comprehensive student ranking.
    6. **Course Enrollment Count** (`LEFT JOIN`): Course demand including subjects with 0 students.
    7. **Student Performance Summary Table** (`SELECT * FROM Student_Performance;`): Persistent summary table with recalculation button.
    8. **Course 101 Average**: Targeted evaluation for *Database Systems (Course 101)*.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ / Flask 3.x
- **Database**: MySQL Server 8.0+ / `mysql-connector-python`
- **Frontend**: HTML5, Modern CSS3 (Grid & Flexbox), Vanilla JavaScript (ES6+)
- **Templating**: Jinja2
- **Data Visualization**: Chart.js 4.4
- **Security**: 100% Parameterized queries (`%s` placeholders) to prevent SQL Injection

---

## 📂 Project Structure

```
GRRR DBMS/
├── app.py                 # Main Flask application and URL routing
├── db.py                  # Database connection, query helper, and error handler
├── schema.sql             # MySQL DDL & DML initialization script
├── requirements.txt       # Python package dependencies
├── test_app.py            # Automated unit and integration test suite
├── .env                   # Local database configuration (credentials)
├── .env.example           # Configuration template
├── static/
│   ├── css/
│   │   └── style.css      # Custom modern stylesheet with GRIET colors
│   └── js/
│       └── main.js        # Live search, modal toggles, auto-grading, copy SQL
├── templates/
│   ├── base.html          # Base layout with sidebar and GRIET header
│   ├── dashboard.html     # Dashboard with metrics, Chart.js, and quick preview
│   ├── students.html      # Students management table and modals
│   ├── courses.html       # Course catalog management table and modals
│   ├── enrollments.html   # Student course enrollment table and form
│   ├── grades.html        # Academic grading table and form
│   └── reports.html       # 8 Analytical Lab Reports with tab navigation
└── README.md              # Project documentation and setup guide
```

---

## ⚙️ Prerequisites

1. **Python 3.10 or higher**: [Download Python](https://www.python.org/downloads/)
2. **MySQL Server 8.0+**: [Download MySQL Community Server](https://dev.mysql.com/downloads/mysql/)

---

## 🚀 Setup & Execution Guide

### Step 1: Clone or Navigate to the Workspace
Open a terminal (PowerShell, Command Prompt, or Bash) in this project directory:
```bash
cd "c:\Users\mekal\OneDrive\Documents\GRRR DBMS"
```

### Step 2: Install Python Dependencies
Install Flask, mysql-connector-python, and python-dotenv:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Database Credentials
A `.env` file has been provided in the root directory. Adjust your MySQL credentials if necessary:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=varshit07
DB_NAME=student_db
DB_PORT=3306
SECRET_KEY=griet-dbms-lab-sms-secretkey-2026
```

### Step 4: Initialize the Database (MySQL)
Run `schema.sql` to create `student_db` and insert the initial lab dataset:

**Using MySQL CLI:**
```powershell
Get-Content schema.sql | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pvarshit07
```
*(Or inside MySQL Workbench: File &rarr; Open SQL Script &rarr; `schema.sql` &rarr; Execute All).*

### Step 5: Start the Flask Application
Run the Flask server:
```bash
python app.py
```

You should see:
```text
Connecting to MySQL Database...
Connected to MySQL Database successfully.
Starting GRIET Student Management System on http://127.0.0.1:5000 ...
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 6: Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Verification & Lab Viva Demonstration

### 1. Automated Test Suite
To automatically verify that all 7 test suites pass, all 8 lab queries execute accurately, and course averages match baseline values:
```bash
python test_app.py
```
**Expected Output:**
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.615s

OK

--- Verified Course Averages ---
  Database Systems: 86.0
  Operating Systems: 87.5
  Computer Networks: 78.0
  Software Engineering: 88.0

--- Verifying All 8 Lab Reports ---
  ✓ Tab 'course_avg' (Average marks per course) passed.
  ✓ Tab 'top_performers' (Top performers (marks > 85)) passed.
  ✓ Tab 'courses_per_student' (Courses per student) passed.
  ✓ Tab 'grade_a' (Students with grade 'A') passed.
  ✓ Tab 'student_avg' (Average marks per student (ranked)) passed.
  ✓ Tab 'course_enrollment' (Enrollment count per course (LEFT JOIN)) passed.
  ✓ Tab 'student_performance' (Student_Performance table) passed.
  ✓ Tab 'course_101_avg' (Average marks for course 101) passed.
```

### 2. Demonstrating Foreign Key Protection
- Navigate to **Students** (`/students`).
- Try clicking **Delete** on student **Rahul Sharma (ID: 1)**.
- **Observation**: The system safely intercepts MySQL Error 1451 and displays a user-friendly alert:
  > *"Foreign Key Constraint Violation: Cannot delete or update this record because it is actively referenced in related records (e.g., active enrollments or recorded grades). Please delete the dependent records first."*

### 3. Reset Database to Original Seed Data
At any point during testing or viva demonstration, click the **↻ Reset DB** button at the bottom of the sidebar or make a `POST` request to `/reset-db` to restore pristine baseline lab data.

---

## 📊 Database Schema Details

```sql
CREATE TABLE Students(
  student_id INT PRIMARY KEY,
  name VARCHAR(50),
  class VARCHAR(20),
  email VARCHAR(50),
  phone VARCHAR(15),
  dob DATE
);

CREATE TABLE Courses (
  course_id INT PRIMARY KEY,
  course_name VARCHAR(50),
  credits INT,
  instructor VARCHAR(50)
);

CREATE TABLE Enrollment (
  enroll_id INT PRIMARY KEY,
  student_id INT,
  course_id INT,
  semester VARCHAR(10),
  FOREIGN KEY (student_id) REFERENCES Students(student_id),
  FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE Grades (
  grade_id INT PRIMARY KEY,
  enroll_id INT,
  marks INT,
  grade CHAR(2),
  FOREIGN KEY (enroll_id) REFERENCES Enrollment(enroll_id)
);

CREATE TABLE Student_Performance (
  student_id INT PRIMARY KEY,
  student_name VARCHAR(50),
  avg_marks DECIMAL(5,2)
);
```

---

*GRIET CSE Department &bull; DBMS Laboratory Project*
