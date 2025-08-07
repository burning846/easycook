import os
import logging
from flask import jsonify

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app import create_app
    logger.info("Successfully imported create_app")
    
    app = create_app()
    logger.info("Successfully created Flask app")
    
    # 测试配置
    with app.app_context():
        logger.info(f"Google Client ID configured: {bool(app.config.get('GOOGLE_CLIENT_ID') and app.config.get('GOOGLE_CLIENT_ID') != 'your-google-client-id')}")
        logger.info(f"Database URL configured: {bool(app.config.get('DATABASE_URL'))}")
    
except Exception as e:
    logger.error(f"Error during app initialization: {str(e)}")
    # 创建一个最小的Flask应用作为fallback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error_home():
        return jsonify({'error': 'App initialization failed', 'details': str(e)}), 500
    
    @app.route('/api/<path:path>')
    def error_api(path):
        return jsonify({'error': 'App initialization failed', 'details': str(e)}), 500
else:
    # Vercel使用WSGI处理程序，需要一个名为app的应用实例
    # 这个文件作为Vercel的入口点
    
    @app.route('/')
    def home():
        return jsonify({'message': 'EasyCook API is running on Vercel'})