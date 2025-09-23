# routes/tracking.py
from flask import Blueprint, request, jsonify
from models.tracking import (
    add_tracking, get_tracking_by_id, get_tracking_for_student,
    update_tracking, delete_tracking
)

tracking_bp = Blueprint("tracking_bp", __name__)

# إضافة متابعة
@tracking_bp.route("/tracking", methods=["POST"])
def route_add_tracking():
    data = request.json or {}
    student_id = data.get("student_id")
    note = data.get("note")
    created_by = data.get("created_by")  # ممكن يكون user_id

    if not student_id or not note:
        return jsonify({"error": "student_id و note مطلوبان"}), 400

    tid = add_tracking(student_id, note, created_by)
    return jsonify({"message": "تمت إضافة الملاحظة", "tracking_id": tid}), 201

# جلب متابعة واحدة
@tracking_bp.route("/tracking/<int:track_id>", methods=["GET"])
def route_get_tracking(track_id):
    row = get_tracking_by_id(track_id)
    if not row:
        return jsonify({"error": "المتابعة غير موجودة"}), 404
    return jsonify(row)

# جلب كل متابعات طالب
@tracking_bp.route("/students/<int:student_id>/tracking", methods=["GET"])
def route_get_tracking_for_student(student_id):
    rows = get_tracking_for_student(student_id)
    return jsonify(rows)

# تحديث ملاحظة
@tracking_bp.route("/tracking/<int:track_id>", methods=["PUT"])
def route_update_tracking(track_id):
    data = request.json or {}
    update_tracking(track_id, note=data.get("note"))
    return jsonify({"message": "تم تحديث الملاحظة"})

# حذف متابعة
@tracking_bp.route("/tracking/<int:track_id>", methods=["DELETE"])
def route_delete_tracking(track_id):
    delete_tracking(track_id)
    return jsonify({"message": "تم حذف المتابعة"})
