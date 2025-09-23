from db.db_setup import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ============================
# دوال CRUD للمستخدمين
# ============================

# ----------------------------
# إضافة مستخدم جديد
# ----------------------------
def create_user(name, username, password, role, school_id=None):
    """
    إضافة مستخدم جديد إلى قاعدة البيانات.
    
    المعاملات:
    - name: اسم المستخدم
    - username: اسم المستخدم الفريد
    - password: كلمة المرور (ستتحول إلى هاش)
    - role: نوع المستخدم (superadmin / admin / teacher)
    - school_id: معرف المدرسة (اختياري)
    
    الإرجاع:
    - id المستخدم الذي تم إضافته
    """
    conn = get_connection()
    cur = conn.cursor()
    hashed_pw = generate_password_hash(password)
    cur.execute("""
        INSERT INTO users (name, username, password, role, school_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (name, username, hashed_pw, role, school_id))
    user_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return user_id

# ----------------------------
# استرجاع المستخدم حسب الـ ID
# ----------------------------
def get_user_by_id(user_id):
    """
    استرجاع بيانات المستخدم باستخدام معرفه (ID).
    
    الإرجاع:
    - قاموس يحتوي على بيانات المستخدم أو None إذا لم يوجد
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

# ----------------------------
# استرجاع المستخدم حسب اسم المستخدم
# ----------------------------
def get_user_by_username(username):
    """
    استرجاع بيانات المستخدم باستخدام اسم المستخدم.
    
    الإرجاع:
    - قاموس يحتوي على بيانات المستخدم أو None إذا لم يوجد
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

# ----------------------------
# تحديث بيانات المستخدم
# ----------------------------
def update_user(user_id, name=None, username=None, password=None, role=None, school_id=None):
    """
    تحديث بيانات المستخدم.
    يمكن تحديث أي من الحقول (name, username, password, role, school_id) بشكل اختياري.
    
    الإرجاع:
    - True بعد نجاح التحديث
    """
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
    if role:
        updates.append("role=%s")
        values.append(role)
    if school_id:
        updates.append("school_id=%s")
        values.append(school_id)
    
    if updates:
        query = f"UPDATE users SET {', '.join(updates)} WHERE id=%s"
        values.append(user_id)
        cur.execute(query, tuple(values))
        conn.commit()
    
    cur.close()
    conn.close()
    return True

# ----------------------------
# حذف مستخدم
# ----------------------------
def delete_user(user_id):
    """
    حذف المستخدم من قاعدة البيانات حسب معرفه.
    
    الإرجاع:
    - True بعد نجاح الحذف
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

# ============================
# دوال مساعدة للتحقق من تسجيل الدخول
# ============================

# ----------------------------
# التحقق من اسم المستخدم وكلمة المرور
# ----------------------------
def verify_user(username, password):
    """
    التحقق من صحة اسم المستخدم وكلمة المرور.
    
    الإرجاع:
    - قاموس بيانات المستخدم إذا كان التحقق صحيح
    - None إذا فشل التحقق
    """
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None
