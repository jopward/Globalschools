# models/tracking.py
from db.db_setup import get_connection

# ============================
# CRUD لتتبع الطلاب
# ============================

def add_tracking(student_id, note, created_by=None):
    """إضافة ملاحظة / متابعة جديدة لطالب"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO student_tracking (student_id, note, created_by)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (student_id, note, created_by))
    tid = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return tid

def get_tracking_by_id(track_id):
    """جلب متابعة واحدة حسب ID"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM student_tracking WHERE id=%s", (track_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_tracking_for_student(student_id, limit=50, offset=0):
    """جلب جميع المتابعات لطالب معيّن"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT st.*, u.name AS created_by_name
        FROM student_tracking st
        LEFT JOIN users u ON st.created_by = u.id
        WHERE st.student_id=%s
        ORDER BY st.id DESC
        LIMIT %s OFFSET %s
    """, (student_id, limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def update_tracking(track_id, note=None):
    """تحديث ملاحظة متابعة"""
    conn = get_connection()
    cur = conn.cursor()
    if note:
        cur.execute("UPDATE student_tracking SET note=%s WHERE id=%s", (note, track_id))
        conn.commit()
    cur.close()
    conn.close()
    return True

def delete_tracking(track_id):
    """حذف متابعة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM student_tracking WHERE id=%s", (track_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True
