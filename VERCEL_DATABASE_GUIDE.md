# Vercel数据库初始化和更新指南

本指南详细说明如何在Vercel部署环境中初始化和更新EasyCook应用的数据库。

## 📋 前提条件

1. ✅ 已在Vercel上部署EasyCook应用
2. ✅ 已配置Neon PostgreSQL数据库
3. ✅ 已设置必要的环境变量
4. ✅ 已安装Vercel CLI

## 🚀 首次数据库初始化

### 方法一：使用新的数据库管理工具（推荐）

1. **安装Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录Vercel**
   ```bash
   vercel login
   ```

3. **拉取环境变量**
   ```bash
   cd /path/to/easycook
   vercel env pull .env.local
   ```

4. **使用数据库管理工具**
   ```bash
   # 初始化数据库
   python vercel_db.py init
   
   # 检查数据库状态
   python vercel_db.py check
   
   # 更新菜谱图片
   python vercel_db.py update-images
   ```

### 方法二：使用传统方式

1. **拉取环境变量**
   ```bash
   cd /path/to/easycook
   vercel env pull .env.local
   ```

2. **运行数据库初始化脚本**
   ```bash
   cd backend
   python init_db.py
   ```

### 方法二：通过Vercel Functions

1. **创建数据库初始化API端点**
   
   在 `backend/vercel_app.py` 中添加：
   ```python
   @app.route('/api/init-db', methods=['POST'])
   def init_database():
       """初始化数据库（仅限管理员）"""
       try:
           # 添加安全验证
           auth_token = request.headers.get('Authorization')
           if auth_token != f"Bearer {os.environ.get('ADMIN_TOKEN')}":
               return jsonify({"error": "Unauthorized"}), 401
           
           # 运行初始化
           from init_db import init_db
           init_db()
           return jsonify({"message": "数据库初始化成功"})
       except Exception as e:
           return jsonify({"error": str(e)}), 500
   ```

2. **设置管理员令牌**
   
   在Vercel环境变量中添加：
   ```
   ADMIN_TOKEN=your-super-secret-admin-token
   ```

3. **调用初始化API**
   ```bash
   curl -X POST https://your-app.vercel.app/api/init-db \
        -H "Authorization: Bearer your-super-secret-admin-token"
   ```

## 🔄 数据库更新和迁移

### 1. 添加新的数据库模型

当您添加新的数据库模型时：

1. **更新模型文件**
   ```python
   # 在 app/models/ 中添加新模型
   class NewModel(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       # ... 其他字段
   ```

2. **更新初始化脚本**
   ```python
   # 在 init_db.py 中添加新表的创建逻辑
   def init_db():
       with app.app_context():
           db.create_all()  # 这会创建所有新表
           # ... 添加新数据
   ```

3. **重新运行初始化**
   ```bash
   vercel env pull .env.local
   python backend/init_db.py
   ```

### 2. 数据库架构更新

对于复杂的架构更改，建议使用Flask-Migrate：

1. **安装Flask-Migrate**
   ```bash
   pip install Flask-Migrate
   ```

2. **初始化迁移**
   ```python
   # 在 app/__init__.py 中
   from flask_migrate import Migrate
   
   migrate = Migrate()
   
   def create_app():
       app = Flask(__name__)
       # ... 其他配置
       migrate.init_app(app, db)
       return app
   ```

3. **生成迁移文件**
   ```bash
   flask db init
   flask db migrate -m "描述更改"
   flask db upgrade
   ```

### 3. 数据更新脚本

创建专门的数据更新脚本：

```python
# backend/update_data.py
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.recipe import Recipe

app = create_app()

def update_recipe_images():
    """更新菜谱图片URL"""
    with app.app_context():
        recipes = Recipe.query.all()
        for recipe in recipes:
            if recipe.image_url and 'example.com' in recipe.image_url:
                # 更新图片URL逻辑
                recipe.image_url = f"/images/{recipe.name}.jpg"
        
        db.session.commit()
        print(f"更新了 {len(recipes)} 个菜谱的图片")

if __name__ == "__main__":
    update_recipe_images()
```

## 🔧 数据库管理工具

### 新的数据库管理工具

我们提供了两个强大的数据库管理工具：

#### 1. `vercel_db.py` - Vercel专用工具
```bash
# 初始化数据库
python vercel_db.py init

# 检查数据库状态
python vercel_db.py check

# 更新菜谱图片URL
python vercel_db.py update-images

# 以JSON格式输出结果
python vercel_db.py check --json
```

#### 2. `backend/db_manager.py` - 完整管理工具
```bash
# 初始化数据库
python backend/db_manager.py init

# 检查数据库状态
python backend/db_manager.py status

# 更新图片URL
python backend/db_manager.py update-images

# 备份数据
python backend/db_manager.py backup

# 执行数据库迁移
python backend/db_manager.py migrate

# 重置数据库（危险操作）
python backend/db_manager.py reset
```

### 传统管理命令

#### 检查数据库状态
```python
# backend/check_db.py
from app import create_app, db
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient

app = create_app()

with app.app_context():
    print(f"菜谱数量: {Recipe.query.count()}")
    print(f"食材数量: {Ingredient.query.count()}")
    print("数据库连接正常")
```

#### 清空数据库
```python
# backend/reset_db.py
from app import create_app, db

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("数据库已重置")
```

#### 备份数据库
```bash
# 使用新工具备份
python backend/db_manager.py backup

# 或使用传统方式
pg_dump $DATABASE_URL > backup.sql
```

## 🔧 环境变量配置

确保在Vercel中设置以下环境变量：

```bash
# 数据库连接
DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/easycook?sslmode=require

# 应用配置
SECRET_KEY=your-super-secret-key
FLASK_ENV=production

# 管理员令牌（用于数据库操作）
ADMIN_TOKEN=your-admin-token

# 前端URL
FRONTEND_URL=https://your-app.vercel.app
```

## 🚨 注意事项

1. **生产环境安全**
   - 永远不要在生产环境中暴露数据库管理端点
   - 使用强密码和令牌
   - 定期备份数据库

2. **数据迁移**
   - 在进行重大更改前先备份数据库
   - 在测试环境中先验证迁移脚本
   - 避免在高峰期进行数据库操作

3. **监控和日志**
   - 监控数据库连接状态
   - 记录所有数据库操作日志
   - 设置错误警报

## 📞 故障排除

### 连接错误
```bash
# 测试数据库连接
python -c "
import os
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
print('数据库连接成功')
conn.close()
"
```

### 权限错误
确保数据库用户有足够的权限：
- CREATE TABLE
- INSERT, UPDATE, DELETE
- SELECT

### 超时错误
对于大量数据操作，考虑：
- 分批处理数据
- 增加连接超时时间
- 使用异步处理

## 📚 相关文档

- [Neon数据库文档](https://neon.tech/docs)
- [Flask-SQLAlchemy文档](https://flask-sqlalchemy.palletsprojects.com/)
- [Vercel环境变量](https://vercel.com/docs/concepts/projects/environment-variables)