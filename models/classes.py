from db.db_setup import get_connection

# ============================
# CRUD ودوال الصفوف
# ============================

def create_class(class_name, section=None, period='صباحي', school_id=None):
    """
    إضافة صف جديد
    section: الشعبة أو القسم
    period: الفترة (صباحية أو مسائية)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO teacher_classes (class_name, section, period, school_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (class_name, section, period, school_id))
    class_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return class_id

def get_class_by_id(class_id):
    """استرجاع الصف حسب ID"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teacher_classes WHERE id=%s", (class_id,))
    class_ = cur.fetchone()
    cur.close()
    conn.close()
    return class_

def get_all_classes():
    """استرجاع جميع الصفوف"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teacher_classes")
    classes = cur.fetchall()
    cur.close()
    conn.close()
    return classes

def update_class(class_id, class_name=None, section=None, period=None, school_id=None):
    """تحديث بيانات الصف"""
    conn = get_connection()
    cur = conn.cursor()
    updates = []
    values = []

    if class_name:
        updates.append("class_name=%s")
        values.append(class_name)
    if section:
        updates.append("section=%s")
        values.append(section)
    if period:
        updates.append("period=%s")
        values.append(period)
    if school_id:
        updates.append("school_id=%s")
        values.append(school_id)

    if updates:
        query = f"UPDATE teacher_classes SET {', '.join(updates)} WHERE id=%s"
        values.append(class_id)
        cur.execute(query, tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    return True

def delete_class(class_id):
    """حذف الصف"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM teacher_classes WHERE id=%s", (class_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

# ============================
# البحث والفلترة
# ============================

def search_classes(keyword):
    """البحث عن الصفوف حسب الاسم"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teacher_classes WHERE class_name ILIKE %s", (f"%{keyword}%",))
    classes = cur.fetchall()
    cur.close()
    conn.close()
    return classes

def filter_classes_by_school(school_id):
    """فلترة الصفوف حسب المدرسة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teacher_classes WHERE school_id=%s", (school_id,))
    classes = cur.fetchall()
    cur.close()
    conn.close()
    return classes

# ============================
# ربط الصف بالمعلمين والمواد
# ============================

def get_class_teachers(class_id):
    """استرجاع المعلمين المرتبطين بالصف"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.name
        FROM class_teachers ct
        JOIN users u ON ct.teacher_id = u.id
        WHERE ct.class_id=%s
    """, (class_id,))
    teachers = cur.fetchall()
    cur.close()
    conn.close()
    return teachers

def get_class_subjects(class_id):
    """استرجاع المواد المرتبطة بالصف"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.subject_name, u.id AS teacher_id, u.name AS teacher_name
        FROM class_subjects cs
        JOIN subjects s ON cs.subject_id = s.id
        JOIN users u ON cs.teacher_id = u.id
        WHERE cs.class_id=%s
    """, (class_id,))
    subjects = cur.fetchall()
    cur.close()
    conn.close()
    return subjects
