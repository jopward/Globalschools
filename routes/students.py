from flask import Blueprint, request, jsonify, session, redirect, url_for, flash, render_template
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
from models.classes import get_all_classes  # الصفوف + الشعب موجودة هنا
from functools import wraps

student_bp = Blueprint('student_bp', __name__)

# ============================
# ديكوريتور للتحقق من تسجيل الدخول والصلاحية
# ============================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get('user')
            if not user:
                flash("يجب تسجيل الدخول أولاً", "warning")
                return redirect(url_for('auth.login'))
            if role and user.get('role') != role:
                flash("لا تمتلك صلاحية الوصول لهذه الصفحة", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# إدارة الطلاب (CRUD كامل)
# ============================
@student_bp.route('/students/manage', methods=['GET', 'POST'])
@login_required(role='admin')
def manage_students():
    user = session.get('user')
    school_id = user.get('school_id')

    # --- إضافة طالب جديد ---
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        class_id = request.form.get('class_id')
        section_name = request.form.get('section_name')  # الشعب موجودة مع الصفوف

        if not all([student_name, class_id, section_name]):
            flash("جميع الحقول مطلوبة", "danger")
        else:
            student_id = create_student(student_name, school_id, class_id)
            flash(f"تم إضافة الطالب بنجاح (ID: {student_id})", "success")
        return redirect(url_for('student_bp.manage_students'))

    # --- جلب الطلاب والصفوف/الشعب ---
    students = filter_students_by_school(school_id)
    classes = get_all_classes(school_id)  # كل صف يحتوي على شعبه
    sections = []
    for cls in classes:
        for sec in cls.get('sections', []):
            sections.append({'class_id': cls['id'], 'name': sec})

    return render_template('students/manage.html', students=students, classes=classes, sections=sections)

# ============================
# تعديل طالب
# ============================
@student_bp.route('/students/<int:student_id>/edit', methods=['POST'])
@login_required(role='admin')
def edit_student_route(student_id):
    user = session.get('user')
    school_id = user.get('school_id')

    student = get_student_by_id(student_id)
    if not student or student['school_id'] != school_id:
        flash("الطالب غير موجود أو ليس من مدرستك", "danger")
        return redirect(url_for('student_bp.manage_students'))

    student_name = request.form.get('student_name')
    class_id = request.form.get('class_id')
    section_name = request.form.get('section_name')

    if not all([student_name, class_id, section_name]):
        flash("جميع الحقول مطلوبة", "danger")
    else:
        update_student(student_id, student_name=student_name, class_id=class_id)
        flash("تم تعديل بيانات الطالب بنجاح", "success")

    return redirect(url_for('student_bp.manage_students'))

# ============================
# حذف طالب
# ============================
@student_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_student_route(student_id):
    user = session.get('user')
    school_id = user.get('school_id')

    student = get_student_by_id(student_id)
    if not student or student['school_id'] != school_id:
        flash("الطالب غير موجود أو ليس من مدرستك", "danger")
    else:
        delete_student(student_id)
        flash("تم حذف الطالب بنجاح", "success")

    return redirect(url_for('student_bp.manage_students'))

# ============================
# البحث والفلترة
# ============================
@student_bp.route('/students/search', methods=['GET'])
@login_required()
def search_student():
    user = session.get('user')
    school_id = user.get('school_id')

    keyword = request.args.get('q')
    if not keyword:
        return jsonify({"error": "يرجى إدخال كلمة البحث"}), 400

    students = search_students_by_name(keyword)
    students = [s for s in students if s['school_id'] == school_id]

    return jsonify(students)

@student_bp.route('/students/filter/class', methods=['GET'])
@login_required()
def filter_student_class():
    user = session.get('user')
    school_id = user.get('school_id')

    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({"error": "يرجى إدخال معرف الصف"}), 400

    students = filter_students_by_class(class_id)
    students = [s for s in students if s['school_id'] == school_id]

    return jsonify(students)

@student_bp.route('/students/filter/school', methods=['GET'])
@login_required()
def filter_student_school():
    user = session.get('user')
    school_id = user.get('school_id')

    students = filter_students_by_school(school_id)
    return jsonify(students)
