# test.py
# تجربة جميع الموديلات CRUD وطباعة النتائج

import models.user as user
import models.student as students
import models.teacher as teachers
import models.school as school
import models.classes as classes
import models.attendance as attendance
import models.grades as grades
import models.subjects as subjects
import models.tracking as tracking
import models.class_subjects as class_subjects

def print_separator():
    print("\n" + "="*50 + "\n")

def test_users():
    print("=== Users ===")
    uid = user.create_user("Ali", "ali123", "1234", "teacher", 1)
    print("تم إنشاء مستخدم:", uid)
    u = user.get_user_by_id(uid)
    print("استرجاع مستخدم:", u)
    print_separator()

def test_schools():
    print("=== Schools ===")
    school_id = school.create_school("مدرسة التجربة")
    print("تم إنشاء مدرسة:", school_id)
    all_schools = school.get_schools()
    print("جميع المدارس:", all_schools)
    print_separator()
    return school_id

def test_students(school_id):
    print("=== Students ===")
    student_id = students.create_student("طالب 1", school_id, 1)
    print("تم إنشاء طالب:", student_id)
    s = students.get_student_by_id(student_id)
    print("استرجاع طالب:", s)
    print_separator()
    return student_id

def test_subjects():
    print("=== Subjects ===")
    subj_id = subjects.create_subject("رياضيات")
    print("تم إنشاء مادة:", subj_id)
    all_subj = subjects.list_subjects()
    print("جميع المواد:", all_subj)
    print_separator()
    return subj_id

def test_classes(school_id):
    print("=== Classes ===")
    class_id = classes.create_class("الصف السابع", "أ", "صباحي", school_id)
    print("تم إنشاء صف:", class_id)
    all_classes = classes.list_classes()
    print("جميع الصفوف:", all_classes)
    print_separator()
    return class_id

def test_attendance(student_id, class_id):
    print("=== Attendance ===")
    attendance_id = attendance.add_attendance(student_id, class_id, "2025-09-23", "present")
    print("تم إضافة حضور:", attendance_id)
    print_separator()

def test_tracking(student_id, class_id, school_id):
    print("=== Tracking ===")
    track_id = tracking.add_tracking(student_id, class_id, school_id, "تم المتابعة")
    print("تم إضافة تتبع:", track_id)
    print_separator()
    return track_id

def test_class_subjects(class_id, subj_id, teacher_id):
    print("=== Class Subjects ===")
    class_subj_id = class_subjects.add_class_subject(class_id, subj_id, teacher_id)
    print("تم إضافة مادة للصف:", class_subj_id)
    print_separator()
    return class_subj_id

def test_grades(student_id, class_subj_id):
    print("=== Grades ===")
    grade_id = grades.add_grade(student_id, class_subj_id, 95)
    print("تم إضافة علامة:", grade_id)
    print_separator()

if __name__ == "__main__":
    test_users()
    school_id = test_schools()
    student_id = test_students(school_id)
    subj_id = test_subjects()
    class_id = test_classes(school_id)
    test_attendance(student_id, class_id)
    test_tracking(student_id, class_id, school_id)
    class_subj_id = test_class_subjects(class_id, subj_id, 1)  # افترضنا teacher_id = 1
    test_grades(student_id, class_subj_id)
