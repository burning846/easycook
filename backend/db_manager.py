#!/usr/bin/env python3
"""
EasyCook数据库管理工具
用于在Vercel环境中管理数据库的初始化、更新和维护
"""

import os
import sys
import argparse
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.recipe import Recipe, Step
from app.models.ingredient import Ingredient, RecipeIngredient
from app.models.user import User, UserIngredient, ShoppingList, ShoppingListItem, UserPreference
from app.models.favorite import FavoriteRecipe

class DatabaseManager:
    def __init__(self):
        self.app = create_app()
        
    def init_database(self):
        """初始化数据库"""
        with self.app.app_context():
            try:
                # 创建所有表
                db.create_all()
                print("✅ 数据库表创建成功")
                
                # 检查是否已有数据
                if Ingredient.query.count() > 0:
                    print("⚠️  数据库已有数据，跳过初始化")
                    return
                
                # 运行初始化脚本
                from init_db import init_db
                init_db()
                print("✅ 数据库初始化完成")
                
            except Exception as e:
                print(f"❌ 数据库初始化失败: {str(e)}")
                raise
    
    def check_status(self):
        """检查数据库状态"""
        with self.app.app_context():
            try:
                # 检查连接
                from sqlalchemy import text
                with db.engine.connect() as connection:
                    connection.execute(text('SELECT 1'))
                print("✅ 数据库连接正常")
                
                # 统计数据
                stats = {
                    '菜谱': Recipe.query.count(),
                    '食材': Ingredient.query.count(),
                    '用户': User.query.count(),
                    '收藏': FavoriteRecipe.query.count(),
                }
                
                print("\n📊 数据库统计:")
                for name, count in stats.items():
                    print(f"  {name}: {count}")
                
                # 检查最近更新
                latest_recipe = Recipe.query.order_by(Recipe.updated_at.desc()).first()
                if latest_recipe:
                    print(f"\n🕒 最近更新: {latest_recipe.updated_at}")
                
            except Exception as e:
                print(f"❌ 数据库检查失败: {str(e)}")
                raise
    
    def update_images(self):
        """更新菜谱图片URL"""
        with self.app.app_context():
            try:
                recipes = Recipe.query.all()
                updated_count = 0
                
                for recipe in recipes:
                    if recipe.image_url and 'example.com' in recipe.image_url:
                        # 更新为本地图片路径
                        recipe.image_url = f"/images/{recipe.name}.jpg"
                        updated_count += 1
                
                db.session.commit()
                print(f"✅ 更新了 {updated_count} 个菜谱的图片URL")
                
            except Exception as e:
                print(f"❌ 图片URL更新失败: {str(e)}")
                raise
    
    def reset_database(self):
        """重置数据库（危险操作）"""
        with self.app.app_context():
            try:
                # 确认操作
                confirm = input("⚠️  这将删除所有数据！请输入 'RESET' 确认: ")
                if confirm != 'RESET':
                    print("❌ 操作已取消")
                    return
                
                # 删除所有表
                db.drop_all()
                print("✅ 数据库表已删除")
                
                # 重新创建表
                db.create_all()
                print("✅ 数据库表已重新创建")
                
                # 重新初始化数据
                from init_db import init_db
                init_db()
                print("✅ 数据库已重置并初始化")
                
            except Exception as e:
                print(f"❌ 数据库重置失败: {str(e)}")
                raise
    
    def backup_data(self):
        """备份关键数据"""
        with self.app.app_context():
            try:
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'recipes': [],
                    'ingredients': [],
                    'users': []
                }
                
                # 备份菜谱
                for recipe in Recipe.query.all():
                    backup_data['recipes'].append({
                        'name': recipe.name,
                        'description': recipe.description,
                        'category': recipe.category,
                        'difficulty': recipe.difficulty,
                        'cooking_time': recipe.cooking_time,
                        'image_url': recipe.image_url
                    })
                
                # 备份食材
                for ingredient in Ingredient.query.all():
                    backup_data['ingredients'].append({
                        'name': ingredient.name,
                        'unit': ingredient.unit,
                        'category': ingredient.category
                    })
                
                # 备份用户（不包含敏感信息）
                for user in User.query.all():
                    backup_data['users'].append({
                        'username': user.username,
                        'email': user.email,
                        'created_at': user.created_at.isoformat() if user.created_at else None
                    })
                
                # 保存备份文件
                import json
                backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 数据备份完成: {backup_filename}")
                
            except Exception as e:
                print(f"❌ 数据备份失败: {str(e)}")
                raise
    
    def migrate_schema(self):
        """执行数据库架构迁移"""
        with self.app.app_context():
            try:
                # 这里可以添加具体的迁移逻辑
                # 例如：添加新字段、修改表结构等
                
                # 示例：为Recipe表添加新字段（如果不存在）
                from sqlalchemy import text
                
                # 检查字段是否存在
                with db.engine.connect() as connection:
                    result = connection.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='recipe' AND column_name='nutrition_info'
                    """))
                    
                    if not result.fetchone():
                        # 添加新字段
                        connection.execute(text("""
                            ALTER TABLE recipe 
                            ADD COLUMN nutrition_info TEXT
                        """))
                        connection.commit()
                        print("✅ 添加了 nutrition_info 字段")
                    else:
                        print("ℹ️  nutrition_info 字段已存在")
                
                print("✅ 数据库架构迁移完成")
                
            except Exception as e:
                print(f"❌ 数据库迁移失败: {str(e)}")
                raise

def main():
    parser = argparse.ArgumentParser(description='EasyCook数据库管理工具')
    parser.add_argument('action', choices=[
        'init', 'status', 'update-images', 'reset', 'backup', 'migrate'
    ], help='要执行的操作')
    
    args = parser.parse_args()
    
    manager = DatabaseManager()
    
    print(f"🚀 执行操作: {args.action}")
    print(f"🌍 环境: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🗄️  数据库: {os.environ.get('DATABASE_URL', '未配置')[:50]}...")
    print("-" * 50)
    
    try:
        if args.action == 'init':
            manager.init_database()
        elif args.action == 'status':
            manager.check_status()
        elif args.action == 'update-images':
            manager.update_images()
        elif args.action == 'reset':
            manager.reset_database()
        elif args.action == 'backup':
            manager.backup_data()
        elif args.action == 'migrate':
            manager.migrate_schema()
        
        print("\n✅ 操作完成!")
        
    except Exception as e:
        print(f"\n❌ 操作失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()