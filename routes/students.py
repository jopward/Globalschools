from flask import Blueprint, request, jsonify
from models.student import (
    create_student,
    get_student_by_id,
    get_all_students,
    update_student,
    delete_student,
    search_students_by_name,
    filter_students_by_class,
    filter_students_by_school
)

student_bp = Blueprint('student_bp', __name__)

# ============================
# CRUD للطلاب
# ============================

@student_bp.route('/students', methods=['POST'])
def add_student():
    """إضافة طالب جديد"""
    data = request.json
    student_name = data.get('student_name')
    school_id = data.get('school_id')
    class_id = data.get('class_id')

    if not all([student_name, school_id, class_id]):
        return jsonify({"error": "جميع الحقول مطلوبة"}), 400

    student_id = create_student(student_name, school_id, class_id)
    return jsonify({"message": "تم إضافة الطالب", "student_id": student_id})

@student_bp.route('/students', methods=['GET'])
def get_students():
    """استرجاع جميع الطلاب"""
    students = get_all_students()
    return jsonify(students)

@student_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """استرجاع طالب حسب ID"""
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"error": "الطالب غير موجود"}), 404
    return jsonify(student)

@student_bp.route('/students/<int:student_id>', methods=['PUT'])
def edit_student(student_id):
    """تحديث بيانات الطالب"""
    data = request.json
    updated = update_student(
        student_id,
        student_name=data.get('student_name'),
        school_id=data.get('school_id'),
        class_id=data.get('class_id')
    )
    if updated:
        return jsonify({"message": "تم تحديث الطالب"})
    return jsonify({"error": "فشل التحديث"}), 400

@student_bp.route('/students/<int:student_id>', methods=['DELETE'])
def remove_student(student_id):
    """حذف طالب"""
    deleted = delete_student(student_id)
    if deleted:
        return jsonify({"message": "تم حذف الطالب"})
    return jsonify({"error": "فشل الحذف"}), 400

# ============================
# البحث والفلترة
# ============================

@student_bp.route('/students/search', methods=['GET'])
def search_student():
    """البحث عن الطلاب بالاسم"""
    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400
    students = search_students_by_name(keyword)
    return jsonify(students)

@student_bp.route('/students/filter/class', methods=['GET'])
def filter_student_class():
    """فلترة الطلاب حسب الصف"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({"error": "يرجى إدخال معرف الصف"}), 400
    students = filter_students_by_class(class_id)
    return jsonify(students)

@student_bp.route('/students/filter/school', methods=['GET'])
def filter_student_school():
    """فلترة الطلاب حسب المدرسة"""
    school_id = request.args.get('school_id')
    if not school_id:
        return jsonify({"error": "يرجى إدخال معرف المدرسة"}), 400
    students = filter_students_by_school(school_id)
    return jsonify(students)
