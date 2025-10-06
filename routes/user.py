from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from db.db_setup import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ============================
# دوال CRUD للمستخدمين
# ============================

def create_user(name, username, password, role, school_id=None, teacher_code=None):
    conn = get_connection()
    cur = conn.cursor()
    hashed_pw = generate_password_hash(password)
    cur.execute("""
        INSERT INTO users (name, username, password, role, school_id, teacher_code)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (name, username, hashed_pw, role, school_id, teacher_code))
    user_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def update_user(user_id, name=None, username=None, password=None, role=None, school_id=None, teacher_code=None):
    conn = get_connection()
    cur = conn.cursor()
    
    updates = []
    values = []

    if name:
        updates.append("name=%s")
        values.append(name)
    if username:
        updates.append("username=%s")
        values.append(username)
    if password:
        updates.append("password=%s")
        values.append(generate_password_hash(password))
    if role:
        updates.append("role=%s")
        values.append(role)
    if school_id:
        updates.append("school_id=%s")
        values.append(school_id)
    if teacher_code:
        updates.append("teacher_code=%s")
        values.append(teacher_code)
    
    if updates:
        query = f"UPDATE users SET {', '.join(updates)} WHERE id=%s"
        values.append(user_id)
        cur.execute(query, tuple(values))
        conn.commit()
    
    cur.close()
    conn.close()
    return True

def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

# ============================
# Blueprint للمستخدمين
# ============================
user_bp = Blueprint("user_bp", __name__, url_prefix="/users")

@user_bp.route("/")
def list_users():
    # هنا يمكن لاحقاً جلب جميع المستخدمين
    return "صفحة جميع المستخدمين"

@user_bp.route("/add", methods=["GET", "POST"])
def add_user_page():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")
        school_id = request.form.get("school_id")
        teacher_code = request.form.get("teacher_code")
        create_user(name, username, password, role, school_id, teacher_code)
        flash("تم إضافة المستخدم بنجاح")
        return redirect(url_for("user_bp.list_users"))
    return render_template("add_user.html")
