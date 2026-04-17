import os
import sys
import hashlib
import atexit
from flask import Flask
from config import Config

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    from models import db
    db.init_app(app)
    
    from services.ai_service import ai_bp
    from routes.client import client_bp, make_slug as client_slug
    from routes.admin import admin_bp
    
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 启动定时调度器
    from services.scheduler import start_news_scheduler
    start_news_scheduler(app)
    
    # 注册退出时关闭调度器
    from services.scheduler import stop_news_scheduler
    atexit.register(stop_news_scheduler)
    
    with app.app_context():
        db.create_all()
        create_default_data()
    
    return app

def create_default_data():
    from models import db, User, Category
    from werkzeug.security import generate_password_hash
    
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
            is_admin=True
        )
        db.session.add(admin)
    
    categories = [
        ('教学笔记', 'teaching-notes', '教师日常教学笔记和心得'),
        ('教育资源', 'educational-resources', '优质教学资源分享'),
        ('教育心得', 'education-experience', '教育理念和方法分享'),
        ('技术教程', 'tech-tutorials', '技术类教学教程'),
        ('生活感悟', 'life-thoughts', '教师生活感悟')
    ]
    
    for name, slug, desc in categories:
        if not Category.query.filter_by(slug=slug).first():
            category = Category(name=name, slug=slug, description=desc)
            db.session.add(category)
    
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
