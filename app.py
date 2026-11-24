"""
GRIET Student Management System - Flask Application
Department of Computer Science & Engineering, DBMS Laboratory
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "griet-dbms-sms-lab-secretkey-2026")


# ==============================================================================
# 1. Dashboard Route
# ==============================================================================
@app.route("/")
@app.route("/dashboard")
def dashboard():
    """
    Dashboard displaying total counts, top performers, and course average marks
    rendered with Chart.js.
    """
    # 1. Aggregate counts
    student_res, _, _ = db.execute_query("SELECT COUNT(*) AS total FROM Students;")
    course_res, _, _ = db.execute_query("SELECT COUNT(*) AS total FROM Courses;")
    enroll_res, _, _ = db.execute_query("SELECT COUNT(*) AS total FROM Enrollment;")
    grade_res, _, _ = db.execute_query("SELECT COUNT(*) AS total FROM Grades;")

    student_count = student_res[0]["total"] if student_res else 0
    course_count = course_res[0]["total"] if course_res else 0
    enrollment_count = enroll_res[0]["total"] if enroll_res else 0
    grade_count = grade_res[0]["total"] if grade_res else 0

    # 2. Average marks per course query
    chart_sql = """
        SELECT c.course_name AS Course, AVG(g.marks) AS Average_Marks
        FROM Grades g
        JOIN Enrollment e ON g.enroll_id = e.enroll_id
        JOIN Courses c ON e.course_id = c.course_id
        GROUP BY c.course_name;
    """
    course_averages, err, _ = db.execute_query(chart_sql)
    if err:
        flash(f"Error fetching course averages: {err}", "error")
        course_averages = []

    # Chart.js dataset formatting
    chart_labels = [row["Course"] for row in course_averages]
    chart_data = [float(row["Average_Marks"]) for row in course_averages]

    # 3. Top performers preview (marks > 85)
    top_sql = """
        SELECT s.name AS Student, c.course_name AS Course, g.marks, g.grade
        FROM Grades g
        JOIN Enrollment e ON g.enroll_id = e.enroll_id
        JOIN Students s ON e.student_id = s.student_id
        JOIN Courses c ON e.course_id = c.course_id
        WHERE g.marks > 85
        ORDER BY g.marks DESC;
    """
    top_performers, _, _ = db.execute_query(top_sql)

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        student_count=student_count,
        course_count=course_count,
        enrollment_count=enrollment_count,
        grade_count=grade_count,
        course_averages=course_averages,
        chart_labels=chart_labels,
        chart_data=chart_data,
        top_performers=top_performers or []
    )


# ==============================================================================
# 2. Students Route (CRUD)
# ==============================================================================
@app.route("/students")
def students():
    """
    Displays all students using: SELECT * FROM Students;
    """
    sql = "SELECT * FROM Students ORDER BY student_id ASC;"
    students_data, err, _ = db.execute_query(sql)
    if err:
        flash(err, "error")
        students_data = []

    # Calculate next student ID for convenience
    max_id_res, _, _ = db.execute_query("SELECT MAX(student_id) AS max_id FROM Students;")
    next_student_id = (max_id_res[0]["max_id"] or 0) + 1 if max_id_res else 1

    return render_template(
        "students.html",
        active_page="students",
        students=students_data,
        next_student_id=next_student_id
    )


@app.route("/students/add", methods=["POST"])
def add_student():
    """Add a new student using a parameterized query."""
    student_id = request.form.get("student_id")
    name = request.form.get("name")
    student_class = request.form.get("class")
    email = request.form.get("email")
    phone = request.form.get("phone")
    dob = request.form.get("dob")

    if not all([student_id, name, student_class, email, phone, dob]):
        flash("All student fields are required.", "warning")
        return redirect(url_for("students"))

    sql = """
        INSERT INTO Students (student_id, name, class, email, phone, dob)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    params = (int(student_id), name.strip(), student_class.strip(), email.strip(), phone.strip(), dob)
    _, err, _ = db.execute_query(sql, params, fetch="none", commit=True)

    if err:
        flash(f"Failed to add student: {err}", "error")
    else:
        flash(f"Student '{name}' (ID: {student_id}) added successfully!", "success")

    return redirect(url_for("students"))


@app.route("/students/edit/<int:student_id>", methods=["POST"])
def edit_student(student_id):
    """Update student details using a parameterized query."""
    name = request.form.get("name")
    student_class = request.form.get("class")
    email = request.form.get("email")
    phone = request.form.get("phone")
    dob = request.form.get("dob")

    sql = """
        UPDATE Students
        SET name = %s, class = %s, email = %s, phone = %s, dob = %s
        WHERE student_id = %s;
    """
    params = (name.strip(), student_class.strip(), email.strip(), phone.strip(), dob, student_id)
    _, err, _ = db.execute_query(sql, params, fetch="none", commit=True)

    if err:
        flash(f"Failed to update student: {err}", "error")
    else:
        # Refresh Student_Performance if student name changed
        db.recalculate_student_performance()
        flash(f"Student #{student_id} updated successfully!", "success")

    return redirect(url_for("students"))


@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    """
    Delete student. Foreign key constraints will prevent deleting
    students with active enrollments and provide a user-friendly message.
    """
    sql = "DELETE FROM Students WHERE student_id = %s;"
    _, err, _ = db.execute_query(sql, (student_id,), fetch="none", commit=True)

    if err:
        flash(err, "error")
    else:
        db.recalculate_student_performance()
        flash(f"Student #{student_id} deleted successfully.", "success")

    return redirect(url_for("students"))


# ==============================================================================
# 3. Courses Route (CRUD)
# ==============================================================================
@app.route("/courses")
def courses():
    """
    Displays all courses using: SELECT * FROM Courses;
    """
    sql = "SELECT * FROM Courses ORDER BY course_id ASC;"
    courses_data, err, _ = db.execute_query(sql)
    if err:
        flash(err, "error")
        courses_data = []

    # Next suggested course ID
    max_id_res, _, _ = db.execute_query("SELECT MAX(course_id) AS max_id FROM Courses;")
    next_course_id = (max_id_res[0]["max_id"] or 100) + 1 if max_id_res else 101

    return render_template(
        "courses.html",
        active_page="courses",
        courses=courses_data,
        next_course_id=next_course_id
    )


@app.route("/courses/add", methods=["POST"])
def add_course():
    """Add a new course using a parameterized query."""
    course_id = request.form.get("course_id")
    course_name = request.form.get("course_name")
    credits = request.form.get("credits")
    instructor = request.form.get("instructor")

    if not all([course_id, course_name, credits, instructor]):
        flash("All course fields are required.", "warning")
        return redirect(url_for("courses"))

    sql = """
        INSERT INTO Courses (course_id, course_name, credits, instructor)
        VALUES (%s, %s, %s, %s);
    """
    params = (int(course_id), course_name.strip(), int(credits), instructor.strip())
    _, err, _ = db.execute_query(sql, params, fetch="none", commit=True)

    if err:
        flash(f"Failed to add course: {err}", "error")
    else:
        flash(f"Course '{course_name}' (ID: {course_id}) added successfully!", "success")

    return redirect(url_for("courses"))


@app.route("/courses/edit/<int:course_id>", methods=["POST"])
def edit_course(course_id):
    """Update course details using a parameterized query."""
    course_name = request.form.get("course_name")
    credits = request.form.get("credits")
    instructor = request.form.get("instructor")

    sql = """
        UPDATE Courses
        SET course_name = %s, credits = %s, instructor = %s
        WHERE course_id = %s;
    """
    params = (course_name.strip(), int(credits), instructor.strip(), course_id)
    _, err, _ = db.execute_query(sql, params, fetch="none", commit=True)

    if err:
        flash(f"Failed to update course: {err}", "error")
    else:
        flash(f"Course #{course_id} updated successfully!", "success")

    return redirect(url_for("courses"))


@app.route("/courses/delete/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    """Delete a course. Enforces foreign key constraints."""
    sql = "DELETE FROM Courses WHERE course_id = %s;"
    _, err, _ = db.execute_query(sql, (course_id,), fetch="none", commit=True)

    if err:
        flash(err, "error")
    else:
        flash(f"Course #{course_id} deleted successfully.", "success")

    return redirect(url_for("courses"))


# ==============================================================================
# 4. Enrollments Route (Join + Add/Delete)
# ==============================================================================
@app.route("/enrollments")
def enrollments():
    """
    Displays enrollments using the exact query:
    SELECT s.name AS StudentName, c.course_name AS Course, e.semester
    FROM Enrollment e JOIN Students s ON e.student_id = s.student_id
    JOIN Courses c ON e.course_id = c.course_id;
    (Also includes e.enroll_id to enable row deletion).
    """
    sql = """
        SELECT e.enroll_id, s.name AS StudentName, c.course_name AS Course, e.semester
        FROM Enrollment e
        JOIN Students s ON e.student_id = s.student_id
        JOIN Courses c ON e.course_id = c.course_id
        ORDER BY e.enroll_id ASC;
    """
    enrollments_data, err, _ = db.execute_query(sql)
    if err:
        flash(err, "error")
        enrollments_data = []

    # Dropdown data for student and course
    students_list, _, _ = db.execute_query("SELECT student_id, name, class FROM Students ORDER BY name ASC;")
    courses_list, _, _ = db.execute_query("SELECT course_id, course_name, credits FROM Courses ORDER BY course_name ASC;")

    # Next suggested enrollment ID
    max_id_res, _, _ = db.execute_query("SELECT MAX(enroll_id) AS max_id FROM Enrollment;")
    next_enroll_id = (max_id_res[0]["max_id"] or 0) + 1 if max_id_res else 1

    return render_template(
        "enrollments.html",
        active_page="enrollments",
        enrollments=enrollments_data,
        students_list=students_list or [],
        courses_list=courses_list or [],
        next_enroll_id=next_enroll_id
    )


@app.route("/enrollments/add", methods=["POST"])
def add_enrollment():
    """Enroll student in a course using a parameterized query."""
    enroll_id = request.form.get("enroll_id")
    student_id = request.form.get("student_id")
    course_id = request.form.get("course_id")
    semester = request.form.get("semester")

    if not all([enroll_id, student_id, course_id, semester]):
        flash("All enrollment fields are required.", "warning")
        return redirect(url_for("enrollments"))

    sql = """
        INSERT INTO Enrollment (enroll_id, student_id, course_id, semester)
        VALUES (%s, %s, %s, %s);
    """
    params = (int(enroll_id), int(student_id), int(course_id), semester.strip())
    _, err, _ = db.execute_query(sql, params, fetch="none", commit=True)

    if err:
        flash(f"Enrollment failed: {err}", "error")
    else:
        flash(f"Enrollment #{enroll_id} created successfully!", "success")

    return redirect(url_for("enrollments"))


@app.route("/enrollments/delete/<int:enroll_id>", methods=["POST"])
def delete_enrollment(enroll_id):
    """Delete enrollment. Foreign key constraint protects against deleting if grades exist."""
    sql = "DELETE FROM Enrollment WHERE enroll_id = %s;"
    _, err, _ = db.execute_query(sql, (enroll_id,), fetch="none", commit=True)

    if err:
        flash(err, "error")
    else:
        db.recalculate_student_performance()
        flash(f"Enrollment #{enroll_id} removed successfully.", "success")

    return redirect(url_for("enrollments"))


# ==============================================================================
# 5. Grades Route (Join + Add/Delete)
# ==============================================================================
@app.route("/grades")
def grades():
    """
    Displays grades using the exact query:
    SELECT s.name AS StudentName, c.course_name AS Course, g.marks, g.grade
    FROM Grades g JOIN Enrollment e ON g.enroll_id = e.enroll_id
    JOIN Students s ON e.student_id = s.student_id
    JOIN Courses c ON e.course_id = c.course_id ORDER BY s.name;
    (Includes g.grade_id for management).
    """
    sql = """
        SELECT g.grade_id, s.name AS StudentName, c.course_name AS Course, g.marks, g.grade
        FROM Grades g
        JOIN Enrollment e ON g.enroll_id = e.enroll_id
        JOIN Students s ON e.student_id = s.student_id
        JOIN Courses c ON e.course_id = c.course_id
        ORDER BY s.name ASC;
    """
    grades_data, err, _ = db.execute_query(sql)
    if err:
        flash(err, "error")
        grades_data = []

    # Dropdown of active enrollments for recording a grade
    enroll_list_sql = """
        SELECT e.enroll_id, s.name AS StudentName, c.course_name AS Course, e.semester
        FROM Enrollment e
        JOIN Students s ON e.student_id = s.student_id
        JOIN Courses c ON e.course_id = c.course_id
        ORDER BY s.name ASC;
    """
    enrollments_list, _, _ = db.execute_query(enroll_list_sql)

    # Next suggested Grade ID
    max_id_res, _, _ = db.execute_query("SELECT MAX(grade_id) AS max_id FROM Grades;")
    next_grade_id = (max_id_res[0]["max_id"] or 0) + 1 if max_id_res else 1

    return render_template(
        "grades.html",
        active_page="grades",
        grades=grades_data,
        enrollments_list=enrollments_list or [],
        next_grade_id=next_grade_id
    )


@app.route("/grades/add", methods=["POST"])
def add_grade():
    """Record a grade and automatically synchronize Student_Performance."""
    grade_id = request.form.get("grade_id")
    enroll_id = request.form.get("enroll_id")
    marks = request.form.get("marks")
    grade = request.form.get("grade")

    if not all([grade_id, enroll_id, marks, grade]):
        flash("All grade fields are required.", "warning")
        return redirect(url_for("grades"))

    sql = """
        INSERT INTO Grades (grade_id, enroll_id, marks, grade)
        VALUES (%s, %s, %s, %s);
    """
    params = (int(grade_id), int(enroll_id), int(marks), grade.strip().upper())
    _, err, _ = db.execute_query(sql, params, fetch="none", commit=True)

    if err:
        flash(f"Failed to record grade: {err}", "error")
    else:
        # Automatically update the summary table
        db.recalculate_student_performance()
        flash(f"Grade #{grade_id} recorded successfully and performance summary updated!", "success")

    return redirect(url_for("grades"))


@app.route("/grades/delete/<int:grade_id>", methods=["POST"])
def delete_grade(grade_id):
    """Delete a grade and synchronize Student_Performance."""
    sql = "DELETE FROM Grades WHERE grade_id = %s;"
    _, err, _ = db.execute_query(sql, (grade_id,), fetch="none", commit=True)

    if err:
        flash(err, "error")
    else:
        db.recalculate_student_performance()
        flash(f"Grade #{grade_id} deleted successfully.", "success")

    return redirect(url_for("grades"))


# ==============================================================================
# 6. Reports Route (8 Lab Queries)
# ==============================================================================
REPORTS_CONFIG = {
    "course_avg": {
        "letter": "a",
        "title": "Average Marks per Course",
        "description": "Calculates the average examination score obtained in each course using JOIN and GROUP BY.",
        "sql": """
SELECT c.course_name AS Course, AVG(g.marks) AS Average_Marks
FROM Grades g
JOIN Enrollment e ON g.enroll_id = e.enroll_id
JOIN Courses c ON e.course_id = c.course_id
GROUP BY c.course_name;
        """
    },
    "top_performers": {
        "letter": "b",
        "title": "Top Performers (Marks > 85)",
        "description": "Retrieves high-achieving students scoring above 85 marks, sorted in descending order.",
        "sql": """
SELECT s.name AS Student, c.course_name AS Course, g.marks, g.grade
FROM Grades g
JOIN Enrollment e ON g.enroll_id = e.enroll_id
JOIN Students s ON e.student_id = s.student_id
JOIN Courses c ON e.course_id = c.course_id
WHERE g.marks > 85
ORDER BY g.marks DESC;
        """
    },
    "courses_per_student": {
        "letter": "c",
        "title": "Courses per Student",
        "description": "Counts the total number of subjects each student is currently enrolled in.",
        "sql": """
SELECT s.name AS Student, COUNT(e.course_id) AS Total_Courses
FROM Students s
JOIN Enrollment e ON s.student_id = e.student_id
GROUP BY s.name;
        """
    },
    "grade_a": {
        "letter": "d",
        "title": "Students with Grade 'A'",
        "description": "Filters students who achieved an 'A' grade in any course.",
        "sql": """
SELECT s.name, c.course_name, g.grade
FROM Grades g
JOIN Enrollment e ON g.enroll_id = e.enroll_id
JOIN Students s ON e.student_id = s.student_id
JOIN Courses c ON e.course_id = c.course_id
WHERE g.grade = 'A';
        """
    },
    "student_avg": {
        "letter": "e",
        "title": "Average Marks per Student (Ranked)",
        "description": "Computes overall average marks per student across all enrolled subjects, ranked highest to lowest.",
        "sql": """
SELECT s.name AS Student, AVG(g.marks) AS AvgMarks
FROM Grades g
JOIN Enrollment e ON g.enroll_id = e.enroll_id
JOIN Students s ON e.student_id = s.student_id
GROUP BY s.name
ORDER BY AvgMarks DESC;
        """
    },
    "course_enrollment": {
        "letter": "f",
        "title": "Enrollment Count per Course (LEFT JOIN)",
        "description": "Demonstrates a LEFT OUTER JOIN to list all courses and their student enrollment count, including any course with zero enrollments.",
        "sql": """
SELECT c.course_name, COUNT(e.student_id) AS Enrolled_Students
FROM Courses c
LEFT JOIN Enrollment e ON c.course_id = e.course_id
GROUP BY c.course_name;
        """
    },
    "student_performance": {
        "letter": "g",
        "title": "Student_Performance Summary Table",
        "description": "Reads directly from the persistent Student_Performance aggregation table.",
        "sql": """
SELECT * FROM Student_Performance;
        """
    },
    "course_101_avg": {
        "letter": "h",
        "title": "Average Marks for Course 101 (Database Systems)",
        "description": "Targeted course evaluation filtering specifically for Course ID 101.",
        "sql": """
SELECT c.course_name, AVG(g.marks) AS AverageMarks
FROM Grades g
JOIN Enrollment e ON g.enroll_id = e.enroll_id
JOIN Courses c ON e.course_id = c.course_id
WHERE c.course_id = 101
GROUP BY c.course_name;
        """
    }
}


@app.route("/reports")
def reports():
    """
    Renders the DBMS laboratory analytical reports page with tabs for all 8 queries.
    """
    tab = request.args.get("tab", "course_avg")
    if tab not in REPORTS_CONFIG:
        tab = "course_avg"

    config = REPORTS_CONFIG[tab]
    sql = config["sql"].strip()

    data, err, _ = db.execute_query(sql)
    if err:
        flash(f"Error executing report query: {err}", "error")
        data = []

    columns = list(data[0].keys()) if data else []

    return render_template(
        "reports.html",
        active_page="reports",
        active_tab=tab,
        active_tab_letter=config["letter"],
        active_tab_title=config["title"],
        active_tab_description=config["description"],
        current_query=sql,
        report_data=data or [],
        columns=columns
    )


@app.route("/reports/recalculate-performance", methods=["POST"])
def recalculate_performance():
    """Manually re-run the INSERT INTO Student_Performance query from base tables."""
    count, err = db.recalculate_student_performance()
    if err:
        flash(f"Failed to recalculate performance: {err}", "error")
    else:
        flash(f"Student_Performance table successfully re-calculated ({count} records updated).", "success")
    return redirect(url_for("reports", tab="student_performance"))


# ==============================================================================
# 7. Database Reset / Seed Route
# ==============================================================================
@app.route("/reset-db", methods=["POST"])
def reset_database():
    """Reset database back to original schema.sql specifications."""
    success, msg = db.init_db("schema.sql")
    if success:
        flash("Database has been reset to original GRIET lab schema and seed data!", "success")
    else:
        flash(f"Database reset error: {msg}", "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    # Ensure database is reachable on startup
    print("Connecting to MySQL Database...")
    data, err, _ = db.execute_query("SELECT 1;")
    if err:
        print(f"Warning: Database connection check returned: {err}")
    else:
        print("Connected to MySQL Database successfully.")
        
    print("Starting GRIET Student Management System on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)
