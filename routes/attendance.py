# routes/attendance.py
from flask import Blueprint, request, jsonify
from models.attendance import (
    add_attendance, get_attendance_by_id,
    get_attendance_for_student, get_attendance_for_class,
    update_attendance, delete_attendance
)

attendance_bp = Blueprint("attendance_bp", __name__)

# إضافة سجل حضور
@attendance_bp.route("/attendance", methods=["POST"])
def route_add_attendance():
    data = request.json or {}
    student_id = data.get("student_id")
    class_id = data.get("class_id")
    date = data.get("date")
    status = data.get("status")
    note = data.get("note")

    if not student_id or not class_id or not date or not status:
        return jsonify({"error": "student_id, class_id, date, status مطلوبين"}), 400

    att_id = add_attendance(student_id, class_id, date, status, note)
    return jsonify({"message": "تم إضافة سجل الحضور", "attendance_id": att_id}), 201

# جلب سجل واحد
@attendance_bp.route("/attendance/<int:att_id>", methods=["GET"])
def route_get_attendance(att_id):
    row = get_attendance_by_id(att_id)
    if not row:
        return jsonify({"error": "السجل غير موجود"}), 404
    return jsonify(row)

# جلب حضور طالب
@attendance_bp.route("/students/<int:student_id>/attendance", methods=["GET"])
def route_get_student_attendance(student_id):
    rows = get_attendance_for_student(student_id)
    return jsonify(rows)

# جلب حضور صف في يوم معين
@attendance_bp.route("/classes/<int:class_id>/attendance/<date>", methods=["GET"])
def route_get_class_attendance(class_id, date):
    rows = get_attendance_for_class(class_id, date)
    return jsonify(rows)

# تحديث حضور
@attendance_bp.route("/attendance/<int:att_id>", methods=["PUT"])
def route_update_attendance(att_id):
    data = request.json or {}
    update_attendance(att_id, status=data.get("status"), note=data.get("note"))
    return jsonify({"message": "تم تحديث السجل"})

# حذف حضور
@attendance_bp.route("/attendance/<int:att_id>", methods=["DELETE"])
def route_delete_attendance(att_id):
    delete_attendance(att_id)
    return jsonify({"message": "تم حذف السجل"})
