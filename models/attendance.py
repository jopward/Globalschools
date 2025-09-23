# models/attendance.py
from db.db_setup import get_connection

# ============================
# CRUD للحضور والغياب
# ============================

def add_attendance(student_id, class_id, date, status, note=None):
    """إضافة سجل حضور / غياب"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO attendance (student_id, class_id, date, status, note)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (student_id, class_id, date, status, note))
    att_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return att_id

def get_attendance_by_id(att_id):
    """جلب سجل حضور واحد"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance WHERE id=%s", (att_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_attendance_for_student(student_id, limit=50, offset=0):
    """جلب حضور طالب معين"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM attendance
        WHERE student_id=%s
        ORDER BY date DESC
        LIMIT %s OFFSET %s
    """, (student_id, limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_attendance_for_class(class_id, date):
    """جلب حضور صف كامل في يوم معين"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, s.student_name
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.class_id=%s AND a.date=%s
    """, (class_id, date))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def update_attendance(att_id, status=None, note=None):
    """تحديث حالة حضور"""
    conn = get_connection()
    cur = conn.cursor()
    updates, values = [], []

    if status:
        updates.append("status=%s")
        values.append(status)
    if note:
        updates.append("note=%s")
        values.append(note)

    if updates:
        query = f"UPDATE attendance SET {', '.join(updates)} WHERE id=%s"
        values.append(att_id)
        cur.execute(query, tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    return True

def delete_attendance(att_id):
    """حذف سجل حضور"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance WHERE id=%s", (att_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True
