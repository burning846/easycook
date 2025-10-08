#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜谱图片生成脚本
为每个菜谱生成SVG图片并更新数据库中的图片URL
"""

import os
import sys
import re
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.recipe import Recipe

class RecipeImageGenerator:
    """菜谱图片生成器"""
    
    def __init__(self):
        self.app = create_app()
        self.images_dir = "/Users/bytedance/Documents/personal/easycook/frontend/public/images"
        
        # 菜谱类别对应的颜色和图标
        self.category_styles = {
            "川菜": {"bg": "#FF6B6B", "icon": "🌶️", "accent": "#FF5252"},
            "粤菜": {"bg": "#4ECDC4", "icon": "🦐", "accent": "#26A69A"},
            "家常菜": {"bg": "#45B7D1", "icon": "🏠", "accent": "#2196F3"},
            "素菜": {"bg": "#96CEB4", "icon": "🥬", "accent": "#4CAF50"},
            "面食": {"bg": "#FFEAA7", "icon": "🍜", "accent": "#FFC107"},
            "炖菜": {"bg": "#DDA0DD", "icon": "🍲", "accent": "#9C27B0"},
            "其他": {"bg": "#95A5A6", "icon": "🍽️", "accent": "#607D8B"}
        }
        
        # 难度对应的颜色
        self.difficulty_colors = {
            "简单": "#4CAF50",
            "中等": "#FF9800", 
            "困难": "#F44336"
        }
    
    def sanitize_filename(self, name: str) -> str:
        """清理文件名，移除特殊字符"""
        # 移除或替换特殊字符
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.replace(' ', '_')
        return name
    
    def generate_svg_image(self, recipe: Recipe) -> str:
        """为菜谱生成SVG图片"""
        category = recipe.category or "其他"
        style = self.category_styles.get(category, self.category_styles["其他"])
        difficulty_color = self.difficulty_colors.get(recipe.difficulty, "#95A5A6")
        
        # 创建SVG内容
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{style['bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{style['accent']};stop-opacity:0.8" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="rgba(0,0,0,0.3)"/>
    </filter>
  </defs>
  
  <!-- 背景 -->
  <rect width="300" height="200" fill="url(#bgGradient)" rx="12"/>
  
  <!-- 装饰性图案 -->
  <circle cx="250" cy="50" r="30" fill="rgba(255,255,255,0.1)"/>
  <circle cx="50" cy="150" r="20" fill="rgba(255,255,255,0.1)"/>
  
  <!-- 类别图标 -->
  <text x="30" y="50" font-size="32" fill="rgba(255,255,255,0.9)">{style['icon']}</text>
  
  <!-- 菜谱名称 -->
  <text x="150" y="80" text-anchor="middle" font-family="Arial, sans-serif" 
        font-size="24" font-weight="bold" fill="white" filter="url(#shadow)">
    {recipe.name}
  </text>
  
  <!-- 类别标签 -->
  <rect x="20" y="110" width="60" height="25" fill="rgba(255,255,255,0.2)" rx="12"/>
  <text x="50" y="127" text-anchor="middle" font-family="Arial, sans-serif" 
        font-size="12" fill="white">{category}</text>
  
  <!-- 难度标签 -->
  <rect x="90" y="110" width="60" height="25" fill="{difficulty_color}" rx="12"/>
  <text x="120" y="127" text-anchor="middle" font-family="Arial, sans-serif" 
        font-size="12" fill="white">{recipe.difficulty}</text>
  
  <!-- 时间标签 -->
  <rect x="160" y="110" width="80" height="25" fill="rgba(255,255,255,0.2)" rx="12"/>
  <text x="200" y="127" text-anchor="middle" font-family="Arial, sans-serif" 
        font-size="12" fill="white">{recipe.cooking_time}分钟</text>
  
  <!-- 装饰线条 -->
  <line x1="30" y1="150" x2="270" y2="150" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
  
  <!-- 描述文字 -->
  <text x="150" y="175" text-anchor="middle" font-family="Arial, sans-serif" 
        font-size="14" fill="rgba(255,255,255,0.8)">
    {recipe.description[:20] + '...' if len(recipe.description) > 20 else recipe.description}
  </text>
</svg>'''
        
        return svg_content
    
    def save_recipe_image(self, recipe: Recipe) -> str:
        """保存菜谱图片并返回URL"""
        # 生成文件名
        filename = f"{self.sanitize_filename(recipe.name)}.svg"
        filepath = os.path.join(self.images_dir, filename)
        
        # 生成SVG内容
        svg_content = self.generate_svg_image(recipe)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        # 返回相对URL
        return f"/images/{filename}"
    
    def update_recipe_images(self):
        """更新所有菜谱的图片"""
        with self.app.app_context():
            recipes = Recipe.query.all()
            updated_count = 0
            
            print(f"开始为 {len(recipes)} 个菜谱生成图片...")
            
            for recipe in recipes:
                try:
                    # 生成并保存图片
                    image_url = self.save_recipe_image(recipe)
                    
                    # 更新数据库
                    recipe.image_url = image_url
                    updated_count += 1
                    
                    print(f"✅ {recipe.name}: {image_url}")
                    
                except Exception as e:
                    print(f"❌ 生成图片失败 {recipe.name}: {str(e)}")
            
            # 提交数据库更改
            try:
                db.session.commit()
                print(f"\n🎉 成功更新 {updated_count} 个菜谱的图片！")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ 数据库更新失败: {str(e)}")
    
    def list_generated_images(self):
        """列出生成的图片文件"""
        if os.path.exists(self.images_dir):
            images = [f for f in os.listdir(self.images_dir) if f.endswith('.svg')]
            print(f"\n📁 生成的图片文件 ({len(images)} 个):")
            for img in images:
                print(f"  - {img}")
        else:
            print(f"\n📁 图片目录不存在: {self.images_dir}")

def main():
    """主函数"""
    generator = RecipeImageGenerator()
    
    try:
        # 确保图片目录存在
        os.makedirs(generator.images_dir, exist_ok=True)
        
        # 生成并更新图片
        generator.update_recipe_images()
        
        # 列出生成的文件
        generator.list_generated_images()
        
        print("\n✅ 图片生成和更新完成！")
        
    except Exception as e:
        print(f"\n❌ 处理过程中出现错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())