from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # 在应用上下文中导入模型
    with app.app_context():
        # 导入模型以确保它们被注册到SQLAlchemy
        from app.models import user, recipe, ingredient, favorite
    
    # 注册蓝图
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app