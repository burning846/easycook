# EasyCook 数据库管理工具

本项目提供了多个便捷的数据库管理工具，帮助您在Vercel环境中轻松管理数据库。

## 🛠️ 工具概览

### 1. 一键部署脚本 (`deploy.sh`)
完整的部署流程，包括依赖安装、构建、部署和数据库初始化。

```bash
# 完整部署
./deploy.sh

# 跳过某些步骤
./deploy.sh --skip-deps --skip-build

# 查看帮助
./deploy.sh --help
```

### 2. Vercel专用工具 (`vercel_db.py`)
专门为Vercel环境设计的轻量级数据库管理工具。

```bash
# 初始化数据库
python vercel_db.py init

# 检查数据库状态
python vercel_db.py check

# 更新菜谱图片
python vercel_db.py update-images

# JSON格式输出
python vercel_db.py check --json
```

### 3. 完整管理工具 (`backend/db_manager.py`)
功能完整的数据库管理工具，支持备份、迁移等高级功能。

```bash
# 初始化数据库
python backend/db_manager.py init

# 检查状态
python backend/db_manager.py status

# 备份数据
python backend/db_manager.py backup

# 执行迁移
python backend/db_manager.py migrate

# 重置数据库（危险）
python backend/db_manager.py reset
```

## 🚀 快速开始

### 首次部署

1. **克隆项目并进入目录**
   ```bash
   git clone <your-repo-url>
   cd easycook
   ```

2. **运行一键部署**
   ```bash
   ./deploy.sh
   ```

3. **验证部署**
   ```bash
   python vercel_db.py check
   ```

### 日常管理

#### 检查数据库状态
```bash
# 快速检查
python vercel_db.py check

# 详细统计
python backend/db_manager.py status
```

#### 更新数据库
```bash
# 更新图片URL
python vercel_db.py update-images

# 执行架构迁移
python backend/db_manager.py migrate
```

#### 备份数据
```bash
# 创建备份
python backend/db_manager.py backup
```

## 📋 使用场景

### 场景1：首次部署
```bash
# 一键完成所有步骤
./deploy.sh
```

### 场景2：代码更新后重新部署
```bash
# 跳过依赖安装，只部署和更新数据库
./deploy.sh --skip-deps
```

### 场景3：仅更新数据库
```bash
# 拉取最新环境变量
vercel env pull .env.local

# 检查当前状态
python vercel_db.py check

# 执行必要的更新
python vercel_db.py update-images
```

### 场景4：数据库维护
```bash
# 备份数据
python backend/db_manager.py backup

# 检查状态
python backend/db_manager.py status

# 执行迁移
python backend/db_manager.py migrate
```

## ⚠️ 注意事项

1. **环境变量**：确保已正确配置Vercel环境变量，特别是`DATABASE_URL`
2. **权限**：确保数据库用户有足够的权限执行DDL操作
3. **备份**：在执行重置或迁移操作前，建议先备份数据
4. **网络**：确保能够访问Neon数据库

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查环境变量
vercel env pull .env.local
cat .env.local | grep DATABASE_URL

# 测试连接
python vercel_db.py check
```

#### 2. 权限不足
```bash
# 检查数据库用户权限
# 确保用户有CREATE、ALTER、DROP权限
```

#### 3. 迁移失败
```bash
# 查看详细错误信息
python backend/db_manager.py migrate

# 如果需要，可以重置数据库
python backend/db_manager.py reset
```

## 📚 更多信息

- 详细部署指南：[VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)
- 数据库管理指南：[VERCEL_DATABASE_GUIDE.md](./VERCEL_DATABASE_GUIDE.md)
- 项目文档：[README.md](./README.md)

## 🤝 贡献

如果您发现问题或有改进建议，欢迎提交Issue或Pull Request。

---

**提示**：这些工具设计为幂等操作，可以安全地多次运行。