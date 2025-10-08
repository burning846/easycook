import React, { useState } from 'react';
import '../styles/MealPlanForm.css';

const MealPlanForm = ({ preferences, onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    days: 7,
    dietary_preferences: [],
    allergies: [],
    cuisine_type: '',
    budget_level: 'medium'
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMultiSelectChange = (field, value, checked) => {
    setFormData(prev => ({
      ...prev,
      [field]: checked
        ? [...prev[field], value]
        : prev[field].filter(item => item !== value)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  if (!preferences) {
    return (
      <div className="form-loading">
        <div className="spinner"></div>
        <p>加载配置选项中...</p>
      </div>
    );
  }

  return (
    <form className="meal-plan-form" onSubmit={handleSubmit}>
      <div className="form-section">
        <h3>基本设置</h3>
        
        <div className="form-group">
          <label htmlFor="days">规划天数</label>
          <select
            id="days"
            value={formData.days}
            onChange={(e) => handleInputChange('days', parseInt(e.target.value))}
            required
          >
            {[1, 2, 3, 4, 5, 6, 7, 10, 14].map(day => (
              <option key={day} value={day}>{day}天</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="budget_level">预算水平</label>
          <select
            id="budget_level"
            value={formData.budget_level}
            onChange={(e) => handleInputChange('budget_level', e.target.value)}
          >
            {preferences.budget_levels.map(level => (
              <option key={level.value} value={level.value}>
                {level.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="cuisine_type">菜系偏好（可选）</label>
          <select
            id="cuisine_type"
            value={formData.cuisine_type}
            onChange={(e) => handleInputChange('cuisine_type', e.target.value)}
          >
            <option value="">不限制</option>
            {preferences.cuisine_types.map(cuisine => (
              <option key={cuisine.value} value={cuisine.value}>
                {cuisine.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-section">
        <h3>饮食偏好</h3>
        <div className="checkbox-group">
          {preferences.dietary_preferences.map(pref => (
            <label key={pref.value} className="checkbox-item">
              <input
                type="checkbox"
                checked={formData.dietary_preferences.includes(pref.value)}
                onChange={(e) => handleMultiSelectChange('dietary_preferences', pref.value, e.target.checked)}
              />
              <span className="checkmark"></span>
              {pref.label}
            </label>
          ))}
        </div>
      </div>

      <div className="form-section">
        <h3>过敏禁忌</h3>
        <div className="checkbox-group">
          {preferences.common_allergies.map(allergy => (
            <label key={allergy.value} className="checkbox-item">
              <input
                type="checkbox"
                checked={formData.allergies.includes(allergy.value)}
                onChange={(e) => handleMultiSelectChange('allergies', allergy.value, e.target.checked)}
              />
              <span className="checkmark"></span>
              {allergy.label}
            </label>
          ))}
        </div>
      </div>

      <div className="form-actions">
        <button
          type="submit"
          className="generate-btn"
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="btn-spinner"></div>
              生成中...
            </>
          ) : (
            <>
              <span className="btn-icon">🤖</span>
              生成AI菜谱
            </>
          )}
        </button>
      </div>

      <div className="form-tips">
        <h4>💡 小贴士</h4>
        <ul>
          <li>选择合适的天数，建议从3-7天开始</li>
          <li>如有特殊饮食需求，请勾选相应的偏好选项</li>
          <li>过敏信息很重要，请如实填写</li>
          <li>AI会根据您的选择生成营养均衡的菜谱</li>
        </ul>
      </div>
    </form>
  );
};

export default MealPlanForm;