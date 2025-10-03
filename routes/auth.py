from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import verify_user, get_user_by_id   # استدعاء الدوال من ملف user.py

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

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


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.')
    return redirect(url_for('auth_bp.login'))
