from db.db_setup import get_connection
import psycopg2.extras

# ============================
# CRUD ودوال الطلاب مع الصف والشعبة
# ============================

def create_student(student_name, school_id, class_id):
    """إضافة طالب جديد"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            INSERT INTO students (student_name, school_id, class_id)
            VALUES (%s, %s, %s) RETURNING id
        """, (student_name, school_id, class_id))
        student_id = cur.fetchone()['id']
        conn.commit()
        return student_id
    finally:
        cur.close()
        conn.close()


def get_student_by_id(student_id):
    """استرجاع طالب حسب المعرف ID مع اسم الصف والشعبة"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT s.*, tc.class_name, tc.section
            FROM students s
            LEFT JOIN teacher_classes tc ON s.class_id = tc.id
            WHERE s.id = %s
        """, (student_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def get_all_students(school_id):
    """استرجاع جميع الطلاب مع اسم الصف والشعبة حسب المدرسة"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT s.*, tc.class_name, tc.section
            FROM students s
            LEFT JOIN teacher_classes tc ON s.class_id = tc.id
            WHERE s.school_id = %s
            ORDER BY s.id DESC
        """, (school_id,))
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
# البحث والفلترة مع الصف والشعبة
# ============================

def search_students_by_name(keyword, school_id=None):
    """البحث عن الطلاب بالاسم"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if school_id:
            cur.execute("""
                SELECT s.*, tc.class_name, tc.section
                FROM students s
                LEFT JOIN teacher_classes tc ON s.class_id = tc.id
                WHERE s.student_name ILIKE %s AND s.school_id = %s
            """, (f"%{keyword}%", school_id))
        else:
            cur.execute("""
                SELECT s.*, tc.class_name, tc.section
                FROM students s
                LEFT JOIN teacher_classes tc ON s.class_id = tc.id
                WHERE s.student_name ILIKE %s
            """, (f"%{keyword}%",))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def filter_students_by_class(class_id):
    """فلترة الطلاب حسب الصف"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT s.*, tc.class_name, tc.section
            FROM students s
            LEFT JOIN teacher_classes tc ON s.class_id = tc.id
            WHERE s.class_id = %s
        """, (class_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def filter_students_by_school(school_id):
    """فلترة الطلاب حسب المدرسة"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT s.*, tc.class_name, tc.section
            FROM students s
            LEFT JOIN teacher_classes tc ON s.class_id = tc.id
            WHERE s.school_id = %s
        """, (school_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


# ============================
# دوال الصفوف والشعب
# ============================

def get_all_classes(school_id=None):
    """استرجاع جميع الصفوف والشعب، مع فلترة حسب المدرسة إذا أعطيت school_id"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if school_id:
            cur.execute("""
                SELECT * FROM teacher_classes
                WHERE school_id = %s
                ORDER BY class_name, section
            """, (school_id,))
        else:
            cur.execute("""
                SELECT * FROM teacher_classes
                ORDER BY class_name, section
            """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
