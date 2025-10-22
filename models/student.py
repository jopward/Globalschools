from db.db_setup import get_connection

# ============================
# CRUD ودوال الطلاب
# ============================

def create_student(student_name, school_id, class_id):
    """إضافة طالب جديد (بدون عمود section)"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (student_name, school_id, class_id)
            VALUES (%s, %s, %s) RETURNING id
        """, (student_name, school_id, class_id))
        student_id = cur.fetchone()[0]  # ✅ إرجاع أول عنصر من النتيجة (ID)
        conn.commit()
        return student_id
    finally:
        cur.close()
        conn.close()


def get_student_by_id(student_id):
    """استرجاع طالب حسب المعرف ID"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def get_all_students():
    """استرجاع جميع الطلاب"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM students ORDER BY id DESC")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def update_student(student_id, student_name=None, school_id=None, class_id=None):
    """تحديث بيانات الطالب"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        updates = []
        values = []

        if student_name:
            updates.append("student_name = %s")
            values.append(student_name)
        if school_id:
            updates.append("school_id = %s")
            values.append(school_id)
        if class_id:
            updates.append("class_id = %s")
            values.append(class_id)

        if updates:
            query = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
            values.append(student_id)
            cur.execute(query, tuple(values))
            conn.commit()

        return True
    finally:
        cur.close()
        conn.close()


def delete_student(student_id):
    """حذف طالب"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()


# ============================
# البحث والفلترة
# ============================

def search_students_by_name(keyword):
    """البحث عن الطلاب بالاسم"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM students WHERE student_name ILIKE %s",
            (f"%{keyword}%",)
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def filter_students_by_class(class_id):
    """فلترة الطلاب حسب الصف"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM students WHERE class_id = %s", (class_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def filter_students_by_school(school_id):
    """فلترة الطلاب حسب المدرسة"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM students WHERE school_id = %s", (school_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
