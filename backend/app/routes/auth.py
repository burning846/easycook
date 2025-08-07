from flask import jsonify, request, redirect, url_for, current_app
import requests
import json
from app import db
from app.models.user import User
from app.routes import api_bp

# Google OAuth配置
# 从Flask配置中获取
def get_google_config():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    discovery_url = current_app.config.get('GOOGLE_DISCOVERY_URL')
    
    # 调试日志
    current_app.logger.info(f"Google Client ID configured: {bool(client_id and client_id != 'your-google-client-id')}")
    current_app.logger.info(f"Google Client Secret configured: {bool(client_secret and client_secret != 'your-google-client-secret')}")
    
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'discovery_url': discovery_url
    }

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

@api_bp.route('/auth/google', methods=['GET'])
def google_login():
    """启动Google OAuth流程"""
    # 获取Google的授权端点
    try:
        discovery_doc = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = discovery_doc["authorization_endpoint"]
        
        # 获取Google配置
        google_config = get_google_config()
        
        if not google_config['client_id'] or google_config['client_id'] == 'your-google-client-id':
            current_app.logger.error("Google Client ID未配置")
            return jsonify({"error": "Google OAuth未正确配置"}), 500
        
        # 构建授权URL
        redirect_uri = url_for('api.google_callback', _external=True)
        
        params = {
            "response_type": "code",
            "client_id": google_config['client_id'],
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "prompt": "select_account"
        }
        
        # 构建完整的授权URL
        auth_url = f"{authorization_endpoint}?" + "&".join([f"{key}={value}" for key, value in params.items()])
        
        # 重定向到Google授权页面
        return redirect(auth_url)
    except Exception as e:
        current_app.logger.error(f"Google OAuth初始化失败: {str(e)}")
        return jsonify({"error": "Google登录初始化失败"}), 500

@api_bp.route('/auth/google/callback', methods=['GET'])
def google_callback():
    """处理Google OAuth回调"""
    # 获取授权码
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "未收到授权码"}), 400
    
    try:
        # 获取Google的token端点
        discovery_doc = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = discovery_doc["token_endpoint"]
        
        # 获取Google配置
        google_config = get_google_config()
        
        if not google_config['client_id'] or not google_config['client_secret']:
            current_app.logger.error("Google OAuth配置不完整")
            return jsonify({"error": "Google OAuth配置错误"}), 500
        
        # 构建token请求
        redirect_uri = url_for('api.google_callback', _external=True)
        
        token_data = {
            "code": code,
            "client_id": google_config['client_id'],
            "client_secret": google_config['client_secret'],
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        # 发送token请求
        token_response = requests.post(token_endpoint, data=token_data)
        token_json = token_response.json()
        
        # 获取用户信息
        userinfo_endpoint = discovery_doc["userinfo_endpoint"]
        userinfo_response = requests.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {token_json['access_token']}"}
        )
        userinfo = userinfo_response.json()
        
        # 检查用户是否已存在
        user = User.query.filter_by(google_id=userinfo["sub"]).first()
        
        if not user:
            # 检查是否有同名或同邮箱的用户
            existing_user = User.query.filter_by(email=userinfo["email"]).first()
            
            if existing_user:
                # 更新现有用户的Google ID
                existing_user.google_id = userinfo["sub"]
                db.session.commit()
                user = existing_user
            else:
                # 创建新用户
                user = User(
                    username=userinfo.get("name", "Google用户"),
                    email=userinfo["email"],
                    google_id=userinfo["sub"]
                )
                db.session.add(user)
                db.session.commit()
        
        # 这里应该生成JWT或会话令牌
        # 简化起见，我们直接返回用户信息
        # 实际应用中，应该返回JWT令牌并重定向到前端
        
        # 重定向到前端，带上用户ID
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/login-success?user_id={user.id}")
    
    except Exception as e:
        current_app.logger.error(f"Google OAuth回调处理失败: {str(e)}")
        return jsonify({"error": "Google登录处理失败"}), 500

@api_bp.route('/auth/user/<int:user_id>', methods=['GET'])
def get_auth_user(user_id):
    """获取认证用户信息"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())