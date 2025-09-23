# routes/subjects.py
from flask import Blueprint, request, jsonify
from models.subjects import (
    create_subject, get_subject_by_id, get_all_subjects,
    update_subject, delete_subject
)

subjects_bp = Blueprint("subjects_bp", __name__)

# إضافة مادة
@subjects_bp.route("/subjects", methods=["POST"])
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


# جلب مادة واحدة
@subjects_bp.route("/subjects/<int:subject_id>", methods=["GET"])
def route_get_subject(subject_id):
    row = get_subject_by_id(subject_id)
    if not row:
        return jsonify({"error": "المادة غير موجودة"}), 404
    return jsonify(row)


# جلب جميع المواد
@subjects_bp.route("/subjects", methods=["GET"])
def route_get_all_subjects():
    school_id = request.args.get("school_id")
    rows = get_all_subjects(school_id)
    return jsonify(rows)


# تحديث مادة
@subjects_bp.route("/subjects/<int:subject_id>", methods=["PUT"])
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


# حذف مادة
@subjects_bp.route("/subjects/<int:subject_id>", methods=["DELETE"])
def route_delete_subject(subject_id):
    delete_subject(subject_id)
    return jsonify({"message": "تم حذف المادة"})
