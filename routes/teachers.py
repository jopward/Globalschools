from flask import Blueprint, request, jsonify
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

teacher_bp = Blueprint('teacher_bp', __name__)

# ============================
# CRUD للمعلمين
# ============================

@teacher_bp.route('/teachers', methods=['POST'])
def add_teacher():
    """إضافة معلم جديد"""
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
def list_teachers():
    """استرجاع جميع المعلمين"""
    teachers = get_all_teachers()
    return jsonify(teachers)

@teacher_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    """استرجاع المعلم حسب ID"""
    teacher = get_teacher_by_id(teacher_id)
    if not teacher:
        return jsonify({"error": "المعلم غير موجود"}), 404
    return jsonify(teacher)

@teacher_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def edit_teacher(teacher_id):
    """تحديث بيانات المعلم"""
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
def remove_teacher(teacher_id):
    """حذف المعلم"""
    deleted = delete_teacher(teacher_id)
    if deleted:
        return jsonify({"message": "تم حذف المعلم"})
    return jsonify({"error": "فشل الحذف"}), 400

# ============================
# البحث والفلترة
# ============================

@teacher_bp.route('/teachers/search', methods=['GET'])
def search_teacher():
    """البحث عن المعلمين بالاسم"""
    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400
    teachers = search_teachers_by_name(keyword)
    return jsonify(teachers)

@teacher_bp.route('/teachers/filter/school', methods=['GET'])
def filter_teacher_school():
    """فلترة المعلمين حسب المدرسة"""
    school_id = request.args.get('school_id')
    if not school_id:
        return jsonify({"error": "يرجى إدخال معرف المدرسة"}), 400
    teachers = filter_teachers_by_school(school_id)
    return jsonify(teachers)

@teacher_bp.route('/teachers/<int:teacher_id>/subjects', methods=['GET'])
def teacher_subjects(teacher_id):
    """استرجاع المواد التي يدرسها المعلم"""
    subjects = get_teacher_subjects(teacher_id)
    return jsonify(subjects)
