from db.db_setup import get_connection

# ============================
# CRUD للحضور والغياب (student_tracking)
# ============================

def add_attendance(student_id, school_id, teacher_id, date, attendance, note=None):
    """إضافة سجل حضور / غياب"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO student_tracking (student_id, school_id, teacher_id, date, attendance, note)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (student_id, school_id, teacher_id, date, attendance, note))
        
        result = cur.fetchone()
        conn.commit()

        if result and len(result) > 0:
            return result[0]
        else:
            print("⚠️ لم يتم إرجاع أي ID من قاعدة البيانات بعد الإدخال.")
            return None
    except Exception as e:
        conn.rollback()
        print("❌ خطأ أثناء الإضافة:", e)
        return None
    finally:
        cur.close()
        conn.close()


def get_attendance_by_id(att_id):
    """جلب سجل حضور واحد"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM student_tracking WHERE id=%s", (att_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_attendance_for_student(student_id, limit=50, offset=0):
    """جلب حضور طالب معين"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM student_tracking
        WHERE student_id=%s
        ORDER BY date DESC
        LIMIT %s OFFSET %s
    """, (student_id, limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_attendance_for_school(school_id, date=None):
    """جلب حضور مدرسة معينة (اختياري حسب التاريخ)"""
    conn = get_connection()
    cur = conn.cursor()
    if date:
        cur.execute("""
            SELECT st.*, s.student_name, u.name AS teacher_name
            FROM student_tracking st
            LEFT JOIN students s ON st.student_id = s.id
            LEFT JOIN users u ON st.teacher_id = u.id
            WHERE st.school_id=%s AND st.date=%s
        """, (school_id, date))
    else:
        cur.execute("""
            SELECT st.*, s.student_name, u.name AS teacher_name
            FROM student_tracking st
            LEFT JOIN students s ON st.student_id = s.id
            LEFT JOIN users u ON st.teacher_id = u.id
            WHERE st.school_id=%s
        """, (school_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_attendance_for_teacher(teacher_id, date=None):
    """جلب حضور مدرس معين (اختياري حسب التاريخ)"""
    conn = get_connection()
    cur = conn.cursor()
    if date:
        cur.execute("""
            SELECT st.*, s.student_name, u.name AS teacher_name
            FROM student_tracking st
            LEFT JOIN students s ON st.student_id = s.id
            LEFT JOIN users u ON st.teacher_id = u.id
            WHERE st.teacher_id=%s AND st.date=%s
        """, (teacher_id, date))
    else:
        cur.execute("""
            SELECT st.*, s.student_name, u.name AS teacher_name
            FROM student_tracking st
            LEFT JOIN students s ON st.student_id = s.id
            LEFT JOIN users u ON st.teacher_id = u.id
            WHERE st.teacher_id=%s
        """, (teacher_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_attendance_for_student_period(student_id, start_date, end_date):
    """جلب حضور طالب معين خلال فترة زمنية محددة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT st.*, s.student_name, u.name AS teacher_name
        FROM student_tracking st
        LEFT JOIN students s ON st.student_id = s.id
        LEFT JOIN users u ON st.teacher_id = u.id
        WHERE st.student_id=%s AND st.date BETWEEN %s AND %s
        ORDER BY st.date DESC
    """, (student_id, start_date, end_date))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_attendance(att_id, attendance=None, note=None):
    """تحديث حالة حضور"""
    conn = get_connection()
    cur = conn.cursor()
    updates, values = [], []

    if attendance:
        updates.append("attendance=%s")
        values.append(attendance)
    if note:
        updates.append("note=%s")
        values.append(note)

    if updates:
        query = f"UPDATE student_tracking SET {', '.join(updates)} WHERE id=%s"
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
    cur.execute("DELETE FROM student_tracking WHERE id=%s", (att_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True


def filter_attendance(student_id=None, school_id=None, teacher_id=None, start_date=None, end_date=None):
    """
    دالة فلترة ذكية لجميع حالات البحث:
    - حسب الطالب، المدرسة، المدرس، فترة زمنية
    """
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT st.*, s.student_name, u.name AS teacher_name
        FROM student_tracking st
        LEFT JOIN students s ON st.student_id = s.id
        LEFT JOIN users u ON st.teacher_id = u.id
        WHERE 1=1
    """
    params = []

    if student_id:
        query += " AND st.student_id=%s"
        params.append(student_id)
    if school_id:
        query += " AND st.school_id=%s"
        params.append(school_id)
    if teacher_id:
        query += " AND st.teacher_id=%s"
        params.append(teacher_id)
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
