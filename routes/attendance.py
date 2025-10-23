from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from functools import wraps
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
    status = data.get("status")  # present / late / absent
    date = data.get("date") or datetime.date.today().isoformat()

    if not student_id or not status:
        return jsonify({"success": False, "error": "student_id و status مطلوبين"}), 400

    conn = get_connection()
    cur = conn.cursor()

    # حذف أي سجل موجود لهذا الطالب في نفس التاريخ
    cur.execute("""
        DELETE FROM student_tracking 
        WHERE student_id = %s AND tracking_date = %s
    """, (student_id, date))

    # إدراج سجل جديد مع الحالة
    cur.execute("""
        INSERT INTO student_tracking (student_id, tracking_date, note)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (student_id, date, status))  # تخزين الحالة في note لحفظها كما في JS
    att_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "attendance_id": att_id})

# ============================
# جلب حضور طالب
# ============================
@attendance_bp.route("/students/<int:student_id>/attendance", methods=["GET"])
@login_required()
def get_student_attendance(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT st.id, st.tracking_date, st.note, s.student_name, tc.id as class_id, tc.class_name, tc.id as section_id, tc.section
        FROM student_tracking st
        JOIN students s ON st.student_id = s.id
        LEFT JOIN teacher_classes tc ON s.class_id = tc.id
        WHERE st.student_id = %s
        ORDER BY st.tracking_date DESC
    """, (student_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rows:
        att_id, tracking_date, note, student_name, class_id, class_name, section_id, section = r
        result.append({
            "id": att_id,
            "student_id": student_id,
            "student_name": student_name,
            "class_id": class_id,
            "class_name": class_name,
            "section_id": section_id,
            "section": section,
            "date": tracking_date.isoformat(),
            "attendance_status": note  # لتوافق مع HTML/JS
        })

    return jsonify(result)

# ============================
# جلب حضور صف في يوم معين
# ============================
@attendance_bp.route("/classes/<int:class_id>/attendance/<date>", methods=["GET"])
@login_required()
def get_class_attendance(class_id, date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT st.id, st.tracking_date, st.note, s.id as student_id, s.student_name, tc.id as class_id, tc.class_name, tc.id as section_id, tc.section
        FROM student_tracking st
        JOIN students s ON st.student_id = s.id
        JOIN teacher_classes tc ON s.class_id = tc.id
        WHERE tc.id = %s AND st.tracking_date = %s
        ORDER BY s.student_name
    """, (class_id, date))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rows:
        att_id, tracking_date, note, student_id, student_name, class_id, class_name, section_id, section = r
        result.append({
            "id": att_id,
            "student_id": student_id,
            "student_name": student_name,
            "class_id": class_id,
            "class_name": class_name,
            "section_id": section_id,
            "section": section,
            "date": tracking_date.isoformat(),
            "attendance_status": note
        })

    return jsonify(result)

# ============================
# حذف حضور
# ============================
@attendance_bp.route("/attendance/<int:att_id>", methods=["DELETE"])
@login_required(role="admin")
def delete_attendance_route(att_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM student_tracking WHERE id = %s", (att_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "تم حذف السجل"})
