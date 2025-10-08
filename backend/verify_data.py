#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本
检查数据库中的菜谱数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.recipe import Recipe, Step
from app.models.ingredient import Ingredient, RecipeIngredient

def verify_data():
    """验证数据库中的数据"""
    app = create_app()
    
    with app.app_context():
        # 统计菜谱数量
        recipe_count = Recipe.query.count()
        print(f"📊 菜谱总数: {recipe_count}")
        
        # 统计食材数量
        ingredient_count = Ingredient.query.count()
        print(f"🥬 食材总数: {ingredient_count}")
        
        # 统计步骤数量
        step_count = Step.query.count()
        print(f"📝 步骤总数: {step_count}")
        
        # 统计菜谱-食材关联数量
        recipe_ingredient_count = RecipeIngredient.query.count()
        print(f"🔗 菜谱-食材关联总数: {recipe_ingredient_count}")
        
        print("\n" + "="*50)
        print("📋 菜谱列表:")
        
        # 显示所有菜谱的基本信息
        recipes = Recipe.query.all()
        for recipe in recipes:
            print(f"\n🍽️  {recipe.name}")
            print(f"   分类: {recipe.category}")
            print(f"   难度: {recipe.difficulty}")
            print(f"   时间: {recipe.cooking_time}分钟")
            print(f"   描述: {recipe.description}")
            
            # 显示食材
            ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
            print(f"   食材({len(ingredients)}个):")
            for ri in ingredients:
                ingredient = Ingredient.query.get(ri.ingredient_id)
                print(f"     - {ingredient.name}: {ri.amount}{ingredient.unit}")
            
            # 显示步骤
            steps = Step.query.filter_by(recipe_id=recipe.id).order_by(Step.step_number).all()
            print(f"   步骤({len(steps)}个):")
            for step in steps:
                print(f"     {step.step_number}. {step.description}")
        
        print("\n" + "="*50)
        print("✅ 数据验证完成！")

if __name__ == "__main__":
    verify_data()