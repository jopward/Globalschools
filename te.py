# register_admin.py
from werkzeug.security import generate_password_hash
from db import get_db_connection, User

def create_admin():
    db = get_db_connection()

    # بيانات المدير
    username = "school_admin1"
    email = "admin1@test.com"
    raw_password = "123456"  # كلمة المرور العادية
    role = "admin"

    # تشفير كلمة المرور
    password_hash = generate_password_hash(raw_password)

    # إنشاء مستخدم جديد
    new_admin = User(username=username, email=email, role=role, password=password_hash)

    # إضافة لقاعدة البيانات
    db.add(new_admin)
    db.commit()

    print(f"✅ تمت إضافة مدير مدرسة: {username} / {email} (الباسورد: {raw_password})")

if __name__ == "__main__":
    create_admin()
