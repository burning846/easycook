# EasyCook Vercel部署指南

本文档提供了如何将EasyCook应用部署到Vercel平台的详细说明，包括Neon数据库配置、监控设置和Google OAuth配置。

## 准备工作

1. 创建[Vercel](https://vercel.com)账号
2. 创建[Neon](https://neon.tech)数据库账号
3. 创建[Google Cloud Console](https://console.cloud.google.com)项目（如需OAuth登录）
4. 确保你的GitHub仓库已经包含了EasyCook项目代码

## 数据库配置（Neon PostgreSQL）

### 1. 创建Neon数据库

1. 登录[Neon控制台](https://console.neon.tech)
2. 点击"Create Project"
3. 填写项目信息：
   - Project name: `easycook-db`
   - Database name: `easycook`
   - Region: 选择离用户最近的区域
4. 点击"Create Project"

### 2. 获取数据库连接信息

1. 在项目仪表板中，点击"Connection Details"
2. 复制连接字符串，格式如下：
   ```
   postgresql://username:password@ep-xxx.region.aws.neon.tech/easycook?sslmode=require
   ```
3. 保存此连接字符串，稍后在Vercel中配置

## Google OAuth配置

### 1. 创建Google Cloud项目

1. 访问[Google Cloud Console](https://console.cloud.google.com)
2. 创建新项目或选择现有项目
3. 启用"Google+ API"和"Google Identity"服务

### 2. 配置OAuth同意屏幕

1. 在左侧菜单中选择"APIs & Services" > "OAuth consent screen"
2. 选择"External"用户类型
3. 填写应用信息：
   - App name: `EasyCook`
   - User support email: 你的邮箱
   - Developer contact information: 你的邮箱
4. 添加授权域名（部署后的Vercel域名）
5. 保存配置

### 3. 创建OAuth客户端

1. 在"APIs & Services" > "Credentials"中点击"Create Credentials"
2. 选择"OAuth client ID"
3. 应用类型选择"Web application"
4. 配置重定向URI：
   ```
   https://your-app.vercel.app/api/auth/google/callback
   https://your-app.vercel.app/login-success
   ```
5. 保存并记录Client ID和Client Secret

## Vercel网页端部署

### 1. 导入项目

1. 登录[Vercel控制台](https://vercel.com/dashboard)
2. 点击"Add New..." > "Project"
3. 选择"Import Git Repository"
4. 连接GitHub账号并选择EasyCook仓库
5. 点击"Import"

### 2. 项目配置

在"Configure Project"页面：

- **Framework Preset**: 选择"Other"
- **Root Directory**: 保持默认（./）
- **Build and Output Settings**: 保持默认（使用vercel.json配置）

### 3. 环境变量配置

在"Environment Variables"部分添加以下变量：

#### 必需变量
```bash
# 应用安全密钥（生成随机字符串）
SECRET_KEY=your-super-secret-key-here

# Neon数据库连接URL
DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/easycook?sslmode=require

# 前端URL（部署后更新）
FRONTEND_URL=https://your-app.vercel.app
```

#### Google OAuth变量（可选）
```bash
# Google OAuth客户端ID
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Google OAuth客户端密钥
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth重定向URI
GOOGLE_REDIRECT_URI=https://your-app.vercel.app/api/auth/google/callback
```

### 4. 部署

1. 确认所有配置正确
2. 点击"Deploy"开始部署
3. 等待构建完成（通常需要2-5分钟）
4. 部署成功后，记录分配的域名

### 5. 部署后配置

1. **更新环境变量**：
   - 将`FRONTEND_URL`更新为实际的Vercel域名
   - 在Google Cloud Console中添加实际的重定向URI

2. **数据库初始化**：
   ```bash
   # 使用Vercel CLI拉取环境变量
   vercel env pull .env.local
   
   # 运行数据库初始化
   python backend/init_db.py
   ```

### 6. 使用Vercel CLI部署（可选）

如果你更喜欢命令行操作：

1. 安装Vercel CLI：`npm install -g vercel`
2. 在项目根目录下登录：`vercel login`
3. 部署项目：`vercel`
4. 按照提示配置项目和环境变量
5. 生产环境部署：`vercel --prod`

## 项目结构说明

本项目已经为Vercel部署做了以下配置：

1. **`vercel.json`**：Vercel配置文件，定义了构建和路由规则
   - 前端：使用`@vercel/static-build`构建到`frontend/dist`
   - 后端：使用`@vercel/python`运行Flask应用
   - 路由：API请求转发到后端，静态资源和页面路由到前端

2. **`backend/vercel_app.py`**：Vercel后端入口文件
   - Flask应用实例
   - 数据库连接配置
   - API路由定义

3. **前端构建配置**：
   - `frontend/package.json`：定义构建脚本
   - `frontend/webpack.config.js`：Webpack配置
   - `frontend/public/404.html`：客户端路由回退页面

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

## Vercel监控配置

Vercel提供了强大的监控和分析功能，帮助你了解应用性能和用户行为。

### 1. 启用Vercel Analytics

1. 在Vercel项目仪表板中，点击"Analytics"选项卡
2. 点击"Enable Analytics"
3. 选择合适的计划（免费版提供基础功能）
4. Analytics将自动开始收集数据

**功能包括**：
- 页面浏览量统计
- 用户访问路径分析
- 地理位置分布
- 设备和浏览器统计
- 实时访问监控

### 2. 启用Speed Insights

1. 在项目设置中找到"Speed Insights"
2. 点击"Enable Speed Insights"
3. 添加监控代码到前端（可选，Vercel会自动注入）

**监控指标**：
- Core Web Vitals（LCP、FID、CLS）
- 页面加载时间
- 首次内容绘制（FCP）
- 最大内容绘制（LCP）
- 累积布局偏移（CLS）

### 3. 函数监控

1. 在"Functions"选项卡中查看API函数性能
2. 监控指标包括：
   - 执行时间
   - 内存使用
   - 错误率
   - 调用频率

### 4. 日志监控

**实时日志查看**：
1. 在项目仪表板中点击"Functions"选项卡
2. 选择具体的函数查看详细日志
3. 使用CLI实时查看：`vercel logs`

**日志类型**：
- 构建日志：查看部署过程中的输出
- 函数日志：查看API请求和响应
- 错误日志：捕获运行时错误

### 5. 错误监控集成

**推荐集成Sentry进行错误监控**：

1. 创建[Sentry](https://sentry.io)账号
2. 在前端添加Sentry SDK：
   ```bash
   npm install @sentry/react @sentry/tracing
   ```
3. 配置Sentry（在`frontend/src/index.js`中）：
   ```javascript
   import * as Sentry from "@sentry/react";
   
   Sentry.init({
     dsn: "YOUR_SENTRY_DSN",
     environment: process.env.NODE_ENV,
   });
   ```
4. 在Vercel环境变量中添加：
   ```bash
   SENTRY_DSN=your-sentry-dsn
   ```

### 6. 自定义监控警报

**设置Vercel集成**：
1. 在项目设置中点击"Integrations"
2. 添加Slack、Discord或邮件通知
3. 配置警报条件：
   - 部署失败
   - 函数错误率过高
   - 响应时间异常

**监控检查清单**：
- ✅ Analytics已启用
- ✅ Speed Insights已配置
- ✅ 函数监控正常
- ✅ 错误监控已集成
- ✅ 警报通知已设置

### 7. 性能优化建议

基于监控数据进行优化：

1. **前端优化**：
   - 图片懒加载
   - 代码分割
   - CDN缓存策略

2. **后端优化**：
   - 数据库查询优化
   - API响应缓存
   - 函数冷启动优化

3. **监控最佳实践**：
   - 定期检查Core Web Vitals
   - 监控API响应时间
   - 跟踪错误率趋势
   - 分析用户行为模式

## 完整部署检查清单

### 部署前准备
- [ ] Neon数据库已创建并获取连接字符串
- [ ] Google Cloud项目已创建（如需OAuth）
- [ ] OAuth客户端已配置
- [ ] GitHub仓库代码已更新

### Vercel配置
- [ ] 项目已导入到Vercel
- [ ] 框架预设选择"Other"
- [ ] 环境变量已正确配置：
  - [ ] `SECRET_KEY`
  - [ ] `DATABASE_URL`
  - [ ] `FRONTEND_URL`
  - [ ] `GOOGLE_CLIENT_ID`（可选）
  - [ ] `GOOGLE_CLIENT_SECRET`（可选）

### 部署后验证
- [ ] 部署成功完成
- [ ] 网站可以正常访问
- [ ] API端点响应正常
- [ ] 数据库连接正常
- [ ] Google OAuth登录正常（如已配置）

### 监控配置
- [ ] Vercel Analytics已启用
- [ ] Speed Insights已配置
- [ ] 错误监控已集成
- [ ] 警报通知已设置

## 故障排除

### 常见问题及解决方案

#### 1. 部署失败

**问题**：构建过程中出现错误

**解决方案**：
1. 检查构建日志中的具体错误信息
2. 确保所有依赖项在`package.json`和`requirements.txt`中正确列出
3. 验证环境变量是否正确设置
4. 检查代码语法错误

#### 2. 数据库连接失败

**问题**：API返回数据库连接错误

**解决方案**：
1. 验证`DATABASE_URL`格式是否正确
2. 确保Neon数据库正在运行
3. 检查数据库用户权限
4. 运行数据库初始化脚本：
   ```bash
   vercel env pull .env.local
   python backend/init_db.py
   ```

#### 3. 404错误

**问题**：页面刷新后出现404错误

**解决方案**：
1. 检查`vercel.json`路由配置
2. 确保`frontend/public/404.html`存在
3. 验证前端路由配置

#### 4. Google OAuth失败

**问题**：OAuth登录重定向失败

**解决方案**：
1. 检查Google Cloud Console中的重定向URI配置
2. 确保`GOOGLE_CLIENT_ID`和`GOOGLE_CLIENT_SECRET`正确
3. 验证OAuth同意屏幕配置
4. 检查域名是否在授权域名列表中

#### 5. API CORS错误

**问题**：前端无法访问API

**解决方案**：
1. 检查Flask-CORS配置
2. 验证`FRONTEND_URL`环境变量
3. 确保API路由正确配置

### 调试工具

1. **Vercel CLI调试**：
   ```bash
   vercel logs --follow
   vercel env ls
   vercel inspect
   ```

2. **本地调试**：
   ```bash
   vercel dev
   vercel env pull .env.local
   ```

3. **数据库调试**：
   ```bash
   # 测试数据库连接
   python -c "from backend.config import Config; print(Config.SQLALCHEMY_DATABASE_URI)"
   ```

## 维护和更新

### 定期维护任务

1. **每周**：
   - 检查监控指标
   - 查看错误日志
   - 更新依赖项

2. **每月**：
   - 数据库备份验证
   - 性能优化评估
   - 安全更新检查

3. **每季度**：
   - 全面性能审查
   - 用户反馈分析
   - 架构优化评估

### 更新部署流程

1. **代码更新**：
   ```bash
   git add .
   git commit -m "更新描述"
   git push origin main
   ```
   Vercel会自动检测并重新部署

2. **环境变量更新**：
   - 在Vercel控制台中更新
   - 或使用CLI：`vercel env add`

3. **数据库迁移**：
   ```bash
   # 生成迁移文件
   flask db migrate -m "迁移描述"
   
   # 推送代码
   git add .
   git commit -m "数据库迁移"
   git push
   
   # 在生产环境执行迁移
   vercel env pull .env.local
   flask db upgrade
   ```

---

**部署完成！** 🎉

你的EasyCook应用现在已经成功部署到Vercel，配置了Neon数据库、Google OAuth和完整的监控系统。记得定期检查监控指标并根据用户反馈进行优化。