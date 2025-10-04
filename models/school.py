from db.db_setup import get_connection

# ============================
# CRUD وإدارة المدارس
# ============================

def create_school(school_name):
    """
    إضافة مدرسة جديدة
    school_name: اسم المدرسة
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO schools (school_name)
        VALUES (%s)
        RETURNING id
    """, (school_name,))
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

def update_school(school_id, school_name=None):
    """
    تحديث بيانات المدرسة
    """
    if not school_name:
        return False

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE schools SET school_name=%s WHERE id=%s", (school_name, school_id))
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

# حذف دالة الفلترة حسب admin_username لأنها لم تعد موجودة
