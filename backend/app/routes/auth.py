from flask import jsonify, request, redirect, url_for, current_app
import requests
import json
from app import db
from app.models.user import User
from app.routes import api_bp

# Google OAuth配置
# 实际应用中，这些应该从环境变量或配置文件中获取
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

@api_bp.route('/auth/google', methods=['GET'])
def google_login():
    """启动Google OAuth流程"""
    # 获取Google的授权端点
    try:
        discovery_doc = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = discovery_doc["authorization_endpoint"]
        
        # 构建授权URL
        redirect_uri = url_for('api.google_callback', _external=True)
        
        params = {
            "response_type": "code",
            "client_id": GOOGLE_CLIENT_ID,
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
        
        # 构建token请求
        redirect_uri = url_for('api.google_callback', _external=True)
        
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
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