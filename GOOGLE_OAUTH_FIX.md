# Google OAuth重定向URI修复指南

## 🚨 问题描述
`Error 400: redirect_uri_mismatch` - Google OAuth重定向URI不匹配错误

## 🔍 问题原因
1. **缺少FRONTEND_URL环境变量** - 导致重定向URI生成错误
2. **Google Cloud Console中未配置正确的重定向URI**
3. **Vercel部署URL动态变化，需要及时更新**

## 🛠️ 解决方案

### 步骤1: 在Google Cloud Console中添加重定向URI

访问 [Google Cloud Console](https://console.cloud.google.com/apis/credentials) 并添加以下重定向URI：

#### 本地开发环境
```
http://localhost:3000/login-success
http://localhost:5000/api/auth/google/callback
http://localhost:3000/api/auth/google/callback
```

#### 生产环境 (基于当前Vercel部署)
```
https://easycook-l6uf9f3te-burning846s-projects.vercel.app/api/auth/google/callback
https://easycook-l6uf9f3te-burning846s-projects.vercel.app/login-success
https://easycook-anzml4r4m-burning846s-projects.vercel.app/api/auth/google/callback
https://easycook-anzml4r4m-burning846s-projects.vercel.app/login-success
https://easycook-lgf2zvgyz-burning846s-projects.vercel.app/api/auth/google/callback
https://easycook-lgf2zvgyz-burning846s-projects.vercel.app/login-success
```

### 步骤2: 更新Vercel环境变量

#### 方法1: 使用Vercel CLI
```bash
# 设置生产环境URL
vercel env add FRONTEND_URL "https://easycook-l6uf9f3te-burning846s-projects.vercel.app" production

# 设置预览环境URL
vercel env add FRONTEND_URL "https://easycook-l6uf9f3te-burning846s-projects.vercel.app" preview

# 设置开发环境URL
vercel env add FRONTEND_URL "http://localhost:3000" development
```

#### 方法2: 使用Vercel Web界面
1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择 `easycook` 项目
3. 进入 `Settings` > `Environment Variables`
4. 添加以下变量：
   - `FRONTEND_URL` = `https://easycook-l6uf9f3te-burning846s-projects.vercel.app`

### 步骤3: 重新部署应用
```bash
vercel --prod
```

### 步骤4: 测试Google登录功能

## 🔧 自动化脚本

使用提供的 `fix_oauth.py` 脚本来自动分析和生成配置：

```bash
python fix_oauth.py
```

## 📋 检查清单

- [ ] Google Cloud Console中添加了所有重定向URI
- [ ] Vercel环境变量中设置了FRONTEND_URL
- [ ] 重新部署了应用
- [ ] 测试了Google登录功能

## ⚠️ 注意事项

1. **动态URL问题**: Vercel每次部署都会生成新的URL，需要及时更新Google Console配置
2. **通配符限制**: Google Cloud Console不支持通配符，必须添加具体的URL
3. **建议**: 考虑设置自定义域名以避免频繁更新重定向URI

## 🚀 长期解决方案

### 设置自定义域名
1. 在Vercel中添加自定义域名
2. 更新Google Cloud Console重定向URI为固定域名
3. 更新环境变量使用固定域名

示例：
```
https://easycook.yourdomain.com/api/auth/google/callback
https://easycook.yourdomain.com/login-success
```

## 🔍 调试命令

```bash
# 检查当前环境变量
grep -E "(GOOGLE|FRONTEND)" .env.local

# 查看Vercel部署状态
vercel ls | head -10

# 检查应用健康状态
python health_check.py https://your-deployment-url.vercel.app

# 查看Vercel环境变量
vercel env ls
```

## 📞 故障排除

如果问题仍然存在：

1. **检查环境变量是否正确设置**
2. **确认Google Cloud Console中的Client ID与应用中的一致**
3. **验证重定向URI的大小写和路径是否完全匹配**
4. **检查是否有缓存问题，尝试清除浏览器缓存**

---

*最后更新: 2025-10-08*