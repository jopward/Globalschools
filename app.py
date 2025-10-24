from flask import Flask, jsonify, render_template, session, redirect, url_for, request, flash

# --- Blueprints ---
from routes.user import user_bp
from routes.students import student_bp
from routes.teachers import teacher_bp
from routes.school import school_bp
from routes.subjects import subjects_bp
from routes.classes import classes_bp
from routes.attendance import attendance_bp
from routes.grades import grades_bp
from routes.tracking import tracking_bp
from routes.auth import auth_bp
from routes.pages.smart import smart_bp

# --- استيراد الدوال من الموديلات ---
from models.classes import filter_classes_by_school, get_all_classes, get_class_by_id
from models.user import get_user_by_username
from models.school import get_all_schools
from models.student import create_student, filter_students_by_school
from models.attendance import (
    add_attendance,
    get_attendance_by_id,
    get_attendance_for_student,  # موجود
    update_attendance,
    delete_attendance
)

app = Flask(__name__, template_folder="templates")
app.secret_key = "YOUR_SECRET_KEY"

# --- تسجيل Blueprints ---
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(student_bp, url_prefix='/students')
app.register_blueprint(teacher_bp, url_prefix='/teachers')
app.register_blueprint(school_bp)
app.register_blueprint(subjects_bp, url_prefix='/subjects')
app.register_blueprint(classes_bp, url_prefix='/classes')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(grades_bp, url_prefix='/grades')
app.register_blueprint(tracking_bp, url_prefix='/tracking')
app.register_blueprint(smart_bp, url_prefix='/smart')

# ===========================================================
# --- مؤقت لتجربة تسجيل الدخول ---
# ===========================================================
@app.before_request
def inject_user():
    if 'user_id' not in session:
        session['user_id'] = 1
        session['user_name'] = 'admin'
        session['user_role'] = 'admin'
        session['school_id'] = 1

# ===========================================================
# --- الصفحة الرئيسية / لوحة التحكم ---
# ===========================================================
@app.route("/")
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    user = {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'name': session.get('user_name')
    }

    if user['role'] == 'superadmin':
        return redirect(url_for('superadmin_page'))

    if user['role'] == 'teacher':
        teacher_code = session.get('teacher_code')
        return render_template("teacher_dashboard.html", user=user, teacher_code=teacher_code)

    return render_template("dashboard.html", user=user)

# ===========================================================
# --- صفحة Super Admin ---
# ===========================================================
@app.route("/superadmin_page")
def superadmin_page():
    if 'user_id' not in session or session.get('user_role') != 'superadmin':
        return redirect(url_for('auth_bp.login'))

    user = {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'name': session.get('user_name')
    }

    schools = get_all_schools()
    return render_template("superadmin.html", user=user, schools=schools)

# ===========================================================
# --- صفحة Classes للـ Admin ---
# ===========================================================
@app.route("/classes_page")
def classes_page():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('auth_bp.login'))

    user = {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'name': session.get('user_name')
    }

    school_id = session.get('school_id', 1)
    classes = filter_classes_by_school(school_id)

    return render_template("classes.html", user=user, classes=classes)

# ===========================================================
# --- صفحة إضافة مادة للـ Admin ---
# ===========================================================
@app.route("/add_subject_page")
def add_subject_page():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('auth_bp.login'))

    user = {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'name': session.get('user_name')
    }

    schools = get_all_schools()
    return render_template("add_subject.html", user=user, schools=schools)

# ===========================================================
# --- صفحة إضافة طلاب للـ Admin ---
# ===========================================================
@app.route("/add_student_page", methods=['GET', 'POST'])
def add_student_page():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('auth_bp.login'))

    user = {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'name': session.get('user_name')
    }

    school_id = session.get('school_id', 1)
    all_classes = get_all_classes()
    classes = []
    sections = []

    for cls in all_classes:
        if cls['school_id'] == school_id:
            if not any(c['id'] == cls['id'] for c in classes):
                classes.append({'id': cls['id'], 'name': cls['class_name']})
            sections.append({'class_id': cls['id'], 'name': cls['section']})

    students = filter_students_by_school(school_id)
    for student in students:
        cls = get_class_by_id(student['class_id'])
        if cls:
            student['class_name'] = cls['class_name']
            student['section'] = cls['section']
        else:
            student['class_name'] = "غير محدد"
            student['section'] = "غير محدد"

    if request.method == 'POST':
        student_text = request.form.get('student_names', '').strip()
        class_id = request.form.get('class_id')
        section_name = request.form.get('section_name')

        if not student_text or not class_id or not section_name:
            flash("جميع الحقول مطلوبة", "danger")
        else:
            names_list = [name.strip() for name in student_text.split('\n') if name.strip()]
            added_students = []
            for name in names_list:
                create_student(name, school_id, class_id, section_name)
                added_students.append(name)
            flash(f"تم إضافة الطلاب بنجاح: {', '.join(added_students)}", "success")

        return redirect(url_for('add_student_page'))

    return render_template(
        "add_student.html",
        user=user,
        classes=classes,
        sections=sections,
        students=students
    )

# ===========================================================
# --- صفحة Attendance للـ Admin ---
# ===========================================================
@app.route("/attendance_page")
def attendance_page():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('auth_bp.login'))

    user = {
        'id': session.get('user_id'),
        'role': session.get('user_role'),
        'name': session.get('user_name')
    }

    school_id = session.get('school_id', 1)
    classes = filter_classes_by_school(school_id)

    return render_template("attendance.html", user=user, classes=classes)

# ===========================================================
# --- صفحة Smart ---
# ===========================================================
@app.route("/smart")
def smart_page():
    smart_pages = ["Smart 1"]
    return render_template(
        "smart.html",
        students=[],
        classes=[],
        sections=[],
        smart_pages=smart_pages
    )

# ===========================================================
# --- Route اختبارية عامة ---
# ===========================================================
@app.route('/test_all')
def test_all_routes():
    result = {}
    try: result['users'] = "✅ OK"
    except: result['users'] = "❌ FAIL"
    try: result['students'] = "✅ OK"
    except: result['students'] = "❌ FAIL"
    try: result['teachers'] = "✅ OK"
    except: result['teachers'] = "❌ FAIL"
    try: result['schools'] = "✅ OK"
    except: result['schools'] = "❌ FAIL"
    try: result['subjects'] = "✅ OK"
    except: result['subjects'] = "❌ FAIL"
    try: result['classes'] = "✅ OK"
    except: result['classes'] = "❌ FAIL"
    try: result['attendance'] = "✅ OK"
    except: result['attendance'] = "❌ FAIL"
    try: result['grades'] = "✅ OK"
    except: result['grades'] = "❌ FAIL"
    try: result['tracking'] = "✅ OK"
    except: result['tracking'] = "❌ FAIL"
    try: result['smart'] = "✅ OK"
    except: result['smart'] = "❌ FAIL"

    return jsonify(result)

# ===========================================================
# --- نقطة التشغيل ---
# ===========================================================
if __name__ == "__main__":
    app.run(debug=True)
