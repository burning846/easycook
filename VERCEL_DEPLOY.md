# EasyCook Vercel部署指南

本文档提供了如何将EasyCook应用部署到Vercel平台的详细说明。

## 准备工作

1. 创建[Vercel](https://vercel.com)账号
2. 安装Vercel CLI（可选）：`npm install -g vercel`
3. 确保你的GitHub仓库已经包含了EasyCook项目代码

## 部署步骤

### 方法一：使用Vercel网页界面

1. 登录Vercel账号
2. 点击"New Project"
3. 导入你的GitHub仓库
4. 配置项目：
   - 框架预设：选择"Other"
   - 构建命令：保持默认（使用vercel.json中的配置）
   - 输出目录：保持默认（使用vercel.json中的配置）
5. 环境变量设置：
   - `SECRET_KEY`: 设置一个安全的随机字符串
   - `DATABASE_URL`: 设置数据库连接URL（推荐使用Vercel集成的PostgreSQL或其他云数据库）
   - `GOOGLE_CLIENT_ID`: 如果使用Google登录，设置Google客户端ID
   - `GOOGLE_CLIENT_SECRET`: 如果使用Google登录，设置Google客户端密钥
6. 点击"Deploy"开始部署

### 方法二：使用Vercel CLI

1. 在项目根目录下登录Vercel：`vercel login`
2. 部署项目：`vercel`
3. 按照提示配置项目和环境变量
4. 完成部署后，可以使用`vercel --prod`进行生产环境部署

## 项目结构说明

本项目已经为Vercel部署做了以下配置：

1. `vercel.json`：Vercel配置文件，定义了构建和路由规则
2. `backend/vercel_app.py`：Vercel后端入口文件
3. `frontend/src/services/vercel-api.config.js`：Vercel API配置文件

## 数据库配置

在Vercel上部署时，推荐使用以下数据库服务：

1. Vercel Postgres（Vercel集成的PostgreSQL服务）
2. Supabase（开源PostgreSQL服务）
3. MongoDB Atlas（文档数据库）

配置步骤：

1. 在Vercel项目设置中添加数据库集成
2. 获取数据库连接URL
3. 在环境变量中设置`DATABASE_URL`

## 自定义域名设置

1. 在Vercel项目设置中，进入"Domains"选项卡
2. 添加你的自定义域名：`easyfood.burning233.top`
3. 按照Vercel提供的说明配置DNS记录
4. 等待DNS生效（通常需要几分钟到几小时）

## 常见问题

### 数据库迁移

在首次部署时，需要手动运行数据库迁移：

1. 使用Vercel CLI连接到项目：`vercel env pull .env.local`
2. 运行迁移命令：`vercel run backend/init_db.py`

### API连接问题

如果前端无法连接到API，请检查：

1. 环境变量`API_URL`是否正确设置
2. Vercel路由配置是否正确
3. 浏览器控制台是否有CORS错误

### 部署失败

如果部署失败，请检查：

1. 构建日志中的错误信息
2. 确保所有必要的环境变量已设置
3. 确保项目结构符合Vercel要求

## 更新部署

当你更新代码后，Vercel会自动检测GitHub仓库的变更并重新部署。你也可以：

1. 在Vercel仪表板中手动触发重新部署
2. 使用CLI命令：`vercel --prod`

## 监控和日志

Vercel提供了内置的监控和日志功能：

1. 在项目仪表板中查看部署状态和性能指标
2. 在"Logs"选项卡中查看应用日志
3. 设置自定义警报以监控应用健康状况