# routes/user.py
from flask import Blueprint, request, jsonify
from models.user import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    update_user,
    delete_user,
    verify_user
)

# تعريف Blueprint خاص باليوزر
user_bp = Blueprint('user_bp', __name__)

# ============================
# إنشاء مستخدم جديد
# ============================
@user_bp.route('/create', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    school_id = data.get('school_id')

    # التحقق من وجود اسم مستخدم مسبقاً
    if get_user_by_username(username):
        return jsonify({"error": "Username already exists"}), 400

    user_id = create_user(name, username, password, role, school_id)
    return jsonify({"message": "User created", "user_id": user_id}), 201

# ============================
# استرجاع مستخدم حسب ID
# ============================
@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

# ============================
# تحديث بيانات مستخدم
# ============================
@user_bp.route('/update/<int:user_id>', methods=['PUT'])
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

    return jsonify({"message": "Login successful", "user": user}), 200

# ============================
# البحث عن مستخدم حسب اسم المستخدم
# ============================
@user_bp.route('/search', methods=['GET'])
def search_user():
    username = request.args.get('username')
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200
