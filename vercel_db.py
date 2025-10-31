#!/usr/bin/env python3
"""
Vercel数据库管理脚本
专门用于在Vercel环境中管理数据库
"""

import os
import sys
import json
from datetime import datetime

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def load_env_from_vercel():
    """从Vercel环境变量加载配置"""
    try:
        # 尝试从.env.local文件加载（如果存在）
        env_file = os.path.join(os.path.dirname(__file__), '.env.local')
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ 从.env.local加载环境变量")
            
            # 修复数据库URL协议问题
            database_url = os.environ.get('DATABASE_URL', '')
            if database_url.startswith('postgres://'):
                os.environ['DATABASE_URL'] = database_url.replace('postgres://', 'postgresql://', 1)
                print("🔧 修复数据库URL协议")
        else:
            print("ℹ️  使用Vercel环境变量")
    except Exception as e:
        print(f"⚠️  环境变量加载警告: {e}")

def init_database():
    """初始化数据库"""
    try:
        load_env_from_vercel()
        
        from app import create_app, db
        from backend.init_db import init_db
        
        app = create_app()
        
        with app.app_context():
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 检查是否已有数据
            from app.models.ingredient import Ingredient
            if Ingredient.query.count() > 0:
                print("⚠️  数据库已有数据，跳过初始化")
                return {"status": "skipped", "message": "数据库已有数据"}
            
            # 运行初始化
            init_db()
            print("✅ 数据库初始化完成")
            
            return {"status": "success", "message": "数据库初始化成功"}
            
    except Exception as e:
        error_msg = f"数据库初始化失败: {str(e)}"
        print(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}

def check_database():
    """检查数据库状态"""
    try:
        load_env_from_vercel()
        
        from app import create_app, db
        from app.models.recipe import Recipe
        from app.models.ingredient import Ingredient
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # 检查连接
            from sqlalchemy import text
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            
            # 统计数据
            stats = {
                'recipes': Recipe.query.count(),
                'ingredients': Ingredient.query.count(),
                'users': User.query.count(),
            }
            
            print("✅ 数据库连接正常")
            print(f"📊 统计: {stats}")
            
            return {"status": "success", "stats": stats}
            
    except Exception as e:
        error_msg = f"数据库检查失败: {str(e)}"
        print(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}

def update_recipe_images():
    """更新菜谱图片URL"""
    try:
        load_env_from_vercel()
        
        from app import create_app, db
        from app.models.recipe import Recipe
        
        app = create_app()
        
        with app.app_context():
            recipes = Recipe.query.all()
            updated_count = 0
            
            for recipe in recipes:
                if recipe.image_url and ('example.com' in recipe.image_url or 'placeholder' in recipe.image_url):
                    # 更新为实际图片路径
                    recipe.image_url = f"/images/{recipe.name}.jpg"
                    updated_count += 1
            
            db.session.commit()
            
            print(f"✅ 更新了 {updated_count} 个菜谱的图片URL")
            return {"status": "success", "updated": updated_count}
            
    except Exception as e:
        error_msg = f"图片URL更新失败: {str(e)}"
        print(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vercel数据库管理')
    parser.add_argument('action', choices=['init', 'check', 'update-images'], 
                       help='要执行的操作')
    parser.add_argument('--json', action='store_true', 
                       help='以JSON格式输出结果')
    
    args = parser.parse_args()
    
    print(f"🚀 Vercel数据库管理 - {args.action}")
    print(f"🕒 时间: {datetime.now().isoformat()}")
    print("-" * 50)
    
    result = None
    
    if args.action == 'init':
        result = init_database()
    elif args.action == 'check':
        result = check_database()
    elif args.action == 'update-images':
        result = update_recipe_images()
    
    if args.json and result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n🏁 操作完成")

if __name__ == "__main__":
    main()