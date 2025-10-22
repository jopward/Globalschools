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
from models.classes import get_all_classes
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
                return redirect(url_for('auth_bp.login'))
            if role and user.get('role') != role:
                flash("لا تمتلك صلاحية الوصول لهذه الصفحة", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# إدارة الطلاب (إضافة/عرض/تعديل/حذف)
# ============================
@student_bp.route('/students/manage', methods=['GET', 'POST'])
@login_required(role='admin')
def manage_students():
    user = session.get('user')
    school_id = user.get('school_id')

    # --- إضافة طالب أو مجموعة طلاب ---
    if request.method == 'POST':
        # استقبال بيانات الطلاب على شكل قائمة من الأسماء (من form متعدد)
        student_names = request.form.getlist('student_name[]')
        class_id = request.form.get('class_id')

        if not student_names or not class_id:
            flash("يرجى تعبئة جميع الحقول المطلوبة", "danger")
        else:
            added_count = 0
            for name in student_names:
                name = name.strip()
                if name:  # فقط الأسماء غير الفارغة
                    create_student(name, school_id, class_id)
                    added_count += 1
            flash(f"تم إضافة {added_count} طالب{'اً' if added_count == 1 else 'اً'} بنجاح", "success")

        # العودة لنفس الصفحة بدون خروج أو خطأ
        return redirect(url_for('student_bp.manage_students'))

    # --- عرض الطلاب ---
    students = filter_students_by_school(school_id)
    classes = get_all_classes(school_id)

    return render_template('add_student.html', students=students, classes=classes)

# ============================
# تعديل طالب
# ============================
@student_bp.route('/students/<int:student_id>/edit', methods=['POST'])
@login_required(role='admin')
def edit_student_route(student_id):
    user = session.get('user')
    school_id = user.get('school_id')

    student = get_student_by_id(student_id)
    if not student or student[2] != school_id:  # student[2] = school_id من الجدول
        flash("الطالب غير موجود أو ليس من مدرستك", "danger")
        return redirect(url_for('student_bp.manage_students'))

    student_name = request.form.get('student_name')
    class_id = request.form.get('class_id')

    if not all([student_name, class_id]):
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
    if not student or student[2] != school_id:
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
    students = [s for s in students if s[2] == school_id]  # التحقق من مدرسة المستخدم

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
    students = [s for s in students if s[2] == school_id]

    return jsonify(students)

@student_bp.route('/students/filter/school', methods=['GET'])
@login_required()
def filter_student_school():
    user = session.get('user')
    school_id = user.get('school_id')

    students = filter_students_by_school(school_id)
    return jsonify(students)
