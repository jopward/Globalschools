# routes/class_subjects.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from models.class_subjects import (
    add_class_subject, get_class_subject_by_id, get_all_class_subjects,
    update_class_subject, delete_class_subject
)
from functools import wraps

class_subjects_bp = Blueprint("class_subjects", __name__, url_prefix="/class_subjects")

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
# Routes
# ============================

@class_subjects_bp.route("/", methods=["GET"])
@login_required()
def list_class_subjects():
    """عرض كل الروابط"""
    data = get_all_class_subjects()
    return jsonify(data), 200


@class_subjects_bp.route("/<int:cs_id>", methods=["GET"])
@login_required()
def get_one(cs_id):
    """عرض ربط واحد"""
    item = get_class_subject_by_id(cs_id)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Not found"}), 404


@class_subjects_bp.route("/", methods=["POST"])
@login_required(role="admin")
def create():
    """إضافة ربط جديد"""
    data = request.json
    new_id = add_class_subject(
        data["class_id"], data["subject_id"], data["teacher_id"]
    )
    return jsonify({"id": new_id}), 201


@class_subjects_bp.route("/<int:cs_id>", methods=["PUT"])
@login_required(role="admin")
def update(cs_id):
    """تحديث ربط"""
    data = request.json
    update_class_subject(
        cs_id,
        data.get("class_id"),
        data.get("subject_id"),
        data.get("teacher_id"),
    )
    return jsonify({"message": "Updated successfully"}), 200


@class_subjects_bp.route("/<int:cs_id>", methods=["DELETE"])
@login_required(role="admin")
def delete(cs_id):
    """حذف ربط"""
    delete_class_subject(cs_id)
    return jsonify({"message": "Deleted successfully"}), 200
