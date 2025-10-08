// API配置文件

// 获取环境配置
const getApiBaseUrl = () => {
  // 如果在window.ENV中定义了API_URL（生产环境），则使用它
  if (window.ENV && window.ENV.API_URL) {
    return window.ENV.API_URL;
  }
  
  // 开发环境使用完整的后端URL
  if (process.env.NODE_ENV === 'development') {
    return 'http://127.0.0.1:5000/api';
  }
  
  // 生产环境使用相对路径
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();
export default API_BASE_URL;