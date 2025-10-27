from db.db_setup import get_connection
import psycopg2.extras
from datetime import date

# ============================================================
# 🧩 Model: student_tracking — إدارة الحضور والغياب
# ============================================================

def add_attendance(student_id, school_id, teacher_id, date_val=None, attendance=None, note=None):
    """
    ➕ إضافة سجل حضور جديد
    """
    if not student_id or not school_id or not teacher_id:
        raise ValueError("student_id و school_id و teacher_id مطلوبة.")

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    date_val = date_val or date.today().isoformat()

    try:
        cur.execute("""
            INSERT INTO student_tracking (student_id, school_id, teacher_id, date, attendance, note)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (student_id, school_id, teacher_id, date_val, attendance, note))
        
        result = cur.fetchone()
        conn.commit()
        print(f"✅ تم الإدخال بنجاح، tracking_id = {result['id']}")
        return result["id"]

    except Exception as e:
        conn.rollback()
        print("❌ خطأ أثناء الإضافة إلى student_tracking:", e)
        return None
    finally:
        cur.close()
        conn.close()


def get_attendance_by_id(att_id):
    """
    📄 جلب سجل حضور واحد
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM student_tracking WHERE id=%s", (att_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_attendance_for_student(student_id, limit=50):
    """
    📚 جلب آخر سجلات حضور طالب معين
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT * FROM student_tracking
        WHERE student_id=%s
        ORDER BY date DESC
        LIMIT %s
    """, (student_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_attendance_for_date(school_id, date_val):
    """
    📅 جلب كل الحضور في تاريخ معين لمدرسة محددة
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT st.*, s.student_name, u.name AS teacher_name
        FROM student_tracking st
        LEFT JOIN students s ON st.student_id = s.id
        LEFT JOIN users u ON st.teacher_id = u.id
        WHERE st.school_id=%s AND st.date=%s
        ORDER BY s.student_name
    """, (school_id, date_val))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_attendance(att_id, attendance=None, note=None):
    """
    ✏️ تحديث حالة الحضور / الملاحظة
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    updates, values = [], []
    if attendance:
        updates.append("attendance=%s")
        values.append(attendance)
    if note:
        updates.append("note=%s")
        values.append(note)

    if not updates:
        return False

    query = f"UPDATE student_tracking SET {', '.join(updates)} WHERE id=%s RETURNING id"
    values.append(att_id)

    try:
        cur.execute(query, tuple(values))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("❌ خطأ أثناء التحديث:", e)
        return False
    finally:
        cur.close()
        conn.close()


def delete_attendance(att_id):
    """
    🗑️ حذف سجل حضور معين
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("DELETE FROM student_tracking WHERE id=%s RETURNING id", (att_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("❌ خطأ أثناء الحذف:", e)
        return False
    finally:
        cur.close()
        conn.close()


def filter_attendance(school_id=None, student_id=None, start_date=None, end_date=None):
    """
    🔍 فلترة حسب المدرسة أو الطالب أو الفترة الزمنية
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """
        SELECT st.*, s.student_name, u.name AS teacher_name
        FROM student_tracking st
        LEFT JOIN students s ON st.student_id = s.id
        LEFT JOIN users u ON st.teacher_id = u.id
        WHERE 1=1
    """
    params = []

    if school_id:
        query += " AND st.school_id=%s"
        params.append(school_id)
    if student_id:
        query += " AND st.student_id=%s"
        params.append(student_id)
    if start_date and end_date:
        query += " AND st.date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date:
        query += " AND st.date >= %s"
        params.append(start_date)
    elif end_date:
        query += " AND st.date <= %s"
        params.append(end_date)

    query += " ORDER BY st.date DESC"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
