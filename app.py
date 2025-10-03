from flask import Flask, jsonify, render_template, session, redirect, url_for

# Blueprints
from routes.user import user_bp
from routes.students import student_bp
from routes.teachers import teacher_bp
from routes.school import school_bp
from routes.subjects import subjects_bp
from routes.classes import classes_bp
from routes.attendance import attendance_bp
from routes.grades import grades_bp
from routes.tracking import tracking_bp
from routes.auth import auth_bp  # <-- إضافة auth
from routes.pages.smart import smart_bp

app = Flask(__name__, template_folder="templates")
app.secret_key = "YOUR_SECRET_KEY"  # <-- غيره لمفتاح قوي

# --- تسجيل Blueprints ---
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(student_bp, url_prefix='/students')
app.register_blueprint(teacher_bp, url_prefix='/teachers')
app.register_blueprint(school_bp, url_prefix='/schools')
app.register_blueprint(subjects_bp, url_prefix='/subjects')
app.register_blueprint(classes_bp, url_prefix='/classes')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(grades_bp, url_prefix='/grades')
app.register_blueprint(tracking_bp, url_prefix='/tracking')
app.register_blueprint(smart_bp, url_prefix='/smart')  # <-- Smart

# --- Dashboard ديناميكي حسب الدور ---
@app.route("/")
@app.route("/dashboard")
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))  # توجيه لصفحة تسجيل الدخول
    return render_template("dashboard.html", user=user)

# --- صفحة Smart ---
@app.route("/smart")
def smart_page():
    smart_pages = ["Smart 1"]
    return render_template(
        "smart.html",
        students=[],  # سيتم جلب البيانات ديناميكياً من API
        classes=[],
        sections=[],
        smart_pages=smart_pages
    )

# --- Route اختبارية عامة ---
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

if __name__ == "__main__":
    app.run(debug=True)
