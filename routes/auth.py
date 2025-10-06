from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import verify_user, create_user
from models.school import get_all_schools
from models.teacher import get_teacher_by_code  # دالة جديدة نستخدمها للتحقق من teacher_code

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# --- تسجيل الدخول ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # التحقق من المستخدم
        user = verify_user(username, password)
        if not user:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.')
            return redirect(url_for('auth_bp.login'))

        # حفظ بيانات المستخدم في الجلسة مع school_id
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        session['user_name'] = user['name']
        session['school_id'] = user.get('school_id')  # كل مدرسة ترى بياناتها فقط

        # توجيه المستخدم حسب دوره
        if user['role'] == 'superadmin':
            return redirect(url_for('auth_bp.superadmin_page'))
        else:
            return redirect(url_for('dashboard'))

    return render_template('login.html')


# --- تسجيل الخروج ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.')
    return redirect(url_for('auth_bp.login'))


# --- صفحة Super Admin ---
@auth_bp.route('/superadmin')
def superadmin_page():
    if session.get('user_role') != 'superadmin':
        flash('لا تمتلك صلاحية الوصول لهذه الصفحة')
        return redirect(url_for('auth_bp.login'))

    schools = get_all_schools()
    return render_template('superadmin.html', user=session.get('user_name'), schools=schools)


# --- صفحة التسجيل (Register) ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    schools = get_all_schools()
    if request.method == 'POST':
        name = request.form['name'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        role = request.form['role']
        school_id = request.form.get('school_id')
        teacher_code = request.form.get('teacher_code', '').strip()  # الكود الخاص بالمعلم (اختياري إلا إذا كان Teacher)

        # التحقق من الحقول العامة
        if not name or not username or not password or not role or not school_id:
            flash('الرجاء تعبئة جميع الحقول المطلوبة.')
            return redirect(url_for('auth_bp.register'))

        # إذا كان الدور Teacher، نتحقق من الكود
        if role == 'teacher':
            if not teacher_code:
                flash('يرجى إدخال كود المعلم.')
                return redirect(url_for('auth_bp.register'))

            teacher = get_teacher_by_code(teacher_code)
            if not teacher:
                flash('كود المعلم غير صحيح أو غير موجود.')
                return redirect(url_for('auth_bp.register'))

        # التحقق من وجود المستخدم مسبقًا
        existing_user = verify_user(username, password)
        if existing_user:
            flash('اسم المستخدم موجود مسبقًا.')
            return redirect(url_for('auth_bp.register'))

        # إنشاء المستخدم
        user_id = create_user(name, username, password, role, school_id)

        flash('تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html', schools=schools)
