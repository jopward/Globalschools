from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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
from models.subjects import get_all_subjects
from werkzeug.security import check_password_hash


#bcrypt = Bcrypt()
teacher_bp = Blueprint('teacher_bp', __name__)

# ============================
# عرض قائمة المعلمين
# ============================
@teacher_bp.route('/teachers')
def teachers_list():
    if 'user_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "warning")
        return redirect(url_for("auth_bp.login"))

    school_id = session.get("school_id")
    teachers = filter_teachers_by_school(school_id)
    return render_template("teachers/list.html", teachers=teachers)

# ============================
# صفحة إضافة معلم جديد
# ============================
@teacher_bp.route('/teachers/add', methods=['GET', 'POST'])
def add_teacher():
    if 'user_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "warning")
        return redirect(url_for("auth_bp.login"))

    school_id = session.get("school_id")
    subjects = get_all_subjects()

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        teacher_code = request.form.get('teacher_code')
        selected_subjects = request.form.getlist('subjects')

        if not all([name, username, password]):
            flash("يرجى تعبئة جميع الحقول المطلوبة", "danger")
            return redirect(url_for('teacher_bp.add_teacher'))

        teacher_id = create_teacher(
            name=name,
            username=username,
            password=password,
            school_id=school_id,
            teacher_code=teacher_code,
            subjects=selected_subjects
        )

        flash("تمت إضافة المعلم بنجاح", "success")
        return redirect(url_for('teacher_bp.teachers_list'))

    return render_template("teachers/add.html", subjects=subjects)

# ============================
# تعديل بيانات المعلم
# ============================
@teacher_bp.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    if 'user_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "warning")
        return redirect(url_for("auth_bp.login"))

    teacher = get_teacher_by_id(teacher_id)
    subjects = get_all_subjects()
    teacher_subjects = [s['id'] for s in get_teacher_subjects(teacher_id)]

    if not teacher:
        flash("لم يتم العثور على المعلم", "danger")
        return redirect(url_for('teacher_bp.teachers_list'))

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        teacher_code = request.form.get('teacher_code')
        selected_subjects = request.form.getlist('subjects')

        update_teacher(
            teacher_id=teacher_id,
            name=name,
            username=username,
            password=password if password else None,
            teacher_code=teacher_code
        )

        flash("تم تحديث بيانات المعلم بنجاح", "success")
        return redirect(url_for('teacher_bp.teachers_list'))

    return render_template("teachers/edit.html",
                           teacher=teacher,
                           subjects=subjects,
                           teacher_subjects=teacher_subjects)

# ============================
# حذف معلم
# ============================
@teacher_bp.route('/teachers/delete/<int:teacher_id>')
def delete_teacher_route(teacher_id):
    if 'user_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "warning")
        return redirect(url_for("auth_bp.login"))

    delete_teacher(teacher_id)
    flash("تم حذف المعلم بنجاح", "success")
    return redirect(url_for('teacher_bp.teachers_list'))

# ============================
# البحث عن معلمين بالاسم
# ============================
@teacher_bp.route('/teachers/search', methods=['GET'])
def search_teachers():
    if 'user_id' not in session:
        flash("الرجاء تسجيل الدخول أولاً", "warning")
        return redirect(url_for("auth_bp.login"))

    keyword = request.args.get('q', '')
    if keyword:
        teachers = search_teachers_by_name(keyword)
    else:
        teachers = get_all_teachers()

    return render_template('teachers/list.html', teachers=teachers, search_query=keyword)
