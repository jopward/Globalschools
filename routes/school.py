from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from db.db_setup import get_connection
from werkzeug.security import generate_password_hash
from functools import wraps

school_bp = Blueprint('school_bp', __name__)

# ============================
# ديكوريتور للتحقق من تسجيل الدخول والصلاحية
# ============================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash("يجب تسجيل الدخول أولاً")
                return redirect(url_for("auth_bp.login"))
            if role:
                user_role = session.get("user_role")
                if isinstance(role, list):
                    if user_role not in role:
                        flash("لا تمتلك صلاحية الوصول لهذه الصفحة")
                        return redirect(url_for("auth_bp.login"))
                elif user_role != role:
                    flash("لا تمتلك صلاحية الوصول لهذه الصفحة")
                    return redirect(url_for("auth_bp.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# CRUD للمدارس
# ============================

@school_bp.route('/schools', methods=['POST'])
@login_required(role=["superadmin"])
def add_school():
    """إضافة مدرسة جديدة وحساب المدير تلقائيًا"""
    data = request.json
    school_name = data.get('school_name')
    admin_username = data.get('admin_username')
    admin_password = data.get('admin_password')

    if not school_name or not admin_username or not admin_password:
        return jsonify({"error": "اسم المدرسة واسم المدير وكلمة المرور مطلوبة"}), 400

    # إضافة المدرسة
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO schools (school_name) VALUES (%s) RETURNING id",
        (school_name,)
    )
    school_id = cur.fetchone()['id']

    # تشفير كلمة المرور
    hashed_password = generate_password_hash(admin_password)

    # إضافة المدير في جدول users
    cur.execute(
        """
        INSERT INTO users (name, username, password, role, school_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (admin_username, admin_username, hashed_password, 'admin', school_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "تمت إضافة المدرسة والمدير بنجاح",
        "school_id": school_id,
        "admin_username": admin_username
    })

@school_bp.route('/schools', methods=['GET'])
@login_required()
def get_schools():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools ORDER BY id")
    schools = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(schools)

@school_bp.route('/schools/<int:school_id>', methods=['GET'])
@login_required()
def get_school(school_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools WHERE id=%s", (school_id,))
    school = cur.fetchone()
    cur.close()
    conn.close()
    if not school:
        return jsonify({"error": "المدرسة غير موجودة"}), 404
    return jsonify(school)

@school_bp.route('/schools/<int:school_id>', methods=['PUT'])
@login_required(role=["superadmin"])
def edit_school(school_id):
    data = request.json
    school_name = data.get('school_name')

    if not school_name:
        return jsonify({"error": "اسم المدرسة مطلوب"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE schools SET school_name=%s WHERE id=%s", (school_name, school_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "تم تحديث المدرسة بنجاح"})

@school_bp.route('/schools/<int:school_id>', methods=['DELETE'])
@login_required(role=["superadmin"])
def remove_school(school_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM schools WHERE id=%s", (school_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "تم حذف المدرسة بنجاح"})

# ============================
# البحث والفلترة
# ============================

@school_bp.route('/schools/search', methods=['GET'])
@login_required()
def search_school():
    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools WHERE school_name ILIKE %s", (f"%{keyword}%",))
    schools = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(schools)

@school_bp.route('/schools/filter', methods=['GET'])
@login_required()
def filter_school():
    admin_username = request.args.get('admin')
    if not admin_username:
        return jsonify({"error": "يرجى إدخال اسم المدير"}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools WHERE admin_username=%s", (admin_username,))
    schools = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(schools)
