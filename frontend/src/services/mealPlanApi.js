const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://easycook-backend.vercel.app/api'
  : 'http://127.0.0.1:5000/api';

class MealPlanApi {
  /**
   * 生成AI菜谱规划
   * @param {Object} params - 规划参数
   * @param {number} params.days - 规划天数
   * @param {Array} params.dietary_preferences - 饮食偏好
   * @param {Array} params.allergies - 过敏信息
   * @param {string} params.cuisine_type - 菜系类型
   * @param {string} params.budget_level - 预算水平
   * @returns {Promise<Object>} 菜谱规划结果
   */
  async generateMealPlan(params) {
    try {
      const response = await fetch(`${API_BASE_URL}/meal-plan/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || '菜谱生成失败');
      }

      return data;
    } catch (error) {
      console.error('生成菜谱失败:', error);
      throw error;
    }
  }

  /**
   * 获取菜谱规划偏好设置选项
   * @returns {Promise<Object>} 偏好设置选项
   */
  async getPreferences() {
    try {
      const response = await fetch(`${API_BASE_URL}/meal-plan/preferences`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || '获取偏好设置失败');
      }

      return data;
    } catch (error) {
      console.error('获取偏好设置失败:', error);
      throw error;
    }
  }

  /**
   * 测试菜谱规划API连接
   * @returns {Promise<Object>} 测试结果
   */
  async testConnection() {
    try {
      const response = await fetch(`${API_BASE_URL}/meal-plan/test`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'API连接测试失败');
      }

      return data;
    } catch (error) {
      console.error('API连接测试失败:', error);
      throw error;
    }
  }
}

export default new MealPlanApi();