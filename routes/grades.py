# routes/grades.py
from flask import Blueprint, request, jsonify
from models.grades import (
    add_grade, get_grade_by_id, get_grades_for_student,
    get_grades_by_subject, update_grade, delete_grade
)

grades_bp = Blueprint("grades_bp", __name__)

# إضافة علامة
@grades_bp.route("/grades", methods=["POST"])
def route_add_grade():
    data = request.json or {}
    student_id = data.get("student_id")
    subject = data.get("subject")
    grade = data.get("grade")
    exam_type = data.get("exam_type")
    date = data.get("date")
    note = data.get("note")

    if not student_id or not subject or grade is None or not exam_type or not date:
        return jsonify({"error": "student_id, subject, grade, exam_type, date مطلوبين"}), 400

    grade_id = add_grade(student_id, subject, grade, exam_type, date, note)
    return jsonify({"message": "تمت إضافة العلامة", "grade_id": grade_id}), 201

# جلب علامة واحدة
@grades_bp.route("/grades/<int:grade_id>", methods=["GET"])
def route_get_grade(grade_id):
    row = get_grade_by_id(grade_id)
    if not row:
        return jsonify({"error": "العلامة غير موجودة"}), 404
    return jsonify(row)

# جلب علامات طالب
@grades_bp.route("/students/<int:student_id>/grades", methods=["GET"])
def route_get_student_grades(student_id):
    rows = get_grades_for_student(student_id)
    return jsonify(rows)

# جلب علامات طالب في مادة
@grades_bp.route("/students/<int:student_id>/grades/<subject>", methods=["GET"])
def route_get_student_subject_grades(student_id, subject):
    rows = get_grades_by_subject(student_id, subject)
    return jsonify(rows)

# تحديث علامة
@grades_bp.route("/grades/<int:grade_id>", methods=["PUT"])
def route_update_grade(grade_id):
    data = request.json or {}
    update_grade(
        grade_id,
        grade=data.get("grade"),
        exam_type=data.get("exam_type"),
        note=data.get("note"),
    )
    return jsonify({"message": "تم تحديث العلامة"})

# حذف علامة
@grades_bp.route("/grades/<int:grade_id>", methods=["DELETE"])
def route_delete_grade(grade_id):
    delete_grade(grade_id)
    return jsonify({"message": "تم حذف العلامة"})
