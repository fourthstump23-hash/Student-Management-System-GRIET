"""
Database Management Module for GRIET Student Management System
Handles connection pooling, query execution, error handling (including Foreign Key constraints),
and schema initialization.
"""

import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "varshit07")
DB_NAME = os.getenv("DB_NAME", "student_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))


def get_db_connection(use_database=True):
    """
    Establish and return a connection to the MySQL database.
    Automatically enables TLS/SSL encryption when connecting to Cloud MySQL (e.g. TiDB Cloud, Aiven).
    """
    config = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "port": DB_PORT,
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
        "autocommit": False
    }

    # If connecting to a cloud database (not localhost), configure SSL seamlessly
    if DB_HOST not in ("localhost", "127.0.0.1"):
        config["ssl_disabled"] = False
        ca_path = os.getenv("DB_SSL_CA")
        if ca_path and os.path.exists(ca_path):
            config["ssl_ca"] = ca_path
            config["ssl_verify_cert"] = True
        elif os.path.exists("/etc/ssl/certs/ca-certificates.crt"):
            # Standard Linux CA bundle (used by Vercel)
            config["ssl_ca"] = "/etc/ssl/certs/ca-certificates.crt"
            config["ssl_verify_cert"] = True
        elif os.path.exists("/etc/pki/tls/certs/ca-bundle.crt"):
            # Amazon Linux / RedHat CA bundle
            config["ssl_ca"] = "/etc/pki/tls/certs/ca-bundle.crt"
            config["ssl_verify_cert"] = True
        else:
            # Fallback: SSL encrypted connection without local CA file requirement
            config["ssl_verify_cert"] = False

    if use_database:
        config["database"] = DB_NAME

    return mysql.connector.connect(**config)


def parse_db_error(err):
    """
    Map MySQL error numbers to friendly, human-readable explanations.
    Especially handles Foreign Key violations (1451, 1452) and duplicate keys (1062).
    """
    errno = getattr(err, "errno", None)
    msg = str(err)

    if errno == errorcode.ER_ROW_IS_REFERENCED_2 or errno == 1451:
        return (
            "Foreign Key Constraint Violation: Cannot delete or update this record because "
            "it is actively referenced in related records (e.g., active enrollments or recorded grades). "
            "Please delete the dependent records first."
        )
    elif errno == errorcode.ER_NO_REFERENCED_ROW_2 or errno == 1452:
        return (
            "Foreign Key Constraint Violation: Cannot add or update record because the referenced "
            "Student ID or Course ID does not exist in the parent table."
        )
    elif errno == errorcode.ER_DUP_ENTRY or errno == 1062:
        return (
            "Duplicate Entry Error: A record with this Primary Key or unique identifier already exists. "
            "Please choose a unique ID."
        )
    elif errno == 1049:
        return f"Unknown database '{DB_NAME}'. Please run database initialization."
    elif errno == 1045:
        return "Access denied: Invalid MySQL username or password."
    elif errno == 2003:
        return f"Cannot connect to MySQL server on {DB_HOST}:{DB_PORT}. Is MySQL running?"
    else:
        return f"Database Error ({errno or 'General'}): {msg}"


def execute_query(sql, params=None, fetch="all", dictionary=True, commit=False):
    """
    Safely execute a parameterized SQL query.
    
    Args:
        sql (str): SQL statement (with %s placeholders)
        params (tuple or list): Parameters for the query
        fetch (str): 'all', 'one', or 'none'
        dictionary (bool): Return results as dictionaries (column_name -> value)
        commit (bool): Commit transaction after execution
        
    Returns:
        tuple: (data, error_message, rowcount)
    """
    conn = None
    cursor = None
    data = None
    error_msg = None
    rowcount = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=dictionary)
        cursor.execute(sql, params or ())

        if fetch == "all":
            data = cursor.fetchall()
            rowcount = cursor.rowcount
        elif fetch == "one":
            data = cursor.fetchone()
            rowcount = 1 if data else 0
        elif fetch == "none":
            rowcount = cursor.rowcount

        if commit:
            conn.commit()

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        error_msg = parse_db_error(err)
    except Exception as ex:
        if conn:
            conn.rollback()
        error_msg = f"Unexpected error: {str(ex)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data, error_msg, rowcount


def recalculate_student_performance():
    """
    Refresh the Student_Performance summary table using the lab formula:
    INSERT INTO Student_Performance (student_id, student_name, avg_marks)
    SELECT s.student_id, s.name, AVG(g.marks) FROM Students s
    JOIN Enrollment e ON s.student_id = e.student_id
    JOIN Grades g ON g.enroll_id = e.enroll_id
    GROUP BY s.student_id, s.name;
    """
    conn = None
    cursor = None
    error_msg = None
    count = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing performance table
        cursor.execute("DELETE FROM Student_Performance;")
        
        # Recalculate and insert
        insert_sql = """
            INSERT INTO Student_Performance (student_id, student_name, avg_marks)
            SELECT s.student_id, s.name, AVG(g.marks)
            FROM Students s
            JOIN Enrollment e ON s.student_id = e.student_id
            JOIN Grades g ON g.enroll_id = e.enroll_id
            GROUP BY s.student_id, s.name;
        """
        cursor.execute(insert_sql)
        count = cursor.rowcount
        conn.commit()
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        error_msg = parse_db_error(err)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return count, error_msg


def init_db(schema_path="schema.sql"):
    """
    Initialize database schema and seed data from schema.sql.
    """
    if not os.path.isabs(schema_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, schema_path)

    if not os.path.exists(schema_path):
        return False, f"Schema file not found at {schema_path}"

    try:
        # First connect without specifying database to create database if not exists
        conn = get_db_connection(use_database=False)
        cursor = conn.cursor()

        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Execute statements separated by semicolons
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
        for stmt in statements:
            cursor.execute(stmt)

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Database initialized and seeded successfully."
    except mysql.connector.Error as err:
        return False, parse_db_error(err)
    except Exception as ex:
        return False, str(ex)
