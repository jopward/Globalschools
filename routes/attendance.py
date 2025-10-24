from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from models.attendance import add_attendance, update_attendance, delete_attendance, filter_attendance
from db.db_setup import get_connection
import datetime

attendance_bp = Blueprint("attendance_bp", __name__)

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
    cur.execute("DELETE FROM student_tracking WHERE student_id = %s AND date = %s", (student_id, date_str))
    conn.commit()
    cur.close()
    conn.close()

    # إضافة السجل الجديد باستخدام الموديل
    att_id = add_attendance(student_id, school_id, teacher_id, date_str, attendance_status, note)
    return jsonify({"success": True, "attendance_id": att_id})

# ============================
# جلب حضور طالب
# ============================
@attendance_bp.route("/students/<int:student_id>/attendance", methods=["GET"])
@login_required()
def get_student_attendance(student_id):
    rows = filter_attendance(student_id=student_id)
    result = []
    for r in rows:
        att_id, student_id, school_id, teacher_id, date_val, attendance_status, note, student_name, teacher_name = r
        result.append({
            "id": att_id,
            "student_id": student_id,
            "student_name": student_name,
            "school_id": school_id,
            "teacher_id": teacher_id,
            "teacher_name": teacher_name,
            "date": date_val.isoformat(),
            "attendance_status": attendance_status,
            "note": note
        })
    return jsonify(result)

# ============================
# جلب حضور صف في يوم معين
# ============================
@attendance_bp.route("/classes/<int:class_id>/attendance/<date_str>", methods=["GET"])
@login_required()
def get_class_attendance(class_id, date_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT s.id FROM students s JOIN teacher_classes tc ON s.class_id = tc.id WHERE tc.id = %s", (class_id,))
    student_rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for student in student_rows:
        student_id = student[0]
        rows = filter_attendance(student_id=student_id, start_date=date_str, end_date=date_str)
        for r in rows:
            att_id, _, school_id, teacher_id, date_val, attendance_status, note, student_name, teacher_name = r
            result.append({
                "id": att_id,
                "student_id": student_id,
                "student_name": student_name,
                "school_id": school_id,
                "teacher_id": teacher_id,
                "teacher_name": teacher_name,
                "class_id": class_id,
                "date": date_val.isoformat(),
                "attendance_status": attendance_status,
                "note": note
            })
    return jsonify(result)

# ============================
# حذف حضور
# ============================
@attendance_bp.route("/attendance/<int:att_id>", methods=["DELETE"])
@login_required(role="admin")
def delete_attendance_route(att_id):
    delete_attendance(att_id)
    return jsonify({"message": "تم حذف السجل"})
