# seed.py
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
import random
from datetime import date
from db_setup import get_connection

def seed_data():
    conn = get_connection()
    cur = conn.cursor()

    # --- المدارس ---
    schools = [
        ("مدرسة النور", "admin_nour", "1234"),
        ("مدرسة الأمل", "admin_amal", "1234")
    ]
    school_ids = []
    for name, admin_user, admin_pw in schools:
        hashed_pw = generate_password_hash(admin_pw)
        cur.execute("""
            INSERT INTO schools (school_name, admin_username, admin_password)
            VALUES (%s, %s, %s) RETURNING id
        """, (name, admin_user, hashed_pw))
        school_ids.append(cur.fetchone()['id'])

    # --- المدراء ---
    for idx, s_id in enumerate(school_ids):
        cur.execute("""
            INSERT INTO users (name, username, password, role, school_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (f"Admin {idx+1}", f"admin{idx+1}", generate_password_hash("1234"), "admin", s_id))

    # --- المعلمين ---
    teachers = [
        ("أحمد","ahmed",0),
        ("سعاد","suad",0),
        ("محمود","mahmoud",1),
        ("منى","mona",1)
    ]
    teacher_ids = []
    for t_name, username, s_idx in teachers:
        cur.execute("""
            INSERT INTO users (name, username, password, role, school_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (t_name, username, generate_password_hash("123"), "teacher", school_ids[s_idx]))
        teacher_ids.append(cur.fetchone()['id'])

    # --- الصفوف ---
    classes = [
        ("الصف السابع","أ",school_ids[0]),
        ("الصف الثامن","ب",school_ids[1])
    ]
    class_ids = []
    for class_name, section, s_id in classes:
        cur.execute("""
            INSERT INTO teacher_classes (class_name, section, school_id)
            VALUES (%s, %s, %s) RETURNING id
        """, (class_name, section, s_id))
        class_ids.append(cur.fetchone()['id'])

    # --- الطلاب ---
    students = [
        ("طالب 1", class_ids[0], school_ids[0]),
        ("طالب 2", class_ids[0], school_ids[0]),
        ("طالب 3", class_ids[1], school_ids[1])
    ]
    student_ids = []
    for s_name, c_id, s_id in students:
        cur.execute("""
            INSERT INTO students (student_name, class_id, school_id)
            VALUES (%s, %s, %s) RETURNING id
        """, (s_name, c_id, s_id))
        student_ids.append(cur.fetchone()['id'])

    # --- المواد ---
    subjects = ["رياضيات","علوم","لغة عربية"]
    subject_ids = []
    for subj in subjects:
        cur.execute("INSERT INTO subjects (subject_name) VALUES (%s) RETURNING id", (subj,))
        subject_ids.append(cur.fetchone()['id'])

    # --- ربط الصفوف بالمواد والمعلمين ---
    for i, class_id in enumerate(class_ids):
        for j, subject_id in enumerate(subject_ids):
            teacher_id = teacher_ids[i % len(teacher_ids)]
            cur.execute("""
                INSERT INTO class_subjects (class_id, subject_id, teacher_id)
                VALUES (%s, %s, %s)
            """, (class_id, subject_id, teacher_id))

    # --- علامات الطلاب عشوائية ---
    for student_id in student_ids:
        for class_subject_id in range(1, len(class_ids)*len(subject_ids)+1):
            cur.execute("""
                INSERT INTO student_grades (student_id, class_subject_id, grade)
                VALUES (%s, %s, %s)
            """, (student_id, class_subject_id, random.randint(50,100)))

    # --- تتبع الطلاب (Tracking) ---
    for student_id in student_ids:
        for _ in range(2):  # مثال: سجلين متابعة لكل طالب
            cur.execute("""
                INSERT INTO student_tracking (student_id, tracking_date, note)
                VALUES (%s, %s, %s)
            """, (student_id, date.today(), "ملاحظة متابعة"))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ تم إضافة جميع البيانات الوهمية بنجاح")

if __name__ == "__main__":
    seed_data()
