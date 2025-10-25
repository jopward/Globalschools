from flask import Flask, jsonify
from models.attendance import get_attendance_for_school

app = Flask(__name__)

@app.route('/attendance_test')
def attendance_test():
    # نحدد school_id مؤقتاً، مثلاً 1
    school_id = 1

    # جلب كل الحضور للمدرسة
    data = get_attendance_for_school(school_id)
    
    # تحويل النتائج لقائمة من القواميس
    result = []
    for row in data:
        result.append({
            "id": row[0],
            "student_id": row[1],
            "school_id": row[2],
            "teacher_id": row[3],
            "date": str(row[4]),
            "attendance": row[5],
            "note": row[6],
            "student_name": row[7],
            "teacher_name": row[8],
        })
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
