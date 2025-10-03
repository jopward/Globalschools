from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from models.user import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    update_user,
    delete_user,
    verify_user
)
from functools import wraps

user_bp = Blueprint('user_bp', __name__)

# ============================
# ديكوريتور للتحقق من تسجيل الدخول والصلاحية
# ============================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("يجب تسجيل الدخول أولاً")
                return redirect(url_for("auth.login"))
            if role and user.get("role") != role:
                flash("لا تمتلك صلاحية الوصول لهذه الصفحة")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# إنشاء مستخدم جديد
# ============================
@user_bp.route('/create', methods=['POST'])
@login_required(role="admin")  # فقط admin يقدر يضيف مستخدم
def add_user():
    data = request.json
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    school_id = data.get('school_id')

    if get_user_by_username(username):
        return jsonify({"error": "Username already exists"}), 400

    user_id = create_user(name, username, password, role, school_id)
    return jsonify({"message": "User created", "user_id": user_id}), 201

# ============================
# استرجاع مستخدم حسب ID
# ============================
@user_bp.route('/<int:user_id>', methods=['GET'])
@login_required()
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

# ============================
# تحديث بيانات مستخدم
# ============================
@user_bp.route('/update/<int:user_id>', methods=['PUT'])
@login_required(role="admin")  # فقط admin يقدر يحدث بيانات مستخدم
def edit_user(user_id):
    data = request.json
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    updated = update_user(
        user_id,
        name=data.get('name'),
        username=data.get('username'),
        password=data.get('password'),
        role=data.get('role'),
        school_id=data.get('school_id')
    )
    return jsonify({"message": "User updated"}), 200

# ============================
# حذف مستخدم
# ============================
@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
@login_required(role="admin")  # فقط admin يقدر يحذف مستخدم
def remove_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    delete_user(user_id)
    return jsonify({"message": "User deleted"}), 200

# ============================
# التحقق من تسجيل الدخول
# ============================
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = verify_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    # حفظ بيانات المستخدم في الجلسة
    session['user'] = user
    return jsonify({"message": "Login successful", "user": user}), 200

# ============================
# البحث عن مستخدم حسب اسم المستخدم
# ============================
@user_bp.route('/search', methods=['GET'])
@login_required()
def search_user():
    username = request.args.get('username')
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200
