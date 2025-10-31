#!/usr/bin/env python3
"""
Google OAuth重定向URI修复脚本
解决redirect_uri_mismatch错误
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def get_vercel_deployments():
    """获取Vercel部署列表"""
    try:
        result = subprocess.run(['vercel', 'ls', '--json'], 
                              capture_output=True, text=True, check=True)
        deployments = json.loads(result.stdout)
        return deployments
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取Vercel部署失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 解析部署数据失败: {e}")
        return None

def get_production_url():
    """获取生产环境URL"""
    deployments = get_vercel_deployments()
    if not deployments:
        return None
    
    # 查找最新的Ready状态的生产环境部署
    for deployment in deployments:
        if (deployment.get('state') == 'READY' and 
            deployment.get('target') == 'production'):
            return f"https://{deployment['url']}"
    
    return None

def print_oauth_config():
    """打印OAuth配置信息"""
    print("🔍 Google OAuth配置分析")
    print("=" * 50)
    
    # 获取当前环境变量
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '未设置')
    frontend_url = os.environ.get('FRONTEND_URL', '未设置')
    
    print(f"📋 当前配置:")
    print(f"  Google Client ID: {google_client_id[:20]}..." if google_client_id != '未设置' else f"  Google Client ID: {google_client_id}")
    print(f"  Frontend URL: {frontend_url}")
    
    # 获取生产环境URL
    prod_url = get_production_url()
    if prod_url:
        print(f"  生产环境URL: {prod_url}")
    else:
        print("  生产环境URL: 无法获取")
    
    print("\n🎯 需要在Google Cloud Console中配置的重定向URI:")
    print("=" * 50)
    
    # 生成所有可能的重定向URI
    uris = []
    
    # 本地开发环境
    uris.extend([
        "http://localhost:3000/login-success",
        "http://localhost:5000/api/auth/google/callback",
        "http://localhost:3000/api/auth/google/callback"
    ])
    
    # 生产环境
    if prod_url:
        uris.extend([
            f"{prod_url}/api/auth/google/callback",
            f"{prod_url}/login-success"
        ])
    
    # 通用Vercel域名模式
    uris.extend([
        "https://easycook-*.vercel.app/api/auth/google/callback",
        "https://easycook-*.vercel.app/login-success",
        "https://*.burning846s-projects.vercel.app/api/auth/google/callback",
        "https://*.burning846s-projects.vercel.app/login-success"
    ])
    
    for i, uri in enumerate(uris, 1):
        print(f"  {i:2d}. {uri}")
    
    print("\n⚠️  注意事项:")
    print("=" * 50)
    print("1. Google Cloud Console不支持通配符，需要添加具体的URL")
    print("2. 每次新部署都会生成新的URL，需要及时更新")
    print("3. 建议设置自定义域名以避免频繁更新")
    
    return prod_url

def create_env_update_commands(prod_url):
    """生成环境变量更新命令"""
    print("\n🛠️  环境变量更新命令:")
    print("=" * 50)
    
    if prod_url:
        print("# 更新Vercel环境变量")
        print(f'vercel env add FRONTEND_URL "{prod_url}" production')
        print(f'vercel env add FRONTEND_URL "{prod_url}" preview')
        print(f'vercel env add FRONTEND_URL "{prod_url}" development')
        
        print("\n# 或者使用Vercel Web界面:")
        print("1. 访问 https://vercel.com/dashboard")
        print("2. 选择easycook项目")
        print("3. 进入Settings > Environment Variables")
        print(f"4. 添加 FRONTEND_URL = {prod_url}")
    else:
        print("❌ 无法获取生产环境URL，请手动设置")

def main():
    """主函数"""
    print("🚀 Google OAuth重定向URI修复工具")
    print(f"🕒 时间: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 检查是否在正确的目录
    if not os.path.exists('vercel.json'):
        print("❌ 请在项目根目录下运行此脚本")
        sys.exit(1)
    
    # 加载环境变量
    if os.path.exists('.env.local'):
        from dotenv import load_dotenv
        load_dotenv('.env.local')
        print("✅ 已加载 .env.local 环境变量")
    
    # 分析配置
    prod_url = print_oauth_config()
    
    # 生成更新命令
    create_env_update_commands(prod_url)
    
    print("\n📝 下一步操作:")
    print("=" * 50)
    print("1. 复制上述重定向URI到Google Cloud Console")
    print("2. 更新Vercel环境变量")
    print("3. 重新部署应用: vercel --prod")
    print("4. 测试Google登录功能")

if __name__ == '__main__':
    main()