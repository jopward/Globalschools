from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from db import get_db_connection, User

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        remember = request.form.get('remember')

        # البحث عن المستخدم في قاعدة البيانات
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.')
            return redirect(url_for('auth_bp.login'))

        # حفظ بيانات المستخدم في الجلسة
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name

        # توجيه المستخدم حسب دوره
        if user.role == 'admin':
            return redirect(url_for('dashboard'))  # صفحة المسؤول
        elif user.role == 'teacher':
            return redirect(url_for('dashboard'))  # صفحة المعلم
        else:
            return redirect(url_for('dashboard'))  # صفحة الطالب

    return render_template('login.html')
