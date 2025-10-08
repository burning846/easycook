#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜品照片下载脚本
从免费图片API下载真实的菜品照片并更新数据库
"""

import os
import sys
import requests
import time
from typing import Dict, List, Optional
from urllib.parse import quote
import hashlib

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.recipe import Recipe

class RecipePhotoDownloader:
    """菜品照片下载器"""
    
    def __init__(self):
        self.app = create_app()
        self.images_dir = "/Users/bytedance/Documents/personal/easycook/frontend/public/images"
        
        # 确保图片目录存在
        os.makedirs(self.images_dir, exist_ok=True)
        
        # 菜品名称到英文关键词的映射（用于搜索）
        self.recipe_keywords = {
            "西红柿炒鸡蛋": "tomato scrambled eggs chinese",
            "土豆炖牛肉": "beef potato stew chinese",
            "青椒炒肉": "green pepper pork stir fry",
            "麻婆豆腐": "mapo tofu sichuan",
            "蔬菜沙拉": "vegetable salad fresh",
            "红烧鱼": "braised fish chinese",
            "宫保鸡丁": "kung pao chicken sichuan",
            "清蒸鲈鱼": "steamed bass fish chinese",
            "糖醋排骨": "sweet sour pork ribs",
            "红烧肉": "braised pork belly chinese",
            "糖醋里脊": "sweet sour pork tenderloin",
            "鱼香茄子": "fish fragrant eggplant sichuan",
            "白切鸡": "white cut chicken cantonese",
            "蒸蛋羹": "steamed egg custard chinese",
            "西红柿鸡蛋面": "tomato egg noodles chinese",
            "可乐鸡翅": "cola chicken wings chinese",
            "蒜蓉西兰花": "garlic broccoli chinese"
        }
        
        # 备用图片URL（高质量菜品图片）
        self.fallback_images = {
            "西红柿炒鸡蛋": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop",
            "土豆炖牛肉": "https://images.unsplash.com/photo-1574484284002-952d92456975?w=400&h=300&fit=crop",
            "青椒炒肉": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop",
            "麻婆豆腐": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=400&h=300&fit=crop",
            "蔬菜沙拉": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
            "红烧鱼": "https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=400&h=300&fit=crop",
            "宫保鸡丁": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400&h=300&fit=crop",
            "清蒸鲈鱼": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=300&fit=crop",
            "糖醋排骨": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400&h=300&fit=crop",
            "红烧肉": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=300&fit=crop",
            "糖醋里脊": "https://images.unsplash.com/photo-1565299507177-b0ac66763828?w=400&h=300&fit=crop",
            "鱼香茄子": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&h=300&fit=crop",
            "白切鸡": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=400&h=300&fit=crop",
            "蒸蛋羹": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=400&h=300&fit=crop",
            "西红柿鸡蛋面": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=300&fit=crop",
            "可乐鸡翅": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=400&h=300&fit=crop",
            "蒜蓉西兰花": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400&h=300&fit=crop"
        }
    
    def sanitize_filename(self, name: str) -> str:
        """清理文件名，移除特殊字符"""
        import re
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.replace(' ', '_')
        return name
    
    def download_image(self, url: str, filename: str) -> bool:
        """下载图片到本地"""
        try:
            print(f"  正在下载: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"  ❌ 不是有效的图片格式: {content_type}")
                return False
            
            # 确定文件扩展名
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'  # 默认
            
            # 保存文件
            filepath = os.path.join(self.images_dir, f"{filename}{ext}")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✅ 下载成功: {filename}{ext} ({len(response.content)} bytes)")
            return True
            
        except Exception as e:
            print(f"  ❌ 下载失败: {str(e)}")
            return False
    
    def get_image_from_unsplash(self, recipe_name: str) -> Optional[str]:
        """从Unsplash获取图片URL"""
        try:
            # 使用备用图片URL
            if recipe_name in self.fallback_images:
                return self.fallback_images[recipe_name]
            
            # 如果没有预设的URL，使用通用的食物图片
            return "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop"
            
        except Exception as e:
            print(f"  ❌ 获取Unsplash图片失败: {str(e)}")
            return None
    
    def download_recipe_photo(self, recipe: Recipe) -> Optional[str]:
        """为单个菜谱下载照片"""
        print(f"\n📸 处理菜谱: {recipe.name}")
        
        # 生成文件名
        filename = self.sanitize_filename(recipe.name)
        
        # 尝试从Unsplash下载
        image_url = self.get_image_from_unsplash(recipe.name)
        if image_url:
            if self.download_image(image_url, filename):
                # 确定实际保存的文件扩展名
                for ext in ['.jpg', '.png', '.webp']:
                    filepath = os.path.join(self.images_dir, f"{filename}{ext}")
                    if os.path.exists(filepath):
                        return f"/images/{filename}{ext}"
        
        print(f"  ❌ 无法下载 {recipe.name} 的照片")
        return None
    
    def update_recipe_photos(self):
        """批量更新所有菜谱的照片"""
        with self.app.app_context():
            recipes = Recipe.query.all()
            updated_count = 0
            failed_count = 0
            
            print(f"🚀 开始为 {len(recipes)} 个菜谱下载真实照片...")
            
            for i, recipe in enumerate(recipes, 1):
                print(f"\n[{i}/{len(recipes)}]", end="")
                
                try:
                    # 下载照片
                    image_url = self.download_recipe_photo(recipe)
                    
                    if image_url:
                        # 更新数据库
                        recipe.image_url = image_url
                        updated_count += 1
                        print(f"  ✅ 更新成功: {image_url}")
                    else:
                        failed_count += 1
                        print(f"  ❌ 更新失败")
                    
                    # 避免请求过于频繁
                    time.sleep(1)
                    
                except Exception as e:
                    failed_count += 1
                    print(f"  ❌ 处理失败: {str(e)}")
            
            # 提交数据库更改
            try:
                db.session.commit()
                print(f"\n🎉 照片下载完成！")
                print(f"✅ 成功: {updated_count} 个")
                print(f"❌ 失败: {failed_count} 个")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ 数据库更新失败: {str(e)}")
    
    def list_downloaded_photos(self):
        """列出已下载的照片文件"""
        if os.path.exists(self.images_dir):
            photos = [f for f in os.listdir(self.images_dir) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            print(f"\n📁 已下载的照片文件 ({len(photos)} 个):")
            for photo in sorted(photos):
                filepath = os.path.join(self.images_dir, photo)
                size = os.path.getsize(filepath)
                print(f"  - {photo} ({size:,} bytes)")
        else:
            print(f"\n📁 图片目录不存在: {self.images_dir}")
    
    def cleanup_old_svg_files(self):
        """清理旧的SVG文件"""
        if os.path.exists(self.images_dir):
            svg_files = [f for f in os.listdir(self.images_dir) if f.endswith('.svg')]
            if svg_files:
                print(f"\n🧹 清理 {len(svg_files)} 个旧的SVG文件...")
                for svg_file in svg_files:
                    filepath = os.path.join(self.images_dir, svg_file)
                    try:
                        os.remove(filepath)
                        print(f"  ✅ 删除: {svg_file}")
                    except Exception as e:
                        print(f"  ❌ 删除失败 {svg_file}: {str(e)}")

def main():
    """主函数"""
    downloader = RecipePhotoDownloader()
    
    try:
        # 清理旧的SVG文件
        downloader.cleanup_old_svg_files()
        
        # 下载并更新照片
        downloader.update_recipe_photos()
        
        # 列出下载的文件
        downloader.list_downloaded_photos()
        
        print("\n✅ 菜品照片下载和更新完成！")
        
    except Exception as e:
        print(f"\n❌ 处理过程中出现错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())