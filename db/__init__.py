# -*- coding: utf-8 -
from flask_sqlalchemy import SQLAlchemy

# تعريف كائن قاعدة البيانات
db = SQLAlchemy()

def init_db(app):
    """
    تهيئة قاعدة البيانات وربطها مع التطبيق Flask
    """
    db.init_app(app)

    # إنشاء الجداول إذا لم تكن موجودة
    with app.app_context():
        db.create_all()
