from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from models.teacher import (
    create_teacher,
    get_teacher_by_id,
    get_all_teachers,
    update_teacher,
    delete_teacher,
    search_teachers_by_name,
    filter_teachers_by_school,
    get_teacher_subjects
)
from functools import wraps

teacher_bp = Blueprint('teacher_bp', __name__)

# ============================
# ديكوريتور للتحقق من تسجيل الدخول والصلاحية
# ============================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get('user')
            if not user:
                flash("يجب تسجيل الدخول أولاً")
                return redirect(url_for('auth.login'))
            if role and user.get('role') != role:
                flash("لا تمتلك صلاحية الوصول لهذه الصفحة")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# CRUD للمعلمين
# ============================

@teacher_bp.route('/teachers', methods=['POST'])
@login_required(role='admin')  # فقط admin يقدر يضيف معلم
def add_teacher():
    data = request.json
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    school_id = data.get('school_id')
    subjects = data.get('subjects', [])

    if not all([name, username, password, school_id]):
        return jsonify({"error": "جميع الحقول مطلوبة"}), 400

    teacher_id = create_teacher(name, username, password, school_id, subjects)
    return jsonify({"message": "تم إضافة المعلم", "teacher_id": teacher_id})

@teacher_bp.route('/teachers', methods=['GET'])
@login_required()  # أي مستخدم مسجل دخول يمكنه الوصول
def list_teachers():
    teachers = get_all_teachers()
    return jsonify(teachers)

@teacher_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
@login_required()
def get_teacher(teacher_id):
    teacher = get_teacher_by_id(teacher_id)
    if not teacher:
        return jsonify({"error": "المعلم غير موجود"}), 404
    return jsonify(teacher)

@teacher_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
@login_required(role='admin')
def edit_teacher(teacher_id):
    data = request.json
    updated = update_teacher(
        teacher_id,
        name=data.get('name'),
        username=data.get('username'),
        password=data.get('password'),
        school_id=data.get('school_id')
    )
    if updated:
        return jsonify({"message": "تم تحديث المعلم"})
    return jsonify({"error": "فشل التحديث"}), 400

@teacher_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
@login_required(role='admin')
def remove_teacher(teacher_id):
    deleted = delete_teacher(teacher_id)
    if deleted:
        return jsonify({"message": "تم حذف المعلم"})
    return jsonify({"error": "فشل الحذف"}), 400

# ============================
# البحث والفلترة
# ============================

@teacher_bp.route('/teachers/search', methods=['GET'])
@login_required()
def search_teacher():
    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400
    teachers = search_teachers_by_name(keyword)
    return jsonify(teachers)

@teacher_bp.route('/teachers/filter/school', methods=['GET'])
@login_required()
def filter_teacher_school():
    school_id = request.args.get('school_id')
    if not school_id:
        return jsonify({"error": "يرجى إدخال معرف المدرسة"}), 400
    teachers = filter_teachers_by_school(school_id)
    return jsonify(teachers)

@teacher_bp.route('/teachers/<int:teacher_id>/subjects', methods=['GET'])
@login_required()
def teacher_subjects(teacher_id):
    subjects = get_teacher_subjects(teacher_id)
    return jsonify(subjects)
