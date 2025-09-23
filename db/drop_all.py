# drop_all.py
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "schoolsdb",
    "user": "u0_a223",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def drop_all_tables():
    conn = get_connection()
    cur = conn.cursor()
    tables = [
        "student_grades",
        "student_tracking",
        "class_subjects",
        "teacher_subjects",
        "subjects",
        "class_teachers",
        "students",
        "teacher_classes",
        "users",
        "schools"
    ]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    conn.commit()
    cur.close()
    conn.close()
    print("🗑️ تم حذف جميع الجداول القديمة بنجاح")

if __name__ == "__main__":
    drop_all_tables()
