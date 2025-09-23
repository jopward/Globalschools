from db.db_setup import get_connection

# ============================
# CRUD وإدارة المدارس
# ============================

def create_school(school_name, admin_username=None, admin_password=None):
    """
    إضافة مدرسة جديدة
    school_name: اسم المدرسة
    admin_username: اسم مستخدم المدير (اختياري)
    admin_password: كلمة مرور المدير (اختياري)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO schools (school_name, admin_username, admin_password)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (school_name, admin_username, admin_password))
    school_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return school_id

def get_school_by_id(school_id):
    """
    استرجاع بيانات مدرسة حسب الـ ID
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools WHERE id = %s", (school_id,))
    school = cur.fetchone()
    cur.close()
    conn.close()
    return school

def get_all_schools():
    """
    استرجاع جميع المدارس
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools ORDER BY id")
    schools = cur.fetchall()
    cur.close()
    conn.close()
    return schools

def update_school(school_id, school_name=None, admin_username=None, admin_password=None):
    """
    تحديث بيانات المدرسة
    """
    conn = get_connection()
    cur = conn.cursor()
    updates = []
    values = []

    if school_name:
        updates.append("school_name=%s")
        values.append(school_name)
    if admin_username:
        updates.append("admin_username=%s")
        values.append(admin_username)
    if admin_password:
        updates.append("admin_password=%s")
        values.append(admin_password)

    if updates:
        query = f"UPDATE schools SET {', '.join(updates)} WHERE id=%s"
        values.append(school_id)
        cur.execute(query, tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    return True

def delete_school(school_id):
    """
    حذف مدرسة
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM schools WHERE id=%s", (school_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

# ============================
# دوال مساعدة للبحث والفلترة
# ============================

def search_schools_by_name(keyword):
    """
    البحث عن المدارس بواسطة اسم جزئي
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools WHERE school_name ILIKE %s", (f"%{keyword}%",))
    schools = cur.fetchall()
    cur.close()
    conn.close()
    return schools

def filter_schools_by_admin(admin_username):
    """
    استرجاع المدارس التي يملكها مدير محدد
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools WHERE admin_username=%s", (admin_username,))
    schools = cur.fetchall()
    cur.close()
    conn.close()
    return schools
