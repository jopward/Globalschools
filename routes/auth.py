from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import verify_user, create_user, get_user_by_username
from models.school import get_all_schools

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# ===============================
# 🟢 تسجيل الدخول
# ===============================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # إذا المستخدم مسجل دخول فعلاً، نوجهه مباشرة حسب دوره
    if 'user' in session:
        user = session['user']
        if user['role'] == 'superadmin':
            return redirect(url_for('auth_bp.superadmin_page'))
        elif user['role'] == 'teacher':
            return redirect(url_for('attendance_bp.update_attendance_page'))
        else:
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('الرجاء إدخال اسم المستخدم وكلمة المرور.', 'warning')
            return redirect(url_for('auth_bp.login'))

        # التحقق من صحة بيانات الدخول
        user = verify_user(username, password)
        if not user:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
            return redirect(url_for('auth_bp.login'))

        # ✅ حفظ جميع بيانات المستخدم داخل session
        session['user'] = {
            'id': user['id'],
            'name': user['name'],
            'username': user['username'],
            'role': user['role'],
            'school_id': user.get('school_id'),
            'teacher_code': user.get('teacher_code'),
            'is_authenticated': True
        }

        flash(f"مرحباً {user['name']}!", "success")

        # ✅ التوجيه حسب الدور
        if user['role'] == 'superadmin':
            return redirect(url_for('auth_bp.superadmin_page'))
        elif user['role'] == 'teacher':
            return redirect(url_for('attendance_bp.update_attendance_page'))
        else:
            return redirect(url_for('dashboard'))

    return render_template('login.html')


# ===============================
# 🔴 تسجيل الخروج
# ===============================
@auth_bp.route('/logout')
def logout():
    if 'user' in session:
        name = session['user'].get('name', 'المستخدم')
        flash(f"تم تسجيل الخروج بنجاح، إلى اللقاء {name} 👋", "success")
    session.clear()
    return redirect(url_for('auth_bp.login'))


# ===============================
# 🏫 صفحة Super Admin
# ===============================
@auth_bp.route('/superadmin')
def superadmin_page():
    user = session.get('user')

    if not user or user.get('role') != 'superadmin':
        flash('🚫 لا تمتلك صلاحية الوصول لهذه الصفحة.', 'danger')
        return redirect(url_for('auth_bp.login'))

    schools = get_all_schools()
    return render_template('superadmin.html', user=user, schools=schools)


# ===============================
# 🧾 تسجيل مستخدم جديد (Register)
# ===============================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    schools = get_all_schools()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role')
        school_id = request.form.get('school_id')
        teacher_code = request.form.get('teacher_code', '').strip()

        # التحقق من الحقول الأساسية
        if not all([name, username, password, role, school_id]):
            flash('⚠️ الرجاء تعبئة جميع الحقول المطلوبة.', 'warning')
            return redirect(url_for('auth_bp.register'))

        # تحقق إضافي: في حال كان المستخدم "teacher"
        if role == 'teacher' and not teacher_code:
            flash('يرجى إدخال كود المعلم.', 'warning')
            return redirect(url_for('auth_bp.register'))

        # التأكد من أن اسم المستخدم غير مستخدم مسبقاً
        existing_user = get_user_by_username(username)
        if existing_user:
            flash('اسم المستخدم موجود مسبقًا، الرجاء اختيار اسم آخر.', 'danger')
            return redirect(url_for('auth_bp.register'))

        # إنشاء المستخدم في قاعدة البيانات
        create_user(
            name=name,
            username=username,
            password=password,
            role=role,
            school_id=school_id,
            teacher_code=teacher_code if role == 'teacher' else None
        )

        flash('✅ تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html', schools=schools)
