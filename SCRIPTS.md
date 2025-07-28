# EasyCook 维护脚本说明

本文档提供了EasyCook应用中包含的所有维护脚本的详细说明。

## 部署脚本

### deploy.sh

传统部署脚本，使用Nginx和Gunicorn部署应用。

**用法：**
```bash
chmod +x deploy.sh
./deploy.sh
```

**功能：**
- 检查必要的工具（Python3、npm、Nginx、Certbot）
- 设置目录结构
- 构建前端应用
- 设置后端环境（虚拟环境、依赖、Gunicorn）
- 配置Nginx（前端和后端API）
- 申请SSL证书（使用Certbot）

### deploy-docker.sh

基于Docker的部署脚本，推荐使用此方式部署。

**用法：**
```bash
chmod +x deploy-docker.sh
./deploy-docker.sh
```

**功能：**
- 检查Docker和Docker Compose
- 创建.env文件（如果不存在）
- 设置必要的目录
- 构建和启动Docker容器
- 初始化数据库
- 申请SSL证书（可选）

### deploy-conda.sh

基于Conda环境的部署脚本，适合熟悉Conda的用户。

**用法：**
```bash
chmod +x deploy-conda.sh
./deploy-conda.sh
```

**功能：**
- 检查Conda、Nginx和Certbot
- 创建前端和后端的Conda环境
- 安装所有依赖
- 构建前端应用
- 初始化数据库
- 配置Nginx和SSL证书
- 创建系统服务实现自动启动

### init-server.sh

服务器初始化脚本，用于在新服务器上快速设置部署环境。

**用法：**
```bash
sudo chmod +x init-server.sh
sudo ./init-server.sh
```

**功能：**
- 更新系统
- 安装基本工具（curl、wget、git、vim、htop）
- 安装Docker和Docker Compose
- 安装Nginx和Certbot
- 配置防火墙
- 创建部署用户
- 设置SSH密钥
- 创建应用目录
- 配置Swap（如果内存小于2GB）
- 设置时区
- 安装Node.js和Python环境

## 维护脚本

### backup.sh

数据库备份脚本，用于定期备份应用数据。

**用法：**
```bash
chmod +x backup.sh
./backup.sh
```

**功能：**
- 备份SQLite或PostgreSQL数据库
- 压缩备份文件
- 清理旧备份（保留最近30天的备份）
- 显示当前备份信息

### restore.sh

数据库恢复脚本，用于从备份中恢复数据库。

**用法：**
```bash
chmod +x restore.sh
./restore.sh
```

**功能：**
- 列出可用备份
- 从选定的备份恢复数据库
- 自动停止和启动应用服务
- 备份当前数据库（以防恢复失败）

### monitor.sh

应用监控脚本，用于检查应用的运行状态。

**用法：**
```bash
chmod +x monitor.sh
./monitor.sh
```

**功能：**
- 检查Docker服务状态
- 检查容器状态
- 检查前端和后端API服务
- 检查系统资源（CPU、内存、磁盘）
- 检查Docker容器资源使用情况
- 检查日志文件大小
- 检查SSL证书有效期

### upgrade.sh

应用升级脚本，用于更新应用代码和依赖。

**用法：**
```bash
chmod +x upgrade.sh
./upgrade.sh
```

**功能：**
- 备份当前代码和数据库
- 处理未提交的更改
- 拉取最新代码
- 更新Docker容器或传统部署
- 运行数据库迁移
- 检查应用状态

### upgrade-conda.sh

Conda环境下的应用升级脚本。

**用法：**
```bash
chmod +x upgrade-conda.sh
./upgrade-conda.sh
```

**功能：**
- 备份当前代码和数据库
- 处理未提交的更改
- 拉取最新代码
- 更新Conda环境中的前端和后端依赖
- 重新构建前端
- 运行数据库迁移
- 重启服务

### cleanup.sh

系统清理脚本，用于清理临时文件和旧的备份。

**用法：**
```bash
chmod +x cleanup.sh
./cleanup.sh        # 标准清理
./cleanup.sh --deep # 深度清理（包括重建依赖）
```

**功能：**
- 清理临时文件
- 清理前端构建缓存
- 清理Docker缓存
- 清理旧的备份文件
- 清理日志文件
- 清理会话文件
- 清理未使用的依赖包（深度清理模式）

### security-check.sh

安全检查脚本，用于检查应用的安全配置。

**用法：**
```bash
chmod +x security-check.sh
./security-check.sh
```

**功能：**
- 检查文件权限
- 检查敏感信息泄露
- 检查Docker安全配置
- 检查SSL配置
- 检查防火墙配置
- 检查日志文件权限
- 检查数据库文件权限
- 检查依赖项安全问题

## 配置文件

### crontab.example

定时任务示例文件，用于自动化备份和监控。

**用法：**
```bash
cat crontab.example
sudo cp crontab.example /etc/cron.d/easycook
sudo chmod 644 /etc/cron.d/easycook
```

### logrotate.conf

日志轮转配置文件，用于管理应用日志。

**用法：**
```bash
sudo cp logrotate.conf /etc/logrotate.d/easycook
sudo chmod 644 /etc/logrotate.d/easycook
```

## 其他文件

### conda-manage.sh

Conda环境管理脚本，用于管理和更新Conda环境。

**用法：**
```bash
chmod +x conda-manage.sh
./conda-manage.sh [选项]
```

**功能：**
- 更新前端和后端环境依赖
- 重建前端和后端环境
- 显示环境状态
- 列出所有环境

### start-conda.sh

Conda环境下的应用启动脚本。

**用法：**
```bash
chmod +x start-conda.sh
./start-conda.sh [选项]
```

**功能：**
- 启动后端服务
- 停止服务
- 重启服务
- 显示服务状态

### .env.example

Docker Compose环境配置示例文件。

**用法：**
```bash
cp .env.example .env
vim .env  # 编辑配置
```

### deploy.config

传统部署配置文件。

**用法：**
```bash
vim deploy.config  # 编辑配置
```