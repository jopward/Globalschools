# models/class_subjects.py
from db.db_setup import get_connection

# ============================
# CRUD + عمليات البحث والفلترة
# ============================

def add_class_subject(class_id, subject_id, teacher_id):
    """إضافة ربط بين صف ومادة ومعلم"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO class_subjects (class_id, subject_id, teacher_id)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (class_id, subject_id, teacher_id))
    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return new_id


def get_class_subject_by_id(cs_id):
    """جلب ربط واحد حسب ID"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM class_subjects WHERE id = %s", (cs_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result


def get_all_class_subjects():
    """جلب جميع الروابط (صف + مادة + معلم)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT cs.id, c.class_name, s.subject_name, u.name AS teacher_name
        FROM class_subjects cs
        JOIN teacher_classes c ON cs.class_id = c.id
        JOIN subjects s ON cs.subject_id = s.id
        JOIN users u ON cs.teacher_id = u.id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_class_subject(cs_id, class_id=None, subject_id=None, teacher_id=None):
    """تحديث بيانات ربط صف + مادة + معلم"""
    conn = get_connection()
    cur = conn.cursor()
    updates, values = [], []

    if class_id:
        updates.append("class_id=%s")
        values.append(class_id)
    if subject_id:
        updates.append("subject_id=%s")
        values.append(subject_id)
    if teacher_id:
        updates.append("teacher_id=%s")
        values.append(teacher_id)

    if updates:
        query = f"UPDATE class_subjects SET {', '.join(updates)} WHERE id=%s"
        values.append(cs_id)
        cur.execute(query, tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    return True


def delete_class_subject(cs_id):
    """حذف ربط معين"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM class_subjects WHERE id=%s", (cs_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True
