from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from models.attendance import add_attendance, update_attendance, delete_attendance, filter_attendance
from db.db_setup import get_connection
import datetime

attendance_bp = Blueprint("attendance_bp", __name__, url_prefix="/attendance")

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
# إضافة أو تحديث سجل حضور للطالب
# ============================
@attendance_bp.route("/update_attendance", methods=["POST"])
@login_required(role="admin")
def update_attendance_route():
    data = request.json or {}
    student_id = data.get("student_id")
    attendance_status = data.get("status")
    date_str = data.get("date") or datetime.date.today().isoformat()
    school_id = data.get("school_id")
    teacher_id = data.get("teacher_id")
    note = data.get("note") or attendance_status

    if not student_id or not attendance_status or not school_id or not teacher_id:
        return jsonify({"success": False, "error": "student_id, status, school_id و teacher_id مطلوبة"}), 400

    # حذف أي سجل موجود لنفس الطالب في نفس التاريخ
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM student_tracking WHERE student_id = %s AND date = %s AND school_id = %s",
        (student_id, date_str, school_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    # إضافة السجل الجديد باستخدام الموديل
    att_id = add_attendance(student_id, school_id, teacher_id, date_str, attendance_status, note)
    return jsonify({"success": True, "tracking_id": att_id})

# ============================
# حذف حضور
# ============================
@attendance_bp.route("/delete_attendance", methods=["POST"])
@login_required(role="admin")
def delete_attendance_route():
    data = request.json or {}
    tracking_id = data.get("tracking_id")
    if not tracking_id:
        return jsonify({"success": False, "error": "tracking_id مطلوب"}), 400

    delete_attendance(tracking_id)
    return jsonify({"success": True})
