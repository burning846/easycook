# EasyCook 应用部署指南

## 项目介绍

EasyCook是一个帮助用户发现美食、规划菜单、管理食材的应用。主要功能包括：

- 菜谱浏览与搜索
- 食材管理
- 购物清单
- 收藏菜谱
- Google账号登录

## 域名规划

本项目使用以下域名结构：

- 主域名：`easyfood.burning233.top` - 前端应用
- API子域名：`api.easyfood.burning233.top` - 后端API服务

## 部署方式

### 方式一：传统部署（使用Nginx和Gunicorn）

1. 克隆代码库

```bash
git clone <repository-url>
cd easycook
```

2. 配置部署参数

```bash
# 编辑部署配置文件
vim deploy.config
```

3. 执行部署脚本

```bash
chmod +x deploy.sh
./deploy.sh
```

### 方式二：Docker部署（推荐）

1. 克隆代码库

```bash
git clone <repository-url>
cd easycook
```

2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入正确的配置信息
vim .env
```

3. 执行Docker部署脚本

```bash
chmod +x deploy-docker.sh
./deploy-docker.sh
```

### 方式三：Conda部署

使用Conda环境部署前端和后端，适合熟悉Conda的用户。

1. 克隆代码库

```bash
git clone <repository-url>
cd easycook
```

2. 执行Conda部署脚本

```bash
chmod +x deploy-conda.sh
./deploy-conda.sh
```

此脚本会：
- 创建前端和后端的Conda环境
- 安装所有依赖
- 配置Nginx和SSL证书
- 设置系统服务自动启动

3. 管理Conda环境

部署完成后，可以使用以下脚本管理Conda环境：

```bash
# 查看环境状态
./conda-manage.sh status

# 更新前端依赖
./conda-manage.sh update-frontend

# 更新后端依赖
./conda-manage.sh update-backend

# 更新所有依赖
./conda-manage.sh update-all
```

4. 启动和停止服务

```bash
# 启动服务
./start-conda.sh start

# 停止服务
./start-conda.sh stop

# 重启服务
./start-conda.sh restart

# 查看服务状态
./start-conda.sh status
```

## Google OAuth配置

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建一个新项目
3. 在API和服务中启用Google+ API
4. 创建OAuth客户端ID
5. 添加授权重定向URI：`https://api.burning233.top/api/auth/google/callback`
6. 将客户端ID和密钥添加到`.env`文件中

## 目录结构

```
├── backend/             # 后端Flask应用
│   ├── app/             # 应用代码
│   │   ├── models/      # 数据模型
│   │   ├── routes/      # API路由
│   │   └── services/    # 业务逻辑
│   ├── Dockerfile       # 后端Docker配置
│   └── requirements.txt # Python依赖
├── frontend/            # 前端React应用
│   ├── src/             # 源代码
│   ├── public/          # 静态资源
│   └── Dockerfile       # 前端Docker配置
├── nginx/               # Nginx配置
├── docker-compose.yml   # Docker Compose配置
├── deploy.sh            # 传统部署脚本
├── deploy-docker.sh     # Docker部署脚本
├── init-server.sh       # 服务器初始化脚本
├── backup.sh            # 数据库备份脚本
├── restore.sh           # 数据库恢复脚本
├── monitor.sh           # 应用监控脚本
├── upgrade.sh           # 应用升级脚本
├── cleanup.sh           # 系统清理脚本
├── security-check.sh    # 安全检查脚本
├── crontab.example      # 定时任务示例
├── logrotate.conf       # 日志轮转配置
└── SCRIPTS.md           # 脚本说明文档
```

有关所有维护脚本的详细说明，请参阅 [SCRIPTS.md](SCRIPTS.md) 文件。

## 维护指南

### 服务器初始化

在新服务器上首次部署前，可以使用初始化脚本快速配置环境：

```bash
# 以root用户运行
sudo chmod +x init-server.sh
sudo ./init-server.sh
```

### 数据库备份与恢复

使用自动化脚本进行数据库备份：

```bash
# 执行备份
chmod +x backup.sh
./backup.sh

# 从备份恢复
chmod +x restore.sh
./restore.sh
```

也可以手动执行备份：

```bash
# 对于SQLite数据库
docker-compose exec backend sqlite3 app.db .dump > backup.sql

# 对于PostgreSQL数据库
docker-compose exec db pg_dump -U username easycook > backup.sql
```

### 应用监控

使用监控脚本检查应用状态：

```bash
chmod +x monitor.sh
./monitor.sh
```

### 日志查看

```bash
# 查看容器日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 查看监控和备份日志
cat /var/log/easycook-monitor.log
cat /var/log/easycook-backup.log
```

### SSL证书更新

SSL证书通过Certbot自动更新，无需手动操作。如需手动更新：

```bash
docker-compose run --rm certbot renew
```

### 定时任务

项目提供了定时任务示例文件，用于自动化备份、监控和维护：

```bash
# 查看定时任务示例
cat crontab.example

# 添加到系统定时任务
sudo cp crontab.example /etc/cron.d/easycook
sudo chmod 644 /etc/cron.d/easycook
```

### 日志轮转

为防止日志文件过大，项目提供了日志轮转配置：

```bash
# 安装日志轮转配置
sudo cp logrotate.conf /etc/logrotate.d/easycook
sudo chmod 644 /etc/logrotate.d/easycook
```

### 系统清理

定期清理临时文件和旧备份以释放磁盘空间：

```bash
# 标准清理
chmod +x cleanup.sh
./cleanup.sh

# 深度清理（包括重建依赖）
./cleanup.sh --deep
```

### 应用升级

使用升级脚本更新应用到最新版本：

```bash
# Docker或传统部署
chmod +x upgrade.sh
./upgrade.sh

# Conda部署
chmod +x upgrade-conda.sh
./upgrade-conda.sh
```

## 故障排除

1. 如果前端无法连接到后端API，检查：
   - Nginx配置是否正确
   - API服务是否正常运行
   - 防火墙设置是否允许相应端口

2. 如果Google登录失败，检查：
   - Google OAuth配置是否正确
   - 重定向URI是否匹配
   - SSL证书是否有效（Google OAuth要求HTTPS）

3. 如果升级后应用无法正常工作：
   - 检查日志文件中的错误信息
   - 使用 `./monitor.sh` 检查服务状态
   - 从备份恢复：`./restore.sh`

4. Conda环境问题排查：
   - 检查环境状态：`./conda-manage.sh status`
   - 重建损坏的环境：`./conda-manage.sh rebuild-all`
   - 查看服务日志：`tail -f /var/www/easycook/logs/backend.log`
   - 重启服务：`./start-conda.sh restart`

5. 安全问题排查：
   - 使用安全检查脚本：`./security-check.sh`
   - 检查并修复脚本提示的安全问题
   - 定期更新依赖包以修复已知漏洞

## 联系方式

如有问题，请联系管理员：sbn1998@pku.edu.cn