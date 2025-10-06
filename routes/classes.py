from flask import Blueprint, request, jsonify, render_template, session
from db import db_connection  # ✅ التعديل هنا
from models.classes import (
    create_class,
    update_class,
    delete_class,
    filter_classes_by_school
)

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')

# ============================
# صفحة إدارة الصفوف
# ============================
@classes_bp.route('/classes_page')
def classes_page():
    # تمرير بيانات المستخدم لتحديد المدرسة
    user = session.get('user', {})
    return render_template('classes_page.html', user=user)

# ============================
# فلترة الصفوف حسب المدرسة
# ============================
@classes_bp.route('/filter/school')
def filter_by_school():
    school_id = request.args.get('school_id')
    if not school_id:
        return jsonify({"error": "لم يتم تحديد معرف المدرسة"}), 400

    try:
        classes = filter_classes_by_school(school_id)
        return jsonify(classes)
    except Exception as e:
        print("❌ خطأ أثناء جلب الصفوف:", e)
        return jsonify({"error": "حدث خطأ أثناء تحميل الصفوف"}), 500

# ============================
# إضافة صف جديد
# ============================
@classes_bp.route('/', methods=['POST'])
def add_class():
    data = request.get_json()
    if not data:
        return jsonify({"error": "بيانات غير صالحة"}), 400

    class_name = data.get('class_name')
    section = data.get('section')
    period = data.get('period', 'صباحي')
    school_id = data.get('school_id')

    if not all([class_name, section, school_id]):
        return jsonify({"error": "جميع الحقول مطلوبة"}), 400

    try:
        class_id = create_class(class_name, section, period, school_id)
        return jsonify({"message": "تمت إضافة الصف بنجاح", "id": class_id}), 201
    except Exception as e:
        print("❌ خطأ أثناء إضافة الصف:", e)
        return jsonify({"error": "حدث خطأ أثناء الإضافة"}), 500

# ============================
# تحديث صف
# ============================
@classes_bp.route('/<int:class_id>', methods=['PUT'])
def update_class_data(class_id):
    data = request.get_json()
    try:
        update_class(class_id, **data)
        return jsonify({"message": "تم تحديث الصف بنجاح"})
    except Exception as e:
        print("❌ خطأ أثناء التحديث:", e)
        return jsonify({"error": "حدث خطأ أثناء التحديث"}), 500

# ============================
# حذف صف
# ============================
@classes_bp.route('/<int:class_id>', methods=['DELETE'])
def delete_class_data(class_id):
    try:
        delete_class(class_id)
        return jsonify({"message": "تم حذف الصف بنجاح"})
    except Exception as e:
        print("❌ خطأ أثناء الحذف:", e)
        return jsonify({"error": "حدث خطأ أثناء الحذف"}), 500
