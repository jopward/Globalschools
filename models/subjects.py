# models/subjects.py
from db.db_setup import get_connection

# ============================
# CRUD للمواد الدراسية
# ============================

def create_subject(name, code=None, description=None, school_id=None):
    """إضافة مادة جديدة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subjects (name, code, description, school_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (name, code, description, school_id))
    subject_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return subject_id


def get_subject_by_id(subject_id):
    """جلب مادة باستخدام ID"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE id=%s", (subject_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_all_subjects(school_id=None):
    """جلب جميع المواد (مع خيار التصفية حسب مدرسة)"""
    conn = get_connection()
    cur = conn.cursor()
    if school_id:
        cur.execute("SELECT * FROM subjects WHERE school_id=%s", (school_id,))
    else:
        cur.execute("SELECT * FROM subjects")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_subject(subject_id, name=None, code=None, description=None, school_id=None):
    """تحديث بيانات مادة"""
    conn = get_connection()
    cur = conn.cursor()
    updates, values = [], []

    if name:
        updates.append("name=%s")
        values.append(name)
    if code:
        updates.append("code=%s")
        values.append(code)
    if description:
        updates.append("description=%s")
        values.append(description)
    if school_id:
        updates.append("school_id=%s")
        values.append(school_id)

    if updates:
        query = f"UPDATE subjects SET {', '.join(updates)} WHERE id=%s"
        values.append(subject_id)
        cur.execute(query, tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    return True


def delete_subject(subject_id):
    """حذف مادة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM subjects WHERE id=%s", (subject_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True
