// Vercel API配置文件
let API_BASE_URL;

// 根据环境设置API基础URL
if (process.env.NODE_ENV === 'production') {
  // 在Vercel上，API和前端在同一个域名下，使用相对路径
  API_BASE_URL = '/api';
} else {
  // 开发环境使用相对路径
  API_BASE_URL = '/api';
}

export default API_BASE_URL;