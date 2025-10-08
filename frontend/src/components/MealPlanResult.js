import React, { useState } from 'react';
import '../styles/MealPlanResult.css';

const MealPlanResult = ({ mealPlan, onReset, onRegenerate }) => {
  const [activeTab, setActiveTab] = useState('plan');
  const [expandedDay, setExpandedDay] = useState(null);

  const toggleDay = (dayKey) => {
    setExpandedDay(expandedDay === dayKey ? null : dayKey);
  };

  const renderMealPlan = () => {
    if (mealPlan.format === 'text') {
      return (
        <div className="text-format-plan">
          <pre>{mealPlan.meal_plan}</pre>
        </div>
      );
    }

    const planData = mealPlan.meal_plan || mealPlan;
    const days = Object.keys(planData).filter(key => key.startsWith('day_'));

    return (
      <div className="meal-plan-grid">
        {days.map(dayKey => {
          const dayData = planData[dayKey];
          const isExpanded = expandedDay === dayKey;
          
          return (
            <div key={dayKey} className={`day-card ${isExpanded ? 'expanded' : ''}`}>
              <div className="day-header" onClick={() => toggleDay(dayKey)}>
                <h3>{dayData.date || dayKey.replace('_', ' ')}</h3>
                <span className="expand-icon">{isExpanded ? '−' : '+'}</span>
              </div>
              
              {isExpanded && (
                <div className="day-content">
                  {['breakfast', 'lunch', 'dinner'].map(mealType => {
                    const meal = dayData[mealType];
                    if (!meal) return null;
                    
                    const mealNames = {
                      breakfast: '早餐',
                      lunch: '午餐', 
                      dinner: '晚餐'
                    };
                    
                    return (
                      <div key={mealType} className="meal-item">
                        <h4 className="meal-type">{mealNames[mealType]}</h4>
                        <div className="meal-details">
                          <h5 className="dish-name">{meal.name}</h5>
                          
                          {meal.ingredients && (
                            <div className="ingredients">
                              <span className="label">食材：</span>
                              <span className="value">{meal.ingredients.join('、')}</span>
                            </div>
                          )}
                          
                          <div className="meal-meta">
                            {meal.cooking_time && (
                              <span className="meta-item">
                                <i className="icon">⏱️</i>
                                {meal.cooking_time}
                              </span>
                            )}
                            {meal.difficulty && (
                              <span className="meta-item">
                                <i className="icon">📊</i>
                                {meal.difficulty}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  const renderShoppingList = () => {
    const shoppingList = mealPlan.shopping_list || [];
    
    if (shoppingList.length === 0) {
      return <p className="no-data">暂无购物清单数据</p>;
    }

    return (
      <div className="shopping-list">
        <div className="list-grid">
          {shoppingList.map((item, index) => (
            <div key={index} className="shopping-item">
              <span className="item-icon">🛒</span>
              <span className="item-name">{item}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTips = () => {
    const nutritionTips = mealPlan.nutrition_tips || [];
    const cookingTips = mealPlan.cooking_tips || [];

    return (
      <div className="tips-section">
        {nutritionTips.length > 0 && (
          <div className="tip-group">
            <h4>🥗 营养建议</h4>
            <ul>
              {nutritionTips.map((tip, index) => (
                <li key={index}>{tip}</li>
              ))}
            </ul>
          </div>
        )}
        
        {cookingTips.length > 0 && (
          <div className="tip-group">
            <h4>👨‍🍳 烹饪小贴士</h4>
            <ul>
              {cookingTips.map((tip, index) => (
                <li key={index}>{tip}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="meal-plan-result">
      <div className="result-header">
        <h2>您的专属菜谱规划</h2>
        <div className="header-actions">
          <button onClick={onReset} className="btn-secondary">
            重新规划
          </button>
          <button onClick={() => window.print()} className="btn-secondary">
            打印菜谱
          </button>
        </div>
      </div>

      <div className="result-tabs">
        <button
          className={`tab-btn ${activeTab === 'plan' ? 'active' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          📅 菜谱规划
        </button>
        <button
          className={`tab-btn ${activeTab === 'shopping' ? 'active' : ''}`}
          onClick={() => setActiveTab('shopping')}
        >
          🛒 购物清单
        </button>
        <button
          className={`tab-btn ${activeTab === 'tips' ? 'active' : ''}`}
          onClick={() => setActiveTab('tips')}
        >
          💡 贴心建议
        </button>
      </div>

      <div className="result-content">
        {activeTab === 'plan' && renderMealPlan()}
        {activeTab === 'shopping' && renderShoppingList()}
        {activeTab === 'tips' && renderTips()}
      </div>

      <div className="result-footer">
        <p className="ai-note">
          <span className="ai-icon">🤖</span>
          此菜谱由AI智能生成，建议根据个人口味和实际情况进行调整
        </p>
      </div>
    </div>
  );
};

export default MealPlanResult;