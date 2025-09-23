# routes/auth.py
from flask import Blueprint, request, jsonify, session
from models.user import verify_user  # استدعاء دوال التحقق من الموديل

# تعريف الـ Blueprint
auth_bp = Blueprint("auth_bp", __name__)

# =============================
# راوتات تسجيل الدخول والخروج
# =============================

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    تسجيل الدخول: يتحقق من اسم المستخدم وكلمة المرور.
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = verify_user(username, password)
    if user:
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        return jsonify({"message": "تم تسجيل الدخول بنجاح", "user": user}), 200
    return jsonify({"message": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    تسجيل الخروج: يحذف بيانات الجلسة.
    """
    session.pop("user_id", None)
    session.pop("role", None)
    return jsonify({"message": "تم تسجيل الخروج بنجاح"}), 200
