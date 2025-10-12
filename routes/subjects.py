# routes/subjects.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models.subjects import (
    create_subject,
    get_subject_by_id,
    get_all_subjects,
    update_subject,
    delete_subject,
)

subjects_bp = Blueprint("subjects_bp", __name__, url_prefix="/subjects")


# ==============================
# عرض صفحة المواد + نموذج الإضافة
# ==============================
@subjects_bp.route("/", methods=["GET"])
def subjects_home():
    try:
        school_id = session.get("school_id")  # من الجلسة إن وجد
        subjects = get_all_subjects(school_id)
        return render_template("add_subject.html", subjects=subjects)
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل المواد: {str(e)}")
        return render_template("add_subject.html", subjects=[])


# ==============================
# إنشاء مادة جديدة
# ==============================
@subjects_bp.route("/create", methods=["POST"])
def create_new_subject():
    try:
        name = request.form.get("name")
        code = request.form.get("code")
        description = request.form.get("description")
        school_id = session.get("school_id")

        if not name:
            flash("يجب إدخال اسم المادة.")
            return redirect(url_for("subjects_bp.subjects_home"))

        create_subject(name, code, description, school_id)
        flash("✅ تم إضافة المادة بنجاح.")
    except Exception as e:
        flash(f"❌ حدث خطأ أثناء الإضافة: {str(e)}")

    print("✅ school_id في الجلسة:", school_id)
    return redirect(url_for("subjects_bp.subjects_home"))


# ==============================
# جلب مادة محددة (للتعديل)
# ==============================
@subjects_bp.route("/get/<int:subject_id>", methods=["GET"])
def get_subject_data(subject_id):
    try:
        subject = get_subject_by_id(subject_id)
        if subject:
            return jsonify(subject)
        else:
            return jsonify({"error": "المادة غير موجودة"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# تعديل مادة موجودة
# ==============================
@subjects_bp.route("/update/<int:subject_id>", methods=["POST"])
def update_existing_subject(subject_id):
    try:
        name = request.form.get("name")
        code = request.form.get("code")
        description = request.form.get("description")
        school_id = session.get("school_id")

        update_subject(subject_id, name, code, description, school_id)
        flash("✅ تم تحديث بيانات المادة بنجاح.")
    except Exception as e:
        flash(f"❌ حدث خطأ أثناء التحديث: {str(e)}")

    return redirect(url_for("subjects_bp.subjects_home"))


# ==============================
# حذف مادة
# ==============================
@subjects_bp.route("/delete/<int:subject_id>", methods=["POST"])
def delete_existing_subject(subject_id):
    try:
        delete_subject(subject_id)
        flash("🗑️ تم حذف المادة بنجاح.")
    except Exception as e:
        flash(f"❌ حدث خطأ أثناء الحذف: {str(e)}")

    return redirect(url_for("subjects_bp.subjects_home"))
