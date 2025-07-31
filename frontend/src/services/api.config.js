// API配置文件

// 获取环境配置
const getApiBaseUrl = () => {
  // 如果在window.ENV中定义了API_URL（生产环境），则使用它
  if (window.ENV && window.ENV.API_URL) {
    return window.ENV.API_URL;
  }
  
  // 开发环境默认使用相对路径，通过webpack代理转发
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();
export default API_BASE_URL;