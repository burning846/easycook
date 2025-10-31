#!/usr/bin/env python3
"""
EasyCook应用健康检查脚本
用于监控Vercel部署的应用状态
"""

import requests
import json
import sys
import time
from datetime import datetime

def check_endpoint(url, timeout=10):
    """检查端点是否可访问"""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'status': 'success' if response.status_code == 200 else 'error',
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'error': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'status_code': None,
            'response_time': None,
            'error': str(e)
        }

def main():
    """主函数"""
    print("🏥 EasyCook应用健康检查")
    print(f"🕒 时间: {datetime.now().isoformat()}")
    print("-" * 50)
    
    # 从命令行参数获取URL，或使用默认值
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # 这里应该是你的实际Vercel部署URL
        base_url = "https://easycook.vercel.app"
    
    # 要检查的端点
    endpoints = [
        {'name': '首页', 'path': '/'},
        {'name': 'API健康检查', 'path': '/api/health'},
        {'name': '菜谱列表', 'path': '/api/recipes'},
        {'name': '食材列表', 'path': '/api/ingredients'},
    ]
    
    results = []
    all_healthy = True
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint['path']}"
        print(f"🔍 检查 {endpoint['name']}: {url}")
        
        result = check_endpoint(url)
        result['name'] = endpoint['name']
        result['url'] = url
        results.append(result)
        
        if result['status'] == 'success':
            print(f"  ✅ 正常 (状态码: {result['status_code']}, 响应时间: {result['response_time']:.2f}s)")
        else:
            print(f"  ❌ 异常 (状态码: {result['status_code']}, 错误: {result['error']})")
            all_healthy = False
    
    print("\n" + "=" * 50)
    print("📊 健康检查总结:")
    
    healthy_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    
    print(f"  正常端点: {healthy_count}/{total_count}")
    print(f"  总体状态: {'✅ 健康' if all_healthy else '❌ 异常'}")
    
    if '--json' in sys.argv:
        print("\n📋 JSON报告:")
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'overall_status': 'healthy' if all_healthy else 'unhealthy',
            'healthy_count': healthy_count,
            'total_count': total_count,
            'endpoints': results
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 返回适当的退出码
    sys.exit(0 if all_healthy else 1)

if __name__ == '__main__':
    main()