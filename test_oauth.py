#!/usr/bin/env python3
"""
Google OAuth测试脚本
测试重定向URI修复是否成功
"""

import requests
import sys
from urllib.parse import urljoin, urlparse, parse_qs
import re

def test_oauth_redirect(base_url):
    """测试OAuth重定向URI"""
    print(f"🔍 测试Google OAuth重定向URI")
    print(f"🌐 基础URL: {base_url}")
    print("=" * 60)
    
    # 测试Google登录端点
    login_url = urljoin(base_url, '/api/auth/google')
    
    try:
        print(f"📡 请求Google登录端点: {login_url}")
        response = requests.get(login_url, allow_redirects=False, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            # 获取重定向URL
            redirect_url = response.headers.get('Location', '')
            print(f"🔄 重定向URL: {redirect_url}")
            
            if 'accounts.google.com' in redirect_url:
                print("✅ 成功重定向到Google OAuth")
                
                # 解析重定向URI参数
                parsed_url = urlparse(redirect_url)
                params = parse_qs(parsed_url.query)
                
                redirect_uri = params.get('redirect_uri', [''])[0]
                client_id = params.get('client_id', [''])[0]
                
                print(f"🎯 重定向URI: {redirect_uri}")
                print(f"🔑 Client ID: {client_id[:20]}..." if client_id else "未找到")
                
                # 验证重定向URI格式
                if redirect_uri:
                    expected_callback = urljoin(base_url, '/api/auth/google/callback')
                    if redirect_uri == expected_callback:
                        print("✅ 重定向URI格式正确")
                        return True, redirect_uri
                    else:
                        print(f"❌ 重定向URI不匹配")
                        print(f"   期望: {expected_callback}")
                        print(f"   实际: {redirect_uri}")
                        return False, redirect_uri
                else:
                    print("❌ 未找到重定向URI参数")
                    return False, None
            else:
                print("❌ 未重定向到Google OAuth")
                return False, None
        else:
            print(f"❌ 意外的响应状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text[:200]}...")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False, None

def test_callback_endpoint(base_url):
    """测试回调端点是否存在"""
    callback_url = urljoin(base_url, '/api/auth/google/callback')
    
    try:
        print(f"\n📡 测试回调端点: {callback_url}")
        response = requests.get(callback_url, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ 回调端点存在 (400错误是正常的，因为缺少授权码)")
            return True
        elif response.status_code == 404:
            print("❌ 回调端点不存在")
            return False
        else:
            print(f"⚠️  意外的响应状态码: {response.status_code}")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def generate_google_console_config(redirect_uri):
    """生成Google Console配置建议"""
    if not redirect_uri:
        return
        
    print(f"\n🛠️  Google Cloud Console配置建议:")
    print("=" * 60)
    print("请在Google Cloud Console中添加以下重定向URI:")
    print(f"✅ {redirect_uri}")
    
    # 生成其他可能需要的URI
    base_url = redirect_uri.replace('/api/auth/google/callback', '')
    additional_uris = [
        f"{base_url}/login-success",
        "http://localhost:3000/api/auth/google/callback",
        "http://localhost:3000/login-success",
        "http://localhost:5000/api/auth/google/callback"
    ]
    
    print("\n其他建议添加的URI:")
    for uri in additional_uris:
        print(f"📌 {uri}")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python test_oauth.py <base_url>")
        print("示例: python test_oauth.py https://easycook-xxx.vercel.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🚀 Google OAuth测试工具")
    print(f"🕒 时间: 2025-10-08")
    print("=" * 60)
    
    # 测试OAuth重定向
    success, redirect_uri = test_oauth_redirect(base_url)
    
    # 测试回调端点
    callback_exists = test_callback_endpoint(base_url)
    
    # 生成配置建议
    if redirect_uri:
        generate_google_console_config(redirect_uri)
    
    # 总结
    print(f"\n📊 测试总结:")
    print("=" * 60)
    print(f"OAuth重定向: {'✅ 正常' if success else '❌ 异常'}")
    print(f"回调端点: {'✅ 存在' if callback_exists else '❌ 不存在'}")
    
    if success and callback_exists:
        print("\n🎉 OAuth配置看起来正常！")
        print("如果仍有问题，请检查Google Cloud Console中的重定向URI配置。")
    else:
        print("\n⚠️  发现问题，请检查配置。")
    
    return success and callback_exists

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)