from flask import Blueprint, request, jsonify
from models.classes import (
    create_class,
    get_class_by_id,
    get_all_classes,
    update_class,
    delete_class,
    search_classes,
    filter_classes_by_school,
    get_class_teachers,
    get_class_subjects
)

classes_bp = Blueprint('classes_bp', __name__)

# ============================
# CRUD للصفوف
# ============================

@classes_bp.route('/classes', methods=['POST'])
def add_class():
    """إضافة صف جديد"""
    data = request.json
    class_name = data.get('class_name')
    section = data.get('section')
    period = data.get('period', 'صباحي')
    school_id = data.get('school_id')

    if not all([class_name, school_id]):
        return jsonify({"error": "اسم الصف ومعرف المدرسة مطلوب"}), 400

    class_id = create_class(class_name, section, period, school_id)
    return jsonify({"message": "تم إضافة الصف", "class_id": class_id})

@classes_bp.route('/classes', methods=['GET'])
def list_classes():
    """استرجاع جميع الصفوف"""
    classes = get_all_classes()
    return jsonify(classes)

@classes_bp.route('/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    """استرجاع الصف حسب ID"""
    class_ = get_class_by_id(class_id)
    if not class_:
        return jsonify({"error": "الصف غير موجود"}), 404
    return jsonify(class_)

@classes_bp.route('/classes/<int:class_id>', methods=['PUT'])
def edit_class(class_id):
    """تحديث بيانات الصف"""
    data = request.json
    updated = update_class(
        class_id,
        class_name=data.get('class_name'),
        section=data.get('section'),
        period=data.get('period'),
        school_id=data.get('school_id')
    )
    if updated:
        return jsonify({"message": "تم تحديث الصف"})
    return jsonify({"error": "فشل التحديث"}), 400

@classes_bp.route('/classes/<int:class_id>', methods=['DELETE'])
def remove_class(class_id):
    """حذف الصف"""
    deleted = delete_class(class_id)
    if deleted:
        return jsonify({"message": "تم حذف الصف"})
    return jsonify({"error": "فشل الحذف"}), 400

# ============================
# البحث والفلترة
# ============================

@classes_bp.route('/classes/search', methods=['GET'])
def search_class():
    """البحث عن الصفوف بالاسم"""
    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400
    classes = search_classes(keyword)
    return jsonify(classes)

@classes_bp.route('/classes/filter/school', methods=['GET'])
def filter_class_school():
    """فلترة الصفوف حسب المدرسة"""
    school_id = request.args.get('school_id')
    if not school_id:
        return jsonify({"error": "يرجى إدخال معرف المدرسة"}), 400
    classes = filter_classes_by_school(school_id)
    return jsonify(classes)

# ============================
# روابط الصفوف بالمعلمين والمواد
# ============================

@classes_bp.route('/classes/<int:class_id>/teachers', methods=['GET'])
def class_teachers(class_id):
    """استرجاع المعلمين المرتبطين بالصف"""
    teachers = get_class_teachers(class_id)
    return jsonify(teachers)

@classes_bp.route('/classes/<int:class_id>/subjects', methods=['GET'])
def class_subjects(class_id):
    """استرجاع المواد المرتبطة بالصف"""
    subjects = get_class_subjects(class_id)
    return jsonify(subjects)
