from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from models.subjects import (
    create_subject, get_subject_by_id, get_all_subjects,
    update_subject, delete_subject
)
from functools import wraps

subjects_bp = Blueprint("subjects_bp", __name__)

# ============================
# ديكوريتور للتحقق من تسجيل الدخول والصلاحية
# ============================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("يجب تسجيل الدخول أولاً")
                return redirect(url_for("auth.login"))
            if role and user.get("role") != role:
                flash("لا تمتلك صلاحية الوصول لهذه الصفحة")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# إضافة مادة
# ============================
@subjects_bp.route("/subjects", methods=["POST"])
@login_required(role="admin")
def route_create_subject():
    data = request.json or {}
    name = data.get("name")
    code = data.get("code")
    description = data.get("description")
    school_id = data.get("school_id")

    if not name:
        return jsonify({"error": "اسم المادة مطلوب"}), 400

    subject_id = create_subject(name, code, description, school_id)
    return jsonify({"message": "تمت إضافة المادة", "subject_id": subject_id}), 201

# ============================
# جلب مادة واحدة
# ============================
@subjects_bp.route("/subjects/<int:subject_id>", methods=["GET"])
@login_required()
def route_get_subject(subject_id):
    row = get_subject_by_id(subject_id)
    if not row:
        return jsonify({"error": "المادة غير موجودة"}), 404
    return jsonify(row)

# ============================
# جلب جميع المواد
# ============================
@subjects_bp.route("/subjects", methods=["GET"])
@login_required()
def route_get_all_subjects():
    school_id = request.args.get("school_id")
    rows = get_all_subjects(school_id)
    return jsonify(rows)

# ============================
# تحديث مادة
# ============================
@subjects_bp.route("/subjects/<int:subject_id>", methods=["PUT"])
@login_required(role="admin")
def route_update_subject(subject_id):
    data = request.json or {}
    update_subject(
        subject_id,
        name=data.get("name"),
        code=data.get("code"),
        description=data.get("description"),
        school_id=data.get("school_id")
    )
    return jsonify({"message": "تم تحديث المادة"})

# ============================
# حذف مادة
# ============================
@subjects_bp.route("/subjects/<int:subject_id>", methods=["DELETE"])
@login_required(role="admin")
def route_delete_subject(subject_id):
    delete_subject(subject_id)
    return jsonify({"message": "تم حذف المادة"})
