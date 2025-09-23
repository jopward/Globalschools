# reset_data.py
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

def reset_data():
    conn = get_connection()
    cur = conn.cursor()

    tables = [
        "student_grades",
        "student_tracking",
        "class_subjects",
        "students",
        "teacher_classes",
        "subjects",
        "users",
        "schools"
    ]

    for table in tables:
        cur.execute(f"DELETE FROM {table};")
        cur.execute(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1;")  # إعادة ترقيم الـID تلقائياً

    conn.commit()
    cur.close()
    conn.close()
    print("♻️ تم حذف جميع البيانات الوهمية وبقيت الجداول موجودة")

if __name__ == "__main__":
    reset_data()
