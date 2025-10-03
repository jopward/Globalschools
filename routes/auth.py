from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import verify_user, get_user_by_id, create_user  # إضافة create_user

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

        # حفظ بيانات المستخدم في الجلسة
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        session['user_name'] = user['name']

        # توجيه المستخدم حسب دوره
        if user['role'] == 'admin':
            return redirect(url_for('dashboard'))
        elif user['role'] == 'teacher':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard'))

    return render_template('login.html')


# --- تسجيل الخروج ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.')
    return redirect(url_for('auth_bp.login'))


# --- صفحة التسجيل (Register) ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        role = request.form['role']  # student أو teacher

        # التحقق من الحقول
        if not name or not username or not password or not role:
            flash('الرجاء تعبئة جميع الحقول.')
            return redirect(url_for('auth_bp.register'))

        # تحقق من اسم المستخدم
        existing_user = verify_user(username, password)
        if existing_user:
            flash('اسم المستخدم موجود مسبقًا.')
            return redirect(url_for('auth_bp.register'))

        # إنشاء المستخدم في قاعدة البيانات
        user_id = create_user(name, username, password, role)

        flash('تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html')
