from db.db_setup import get_connection

# ============================
# CRUD ودوال المعلمين
# ============================

def create_teacher(name, username, password, school_id, subjects=[]):
    """
    إضافة معلم جديد.
    subjects: قائمة معرفات المواد التي يدرسها.
    """
    from werkzeug.security import generate_password_hash
    conn = get_connection()
    cur = conn.cursor()
    hashed_pw = generate_password_hash(password)
    # إضافة المعلم
    cur.execute("""
        INSERT INTO users (name, username, password, role, school_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """, (name, username, hashed_pw, 'teacher', school_id))
    teacher_id = cur.fetchone()['id']

    # ربط المعلم بالمواد
    for subject_id in subjects:
        cur.execute("""
            INSERT INTO teacher_subjects (teacher_id, subject_id)
            VALUES (%s, %s)
        """, (teacher_id, subject_id))

    conn.commit()
    cur.close()
    conn.close()
    return teacher_id

def get_teacher_by_id(teacher_id):
    """استرجاع المعلم حسب ID"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s AND role='teacher'", (teacher_id,))
    teacher = cur.fetchone()
    cur.close()
    conn.close()
    return teacher

def get_all_teachers():
    """استرجاع جميع المعلمين"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE role='teacher'")
    teachers = cur.fetchall()
    cur.close()
    conn.close()
    return teachers

def update_teacher(teacher_id, name=None, username=None, password=None, school_id=None):
    """تحديث بيانات المعلم"""
    from werkzeug.security import generate_password_hash
    conn = get_connection()
    cur = conn.cursor()
    updates = []
    values = []

    if name:
        updates.append("name=%s")
        values.append(name)
    if username:
        updates.append("username=%s")
        values.append(username)
    if password:
        updates.append("password=%s")
        values.append(generate_password_hash(password))
    if school_id:
        updates.append("school_id=%s")
        values.append(school_id)

    if updates:
        query = f"UPDATE users SET {', '.join(updates)} WHERE id=%s AND role='teacher'"
        values.append(teacher_id)
        cur.execute(query, tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    return True

def delete_teacher(teacher_id):
    """حذف المعلم"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s AND role='teacher'", (teacher_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

# ============================
# البحث والفلترة
# ============================

def search_teachers_by_name(keyword):
    """البحث عن المعلمين بالاسم"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE role='teacher' AND name ILIKE %s", (f"%{keyword}%",))
    teachers = cur.fetchall()
    cur.close()
    conn.close()
    return teachers

def filter_teachers_by_school(school_id):
    """فلترة المعلمين حسب المدرسة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE role='teacher' AND school_id=%s", (school_id,))
    teachers = cur.fetchall()
    cur.close()
    conn.close()
    return teachers

def get_teacher_subjects(teacher_id):
    """استرجاع المواد التي يدرسها المعلم"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.subject_name
        FROM teacher_subjects ts
        JOIN subjects s ON ts.subject_id = s.id
        WHERE ts.teacher_id=%s
    """, (teacher_id,))
    subjects = cur.fetchall()
    cur.close()
    conn.close()
    return subjects
