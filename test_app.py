"""
Automated Verification Test Suite for GRIET Student Management System
Tests all routes, SQL queries, Chart.js data, CRUD workflows, and foreign key handling.
"""

import unittest
import html
from app import app
import db

class TestGRIETStudentManagementSystem(unittest.TestCase):

    def setUp(self):
        # Configure test client
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_dashboard_and_averages(self):
        """Verify dashboard route and exact course averages on first run."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        
        # Verify GRIET header
        self.assertIn("Student Management System - GRIET", html)
        self.assertIn("Database Systems", html)
        self.assertIn("Operating Systems", html)
        self.assertIn("Computer Networks", html)
        self.assertIn("Software Engineering", html)
        
        # Verify query used box
        self.assertIn("SELECT c.course_name AS Course, AVG(g.marks) AS Average_Marks", html)

        # Check DB averages directly
        chart_sql = """
            SELECT c.course_name AS Course, AVG(g.marks) AS Average_Marks
            FROM Grades g
            JOIN Enrollment e ON g.enroll_id = e.enroll_id
            JOIN Courses c ON e.course_id = c.course_id
            GROUP BY c.course_name;
        """
        rows, err, _ = db.execute_query(chart_sql)
        self.assertIsNone(err)
        avg_dict = {r["Course"]: float(r["Average_Marks"]) for r in rows}

        print("\n--- Verified Course Averages ---")
        for course, avg in avg_dict.items():
            print(f"  {course}: {avg}")

        self.assertAlmostEqual(avg_dict["Database Systems"], 86.0, places=1)
        self.assertAlmostEqual(avg_dict["Operating Systems"], 87.5, places=1)
        self.assertAlmostEqual(avg_dict["Computer Networks"], 78.0, places=1)
        self.assertAlmostEqual(avg_dict["Software Engineering"], 88.0, places=1)

    def test_02_students_page_and_crud(self):
        """Verify students page, query box, add, edit, foreign key protection, delete."""
        res = self.client.get("/students")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("SELECT * FROM Students;", html)
        self.assertIn("Rahul Sharma", html)

        # Test Add Student (ID: 99)
        add_res = self.client.post("/students/add", data={
            "student_id": 99,
            "name": "Test Student",
            "class": "CSE-C",
            "email": "test@griet.in",
            "phone": "9123456789",
            "dob": "2004-12-01"
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn("Test Student", add_res.data.decode("utf-8"))

        # Test Edit Student
        edit_res = self.client.post("/students/edit/99", data={
            "name": "Test Student Updated",
            "class": "CSE-C",
            "email": "test_upd@griet.in",
            "phone": "9123456789",
            "dob": "2004-12-01"
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn("Test Student Updated", edit_res.data.decode("utf-8"))

        # Test Foreign Key Protection: Deleting Student #1 who has enrollments
        fk_del_res = self.client.post("/students/delete/1", follow_redirects=True)
        fk_html = fk_del_res.data.decode("utf-8")
        # Should show friendly foreign key message
        self.assertTrue(
            "Foreign Key Constraint" in fk_html or "Cannot delete" in fk_html,
            "Friendly Foreign Key error message should be displayed."
        )

        # Test Clean Delete of un-enrolled Student #99
        del_res = self.client.post("/students/delete/99", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIn("deleted successfully", del_res.data.decode("utf-8"))

    def test_03_courses_page(self):
        """Verify courses page, query box, add and delete course."""
        res = self.client.get("/courses")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("SELECT * FROM Courses;", html)
        self.assertIn("Database Systems", html)

        # Add course 109
        add_res = self.client.post("/courses/add", data={
            "course_id": 109,
            "course_name": "Artificial Intelligence",
            "credits": 4,
            "instructor": "Dr. Pradeep"
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn("Artificial Intelligence", add_res.data.decode("utf-8"))

        # Delete course 109
        del_res = self.client.post("/courses/delete/109", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIn("deleted successfully", del_res.data.decode("utf-8"))

    def test_04_enrollments_page(self):
        """Verify enrollments page and exact JOIN query."""
        res = self.client.get("/enrollments")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("SELECT s.name AS StudentName, c.course_name AS Course, e.semester", html)
        self.assertIn("Rahul Sharma", html)
        self.assertIn("Sem-5", html)

    def test_05_grades_page(self):
        """Verify grades page and exact query with ORDER BY."""
        res = self.client.get("/grades")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("SELECT s.name AS StudentName, c.course_name AS Course, g.marks, g.grade", html)
        self.assertIn("ORDER BY s.name", html)

    def test_06_reports_all_8_tabs(self):
        """Verify every one of the 8 reports runs its exact required query without error."""
        tabs = [
            ("course_avg", "Average marks per course", "SELECT c.course_name AS Course, AVG(g.marks) AS Average_Marks"),
            ("top_performers", "Top performers (marks > 85)", "WHERE g.marks > 85"),
            ("courses_per_student", "Courses per student", "COUNT(e.course_id) AS Total_Courses"),
            ("grade_a", "Students with grade 'A'", "WHERE g.grade = 'A'"),
            ("student_avg", "Average marks per student (ranked)", "ORDER BY AvgMarks DESC"),
            ("course_enrollment", "Enrollment count per course (LEFT JOIN)", "LEFT JOIN Enrollment e"),
            ("student_performance", "Student_Performance table", "SELECT * FROM Student_Performance;"),
            ("course_101_avg", "Average marks for course 101", "WHERE c.course_id = 101")
        ]

        print("\n--- Verifying All 8 Lab Reports ---")
        for tab_id, desc, sql_snippet in tabs:
            res = self.client.get(f"/reports?tab={tab_id}")
            self.assertEqual(res.status_code, 200, f"Failed for tab {tab_id}")
            page_content = html.unescape(res.data.decode("utf-8"))
            self.assertIn(sql_snippet, page_content, f"SQL snippet '{sql_snippet}' not found in tab {tab_id}")
            print(f"  ✓ Tab '{tab_id}' ({desc}) passed.")

    def test_07_reset_database(self):
        """Verify database reset restores original state."""
        res = self.client.post("/reset-db", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Database has been reset", res.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
