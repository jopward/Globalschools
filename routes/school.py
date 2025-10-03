from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from models.school import (
    create_school,
    get_school_by_id,
    get_all_schools,
    update_school,
    delete_school,
    search_schools_by_name,
    filter_schools_by_admin
)
from functools import wraps

school_bp = Blueprint('school_bp', __name__)

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
# CRUD للمدارس
# ============================

@school_bp.route('/schools', methods=['POST'])
@login_required(role="admin")
def add_school():
    """إضافة مدرسة جديدة"""
    data = request.json
    school_name = data.get('school_name')
    admin_username = data.get('admin_username')
    admin_password = data.get('admin_password')

    if not school_name:
        return jsonify({"error": "اسم المدرسة مطلوب"}), 400

    school_id = create_school(school_name, admin_username, admin_password)
    return jsonify({"message": "تمت إضافة المدرسة", "school_id": school_id})

@school_bp.route('/schools', methods=['GET'])
@login_required()
def get_schools():
    """استرجاع جميع المدارس"""
    schools = get_all_schools()
    return jsonify(schools)

@school_bp.route('/schools/<int:school_id>', methods=['GET'])
@login_required()
def get_school(school_id):
    """استرجاع مدرسة حسب الـ ID"""
    school = get_school_by_id(school_id)
    if not school:
        return jsonify({"error": "المدرسة غير موجودة"}), 404
    return jsonify(school)

@school_bp.route('/schools/<int:school_id>', methods=['PUT'])
@login_required(role="admin")
def edit_school(school_id):
    """تحديث بيانات المدرسة"""
    data = request.json
    school_name = data.get('school_name')
    admin_username = data.get('admin_username')
    admin_password = data.get('admin_password')

    updated = update_school(school_id, school_name, admin_username, admin_password)
    if updated:
        return jsonify({"message": "تم تحديث المدرسة بنجاح"})
    return jsonify({"error": "فشل تحديث المدرسة"}), 400

@school_bp.route('/schools/<int:school_id>', methods=['DELETE'])
@login_required(role="admin")
def remove_school(school_id):
    """حذف مدرسة"""
    deleted = delete_school(school_id)
    if deleted:
        return jsonify({"message": "تم حذف المدرسة بنجاح"})
    return jsonify({"error": "فشل حذف المدرسة"}), 400

# ============================
# البحث والفلترة
# ============================

@school_bp.route('/schools/search', methods=['GET'])
@login_required()
def search_school():
    """البحث عن المدارس بواسطة الاسم"""
    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400
    schools = search_schools_by_name(keyword)
    return jsonify(schools)

@school_bp.route('/schools/filter', methods=['GET'])
@login_required()
def filter_school():
    """فلترة المدارس حسب اسم المدير"""
    admin_username = request.args.get('admin')
    if not admin_username:
        return jsonify({"error": "يرجى إدخال اسم المدير"}), 400
    schools = filter_schools_by_admin(admin_username)
    return jsonify(schools)
