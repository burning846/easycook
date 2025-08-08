import os
import logging
from flask import Flask, jsonify

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app import create_app
    logger.info("Successfully imported create_app")
    
    app = create_app()
    logger.info("Successfully created Flask app")
    
except Exception as e:
    import traceback
    logger.error(f"Error during app initialization: {str(e)}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    
    # 创建一个简化的Flask应用，包含auth路由
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"
    app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'https://easycook-mu.vercel.app')
    
    # 导入auth路由
    try:
        from flask import Blueprint
        api_bp = Blueprint('api', __name__)
        
        # 手动添加Google登录路由
        from flask import jsonify, request, redirect, url_for, current_app
        import requests
        from urllib.parse import urlencode
        
        @api_bp.route('/auth/google', methods=['GET'])
        def google_login():
            """启动Google OAuth流程"""
            try:
                current_app.logger.info("开始Google OAuth登录流程")
                
                client_id = current_app.config.get('GOOGLE_CLIENT_ID')
                if not client_id or client_id == 'your-google-client-id':
                    current_app.logger.error("Google Client ID未配置")
                    return jsonify({"error": "Google OAuth未正确配置"}), 500
                
                discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
                discovery_response = requests.get(discovery_url)
                
                if discovery_response.status_code != 200:
                    return jsonify({"error": "无法获取Google配置"}), 500
                    
                discovery_doc = discovery_response.json()
                authorization_endpoint = discovery_doc["authorization_endpoint"]
                
                redirect_uri = url_for('api.google_callback', _external=True)
                
                params = {
                    "response_type": "code",
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "scope": "openid email profile",
                    "prompt": "select_account"
                }
                
                auth_url = f"{authorization_endpoint}?{urlencode(params)}"
                return redirect(auth_url)
                
            except Exception as e:
                current_app.logger.error(f"Google OAuth初始化失败: {str(e)}")
                return jsonify({"error": "Google登录初始化失败", "details": str(e)}), 500
        
        @api_bp.route('/auth/google/callback', methods=['GET'])
        def google_callback():
            """处理Google OAuth回调"""
            # 获取授权码
            code = request.args.get("code")
            if not code:
                return jsonify({"error": "未收到授权码"}), 400
            
            try:
                # 获取Google的token端点
                discovery_doc = requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()
                token_endpoint = discovery_doc["token_endpoint"]
                
                # 构建token请求
                redirect_uri = url_for('api.google_callback', _external=True)
                
                token_data = {
                    "code": code,
                    "client_id": app.config['GOOGLE_CLIENT_ID'],
                    "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
                
                # 发送token请求
                token_response = requests.post(token_endpoint, data=token_data)
                token_json = token_response.json()
                
                if 'access_token' not in token_json:
                    logger.error(f"Token response error: {token_json}")
                    return jsonify({"error": "获取访问令牌失败"}), 400
                
                # 获取用户信息
                userinfo_endpoint = discovery_doc["userinfo_endpoint"]
                userinfo_response = requests.get(
                    userinfo_endpoint,
                    headers={"Authorization": f"Bearer {token_json['access_token']}"}
                )
                userinfo = userinfo_response.json()
                
                # 简化处理：直接重定向到前端并传递用户信息
                frontend_url = app.config.get('FRONTEND_URL', 'https://easycook-mu.vercel.app')
                user_data = {
                    'id': userinfo.get('sub'),
                    'name': userinfo.get('name'),
                    'email': userinfo.get('email'),
                    'picture': userinfo.get('picture')
                }
                
                # 重定向到前端登录成功页面
                import urllib.parse
                user_params = urllib.parse.urlencode(user_data)
                return redirect(f"{frontend_url}/login-success?{user_params}")
                
            except Exception as e:
                logger.error(f"Google OAuth回调处理失败: {str(e)}")
                import traceback
                logger.error(f"完整错误堆栈: {traceback.format_exc()}")
                return jsonify({"error": "Google登录处理失败", "details": str(e)}), 500
        
        app.register_blueprint(api_bp, url_prefix='/api')
        logger.info("Successfully registered simplified auth routes")
        
    except Exception as auth_error:
        logger.error(f"Error setting up auth routes: {str(auth_error)}")
        
        @app.route('/')
        def error_home():
            return jsonify({'error': 'App initialization failed', 'details': str(e)}), 500
        
        @app.route('/api/<path:path>')
        def error_api(path):
            return jsonify({'error': 'App initialization failed', 'details': str(e)}), 500

# 添加基本的测试端点
@app.route('/api/test')
def test():
    return jsonify({'message': 'Test endpoint working'})

@app.route('/api/env-test')
def env_test():
    return jsonify({
        'google_client_id_exists': bool(os.environ.get('GOOGLE_CLIENT_ID')),
        'database_url_exists': bool(os.environ.get('DATABASE_URL')),
        'secret_key_exists': bool(os.environ.get('SECRET_KEY')),
        'google_client_id_value': os.environ.get('GOOGLE_CLIENT_ID', 'NOT_SET')[:10] + '...' if os.environ.get('GOOGLE_CLIENT_ID') else 'NOT_SET'
    })

@app.route('/api/google-config-test')
def google_config_test():
    try:
        import requests
        discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
        response = requests.get(discovery_url)
        return jsonify({
            'requests_available': True,
            'discovery_status': response.status_code,
            'google_client_id': os.environ.get('GOOGLE_CLIENT_ID', 'NOT_SET')[:10] + '...' if os.environ.get('GOOGLE_CLIENT_ID') else 'NOT_SET'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'requests_available': False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)