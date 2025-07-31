import axios from 'axios';
// 根据环境选择合适的API配置
import API_BASE_URL from './api.config';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 处理错误响应
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('API错误:', error.response.data);
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      console.error('网络错误:', error.request);
    } else {
      // 请求配置出错
      console.error('请求错误:', error.message);
    }
    return Promise.reject(error);
  }
);

// 菜谱相关API
const recipeApi = {
  // 获取菜谱列表
  getRecipes: (params) => api.get('/recipes', { params }),
  
  // 获取单个菜谱详情
  getRecipe: (id) => api.get(`/recipes/${id}`),
  
  // 创建菜谱
  createRecipe: (data) => api.post('/recipes', data),
  
  // 更新菜谱
  updateRecipe: (id, data) => api.put(`/recipes/${id}`, data),
  
  // 删除菜谱
  deleteRecipe: (id) => api.delete(`/recipes/${id}`),
  
  // 获取菜谱分类
  getCategories: () => api.get('/recipes/categories'),
  
  // 搜索菜谱
  searchRecipes: (query) => api.get('/recipes/search', { params: { q: query } }),
};

// 食材相关API
const ingredientApi = {
  // 获取食材列表
  getIngredients: (params) => api.get('/ingredients', { params }),
  
  // 获取单个食材详情
  getIngredient: (id) => api.get(`/ingredients/${id}`),
  
  // 创建食材
  createIngredient: (data) => api.post('/ingredients', data),
  
  // 更新食材
  updateIngredient: (id, data) => api.put(`/ingredients/${id}`, data),
  
  // 删除食材
  deleteIngredient: (id) => api.delete(`/ingredients/${id}`),
  
  // 获取食材分类
  getCategories: () => api.get('/ingredients/categories'),
  
  // 搜索食材
  searchIngredients: (query) => api.get('/ingredients/search', { params: { q: query } }),
};

// 用户相关API
const userApi = {
  // 获取用户信息
  getUser: (id) => api.get(`/users/${id}`),
  
  // 创建用户
  createUser: (data) => api.post('/users', data),
  
  // 获取用户食材库
  getUserIngredients: (userId) => api.get(`/users/${userId}/ingredients`),
  
  // 添加食材到用户食材库
  addUserIngredient: (userId, data) => api.post(`/users/${userId}/ingredients`, data),
  
  // 更新用户食材库中的食材
  updateUserIngredient: (userId, ingredientId, data) => 
    api.put(`/users/${userId}/ingredients/${ingredientId}`, data),
  
  // 从用户食材库中删除食材
  deleteUserIngredient: (userId, ingredientId) => 
    api.delete(`/users/${userId}/ingredients/${ingredientId}`),
  
  // 获取用户购物清单
  getShoppingLists: (userId) => api.get(`/users/${userId}/shopping_lists`),
  
  // 获取单个购物清单详情
  getShoppingList: (userId, listId) => api.get(`/users/${userId}/shopping_lists/${listId}`),
  
  // 创建购物清单
  createShoppingList: (userId, data) => api.post(`/users/${userId}/shopping_lists`, data),
  
  // 删除购物清单
  deleteShoppingList: (userId, listId) => api.delete(`/users/${userId}/shopping_lists/${listId}`),
  
  // 添加食材到购物清单
  addShoppingListItem: (userId, listId, data) => 
    api.post(`/users/${userId}/shopping_lists/${listId}/items`, data),
  
  // 更新购物清单中的食材
  updateShoppingListItem: (userId, listId, itemId, data) => 
    api.put(`/users/${userId}/shopping_lists/${listId}/items/${itemId}`, data),
  
  // 从购物清单中删除食材
  deleteShoppingListItem: (userId, listId, itemId) => 
    api.delete(`/users/${userId}/shopping_lists/${listId}/items/${itemId}`),
  
  // 获取用户偏好设置
  getUserPreferences: (userId) => api.get(`/users/${userId}/preferences`),
  
  // 添加用户偏好设置
  addUserPreference: (userId, data) => api.post(`/users/${userId}/preferences`, data),
  
  // 删除用户偏好设置
  deleteUserPreference: (userId, key) => api.delete(`/users/${userId}/preferences/${key}`),
  
  // 获取用户收藏的菜谱
  getFavorites: (userId, params) => api.get(`/users/${userId}/favorites`, { params }),
  
  // 添加菜谱到收藏
  addFavorite: (userId, recipeId) => api.post(`/users/${userId}/favorites`, { recipe_id: recipeId }),
  
  // 从收藏中移除菜谱
  removeFavorite: (userId, recipeId) => api.delete(`/users/${userId}/favorites/${recipeId}`),
  
  // 检查菜谱是否已收藏
  checkFavorite: (userId, recipeId) => api.get(`/users/${userId}/favorites/check/${recipeId}`),
};

export { recipeApi, ingredientApi, userApi };