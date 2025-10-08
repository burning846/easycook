#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片显示测试脚本
验证所有菜谱图片是否能正常访问
"""

import os
import sys
import requests
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.recipe import Recipe

class ImageDisplayTester:
    """图片显示测试器"""
    
    def __init__(self):
        self.app = create_app()
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://127.0.0.1:5000"
    
    def test_image_accessibility(self) -> Dict[str, List[str]]:
        """测试图片可访问性"""
        results = {
            "success": [],
            "failed": [],
            "missing_url": []
        }
        
        with self.app.app_context():
            recipes = Recipe.query.all()
            
            print(f"🔍 开始测试 {len(recipes)} 个菜谱的图片...")
            
            for recipe in recipes:
                if not recipe.image_url:
                    results["missing_url"].append(recipe.name)
                    print(f"❌ {recipe.name}: 缺少图片URL")
                    continue
                
                # 构建完整的图片URL
                image_url = f"{self.frontend_url}{recipe.image_url}"
                
                try:
                    response = requests.head(image_url, timeout=5)
                    if response.status_code == 200:
                        results["success"].append(recipe.name)
                        print(f"✅ {recipe.name}: 图片可访问 ({response.headers.get('content-type', 'unknown')})")
                    else:
                        results["failed"].append(recipe.name)
                        print(f"❌ {recipe.name}: HTTP {response.status_code}")
                except Exception as e:
                    results["failed"].append(recipe.name)
                    print(f"❌ {recipe.name}: 访问失败 - {str(e)}")
        
        return results
    
    def test_api_response(self):
        """测试API返回的图片URL"""
        try:
            response = requests.get(f"{self.backend_url}/api/recipes?per_page=5")
            if response.status_code == 200:
                data = response.json()
                recipes = data.get('recipes', [])
                
                print(f"\n📡 API测试结果:")
                print(f"返回 {len(recipes)} 个菜谱")
                
                for recipe in recipes:
                    name = recipe.get('name', 'Unknown')
                    image_url = recipe.get('image_url', 'None')
                    print(f"  - {name}: {image_url}")
                
                return True
            else:
                print(f"❌ API请求失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API测试失败: {str(e)}")
            return False
    
    def generate_test_report(self, results: Dict[str, List[str]]):
        """生成测试报告"""
        total = len(results["success"]) + len(results["failed"]) + len(results["missing_url"])
        
        print(f"\n📊 图片显示测试报告")
        print(f"=" * 50)
        print(f"总计菜谱: {total}")
        print(f"✅ 成功显示: {len(results['success'])}")
        print(f"❌ 显示失败: {len(results['failed'])}")
        print(f"⚠️  缺少URL: {len(results['missing_url'])}")
        print(f"成功率: {len(results['success'])/total*100:.1f}%" if total > 0 else "成功率: 0%")
        
        if results["failed"]:
            print(f"\n❌ 显示失败的菜谱:")
            for name in results["failed"]:
                print(f"  - {name}")
        
        if results["missing_url"]:
            print(f"\n⚠️  缺少图片URL的菜谱:")
            for name in results["missing_url"]:
                print(f"  - {name}")

def main():
    """主函数"""
    tester = ImageDisplayTester()
    
    try:
        # 测试图片可访问性
        results = tester.test_image_accessibility()
        
        # 测试API响应
        tester.test_api_response()
        
        # 生成测试报告
        tester.generate_test_report(results)
        
        # 判断测试结果
        if len(results["failed"]) == 0 and len(results["missing_url"]) == 0:
            print(f"\n🎉 所有图片测试通过！")
            return 0
        else:
            print(f"\n⚠️  存在图片显示问题，请检查上述失败项目")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())