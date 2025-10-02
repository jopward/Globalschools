# db/db_setup.p
from .db_connection import get_connection
from werkzeug.security import generate_password_hash

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # --- جدول المدارس ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        id SERIAL PRIMARY KEY,
        school_name TEXT NOT NULL,
        admin_username TEXT,
        admin_password TEXT
    );
    """)

    # --- جدول المستخدمين ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        school_id INTEGER REFERENCES schools(id)
    );
    """)

    # --- جدول الصفوف ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_classes (
        id SERIAL PRIMARY KEY,
        class_name TEXT NOT NULL,
        section TEXT,
        period TEXT DEFAULT 'صباحي',
        school_id INTEGER REFERENCES schools(id)
    );
    """)

    # --- جدول الطلاب ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        student_name TEXT NOT NULL,
        school_id INTEGER REFERENCES schools(id),
        class_id INTEGER REFERENCES teacher_classes(id)
    );
    """)

    # --- جدول المواد ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id SERIAL PRIMARY KEY,
        subject_name TEXT NOT NULL UNIQUE
    );
    """)

    # --- جدول ربط الصف بالمادة والمعلم ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_subjects (
        id SERIAL PRIMARY KEY,
        class_id INTEGER REFERENCES teacher_classes(id) ON DELETE CASCADE,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(class_id, subject_id, teacher_id)
    );
    """)

    # --- جدول تتبع الطالب ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_tracking (
        id SERIAL PRIMARY KEY,
        student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
        tracking_date DATE NOT NULL,
        note TEXT
    );
    """)

    # --- جدول علامات الطلاب ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_grades (
        id SERIAL PRIMARY KEY,
        student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
        class_subject_id INTEGER REFERENCES class_subjects(id) ON DELETE CASCADE,
        grade NUMERIC
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ تم إنشاء جميع الجداول بنجاح")

def seed_superadmin():
    conn = get_connection()
    cur = conn.cursor()
    hashed_pw = generate_password_hash("12345")
    cur.execute("""
        INSERT INTO users (name, username, password, role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
    """, ("Super Admin", "superadmin", hashed_pw, "superadmin"))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ تم إضافة السوبر أدمن بنجاح")

if __name__ == "__main__":
    create_tables()
    seed_superadmin()
