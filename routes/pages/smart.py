from flask import Blueprint, request, jsonify
from models.student import get_all_students, search_students_by_name, filter_students_by_class, filter_students_by_school

smart_bp = Blueprint('smart_bp', __name__, url_prefix='/smart')

# ============================
# صفحة ذكية: الطلاب
# ============================

@smart_bp.route('/students', methods=['GET'])
def smart_get_students():
    """
    استرجاع جميع الطلاب أو فلترة حسب الصف أو المدرسة أو البحث بالاسم
    Query Parameters:
    - class_id: اختياري
    - school_id: اختياري
    - q: اختياري (كلمة البحث)
    """
    class_id = request.args.get('class_id')
    school_id = request.args.get('school_id')
    keyword = request.args.get('q')

    students = []

    # البحث أولاً إذا تم تمرير كلمة البحث
    if keyword:
        students = search_students_by_name(keyword)
    # فلترة حسب الصف
    elif class_id:
        students = filter_students_by_class(class_id)
    # فلترة حسب المدرسة
    elif school_id:
        students = filter_students_by_school(school_id)
    else:
        # استرجاع جميع الطلاب إذا لم يتم تمرير أي فلتر
        students = get_all_students()

    # إعادة قائمة الاسماء فقط (ممكن لاحقاً إضافة أي حقل آخر)
    result = [{"id": s["id"], "student_name": s["student_name"]} for s in students]

    return jsonify(result)
