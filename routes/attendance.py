from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import date
import psycopg2.extras
from db.db_setup import get_connection

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

# ============================================================
# 🧠 Middleware بسيط للتأكد من تسجيل الدخول
# ============================================================
@attendance_bp.before_request
def check_login():
    """تسجيل دخول مؤقت أثناء التطوير إن لم يوجد مستخدم."""
    if "user_id" not in session:
        session["user_id"] = 1
        session["user_role"] = "teacher"
        session["school_id"] = 1


# ============================================================
# 📄 عرض صفحة الحضور
# ============================================================
@attendance_bp.route("/page")
def attendance_page():
    user_id = session.get("user_id")
    school_id = session.get("school_id")
    role = session.get("user_role")
    today = date.today().isoformat()

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 🔹 جلب الصفوف والشعب من جدول teacher_classes
        cur.execute("""
            SELECT id, class_name, section, period
            FROM teacher_classes
            WHERE school_id = %s
            ORDER BY class_name
        """, (school_id,))
        classes = cur.fetchall()

        # 🔹 جلب الطلاب
        if role == "admin":
            cur.execute("""
                SELECT 
                    s.id AS student_id,
                    s.student_name,
                    tc.class_name,
                    tc.section,
                    st.attendance,
                    st.id AS tracking_id,
                    st.note
                FROM students s
                LEFT JOIN teacher_classes tc ON s.class_id = tc.id
                LEFT JOIN student_tracking st 
                    ON st.student_id = s.id
                    AND st.school_id = %s
                    AND st.date = %s
                WHERE s.school_id = %s
                ORDER BY tc.class_name, s.student_name
            """, (school_id, today, school_id))
        else:
            cur.execute("""
                SELECT 
                    s.id AS student_id,
                    s.student_name,
                    tc.class_name,
                    tc.section,
                    st.attendance,
                    st.id AS tracking_id,
                    st.note
                FROM students s
                LEFT JOIN teacher_classes tc ON s.class_id = tc.id
                LEFT JOIN student_tracking st 
                    ON st.student_id = s.id
                    AND st.teacher_id = %s
                    AND st.school_id = %s
                    AND st.date = %s
                WHERE s.school_id = %s AND tc.teacher_id = %s
                ORDER BY tc.class_name, s.student_name
            """, (user_id, school_id, today, school_id, user_id))

        students = cur.fetchall()

        # 🔹 جلب آخر 10 تواريخ فيها سجلات
        cur.execute("""
            SELECT DISTINCT date 
            FROM student_tracking 
            WHERE school_id = %s
            ORDER BY date DESC
            LIMIT 10
        """, (school_id,))
        date_list = [row["date"].isoformat() for row in cur.fetchall()]

    finally:
        cur.close()
        conn.close()

    # 🟢 تمرير كل القيم إلى القالب
    return render_template(
        "attendance.html",
        students=students,
        today=today,
        classes=classes,
        date_list=date_list
    )


# ============================================================
# ✅ إضافة أو تحديث حضور لطالب
# ============================================================
@attendance_bp.route("/update", methods=["POST"])
def update_attendance():
    data = request.get_json()
    student_id = data.get("student_id")
    status = data.get("status")
    note = data.get("note") or None
    date_val = data.get("date") or date.today().isoformat()

    teacher_id = session.get("user_id")
    school_id = session.get("school_id")

    if not student_id or not status:
        return jsonify({"success": False, "error": "student_id و status مطلوبان"}), 400

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 🧹 حذف أي سجل سابق لنفس الطالب/المعلم في نفس اليوم
        cur.execute("""
            DELETE FROM student_tracking
            WHERE student_id = %s AND date = %s AND school_id = %s AND teacher_id = %s
        """, (student_id, date_val, school_id, teacher_id))

        # ➕ إدخال سجل جديد
        cur.execute("""
            INSERT INTO student_tracking (student_id, school_id, teacher_id, date, attendance, note)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (student_id, school_id, teacher_id, date_val, status, note))

        tracking_id = cur.fetchone()["id"]
        conn.commit()

        return jsonify({"success": True, "tracking_id": tracking_id})

    except Exception as e:
        conn.rollback()
        print("❌ خطأ أثناء حفظ الحضور:", e)
        return jsonify({"success": False, "error": str(e)})
    finally:
        cur.close()
        conn.close()


# ============================================================
# 🗑️ حذف سجل حضور
# ============================================================
@attendance_bp.route("/delete", methods=["POST"])
def delete_attendance():
    data = request.get_json()
    tracking_id = data.get("tracking_id")
    if not tracking_id:
        return jsonify({"success": False, "error": "tracking_id مطلوب"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM student_tracking WHERE id=%s", (tracking_id,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        cur.close()
        conn.close()


# ============================================================
# 🔍 جلب بيانات الحضور لتاريخ معين
# ============================================================
@attendance_bp.route("/filter", methods=["GET"])
def filter_attendance():
    school_id = session.get("school_id")
    teacher_id = session.get("user_id")
    date_val = request.args.get("date") or date.today().isoformat()
    role = session.get("user_role")

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        if role == "admin":
            cur.execute("""
                SELECT 
                    st.*, 
                    s.student_name, 
                    tc.class_name, 
                    tc.section
                FROM student_tracking st
                LEFT JOIN students s ON st.student_id = s.id
                LEFT JOIN teacher_classes tc ON s.class_id = tc.id
                WHERE st.school_id = %s AND st.date = %s
                ORDER BY s.student_name
            """, (school_id, date_val))
        else:
            cur.execute("""
                SELECT 
                    st.*, 
                    s.student_name, 
                    tc.class_name, 
                    tc.section
                FROM student_tracking st
                LEFT JOIN students s ON st.student_id = s.id
                LEFT JOIN teacher_classes tc ON s.class_id = tc.id
                WHERE st.school_id = %s AND st.date = %s AND st.teacher_id = %s
                ORDER BY s.student_name
            """, (school_id, date_val, teacher_id))

        rows = cur.fetchall()
        return jsonify(rows)

    except Exception as e:
        print("❌ خطأ أثناء فلترة الحضور:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
