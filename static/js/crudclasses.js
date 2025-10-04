from flask import Blueprint, request, jsonify, session, redirect, url_for, flash, render_template
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
from functools import wraps

classes_bp = Blueprint('classes_bp', __name__)  # بدون url_prefix هنا

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
            user_role = session.get("user_role")
            if role and user_role != role:
                flash("لا تمتلك صلاحية الوصول لهذه الصفحة")
                return redirect(url_for("auth_bp.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# CRUD للصفوف
# ============================
@classes_bp.route('/', methods=['POST'])
@login_required(role='admin')
def add_class():
    data = request.json
    class_name = data.get('class_name')
    section = data.get('section')
    period = data.get('period', 'صباحي')
    school_id = data.get('school_id')

    if not all([class_name, school_id]):
        return jsonify({"error": "اسم الصف ومعرف المدرسة مطلوب"}), 400

    class_id = create_class(class_name, section, period, school_id)
    return jsonify({"message": "تم إضافة الصف", "class_id": class_id})


@classes_bp.route('/', methods=['GET'])
@login_required()
def list_classes():
    classes = get_all_classes()
    return jsonify(classes)


@classes_bp.route('/<int:class_id>', methods=['GET'])
@login_required()
def get_class(class_id):
    class_ = get_class_by_id(class_id)
    if not class_:
        return jsonify({"error": "الصف غير موجود"}), 404
    return jsonify(class_)


@classes_bp.route('/<int:class_id>', methods=['PUT'])
@login_required(role='admin')
def edit_class(class_id):
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


@classes_bp.route('/<int:class_id>', methods=['DELETE'])
@login_required(role='admin')
def remove_class(class_id):
    deleted = delete_class(class_id)
    if deleted:
        return jsonify({"message": "تم حذف الصف"})
    return jsonify({"error": "فشل الحذف"}), 400


# ============================
# البحث والفلترة
# ============================
@classes_bp.route('/search', methods=['GET'])
@login_required()
def search_class():
    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400
    classes = search_classes(keyword)
    return jsonify(classes)


@classes_bp.route('/filter/school', methods=['GET'])
@login_required()
def filter_class_school():
    school_id = request.args.get('school_id')
    if not school_id:
        return jsonify({"error": "يرجى إدخال معرف المدرسة"}), 400
    classes = filter_classes_by_school(school_id)
    return jsonify(classes)


# ============================
# روابط الصفوف بالمعلمين والمواد
# ============================
@classes_bp.route('/<int:class_id>/teachers', methods=['GET'])
@login_required()
def class_teachers(class_id):
    teachers = get_class_teachers(class_id)
    return jsonify(teachers)


@classes_bp.route('/<int:class_id>/subjects', methods=['GET'])
@login_required()
def class_subjects(class_id):
    subjects = get_class_subjects(class_id)
    return jsonify(subjects)


# ============================
# صفحة HTML للعرض (مدير)
# ============================
@classes_bp.route('/page')
@login_required(role='admin')
def classes_page():
    user = {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'name': session.get('user_name'),
        'school_id': session.get('user_school_id', 1)
    }
    return render_template("classes.html", user=user)
