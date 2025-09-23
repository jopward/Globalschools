# models/grades.py
from db.db_setup import get_connection

# ============================
# CRUD للعلامات
# ============================

def add_grade(student_id, subject, grade, exam_type, date, note=None):
    """إضافة علامة جديدة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO student_grades (student_id, subject, grade, exam_type, date, note)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (student_id, subject, grade, exam_type, date, note))
    grade_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return grade_id

def get_grade_by_id(grade_id):
    """جلب علامة واحدة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM student_grades WHERE id=%s", (grade_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_grades_for_student(student_id):
    """جلب جميع علامات طالب معين"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM student_grades
        WHERE student_id=%s
        ORDER BY date DESC
    """, (student_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_grades_by_subject(student_id, subject):
    """جلب علامات مادة معينة لطالب"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM student_grades
        WHERE student_id=%s AND subject=%s
        ORDER BY date DESC
    """, (student_id, subject))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def update_grade(grade_id, grade=None, exam_type=None, note=None):
    """تحديث علامة"""
    conn = get_connection()
    cur = conn.cursor()
    updates, values = [], []

    if grade is not None:
        updates.append("grade=%s")
        values.append(grade)
    if exam_type:
        updates.append("exam_type=%s")
        values.append(exam_type)
    if note:
        updates.append("note=%s")
        values.append(note)

    if updates:
        query = f"UPDATE student_grades SET {', '.join(updates)} WHERE id=%s"
        values.append(grade_id)
        cur.execute(query, tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    return True

def delete_grade(grade_id):
    """حذف علامة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM student_grades WHERE id=%s", (grade_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True
