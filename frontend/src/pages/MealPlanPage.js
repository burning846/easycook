import React, { useState, useEffect } from 'react';
import mealPlanApi from '../services/mealPlanApi';
import MealPlanForm from '../components/MealPlanForm';
import MealPlanResult from '../components/MealPlanResult';
import '../styles/MealPlanPage.css';

const MealPlanPage = () => {
  const [preferences, setPreferences] = useState(null);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await mealPlanApi.getPreferences();
      if (response.success) {
        setPreferences(response.data);
      }
    } catch (error) {
      console.error('加载偏好设置失败:', error);
      setError('加载偏好设置失败，请刷新页面重试');
    }
  };

  const handleGenerateMealPlan = async (formData) => {
    setLoading(true);
    setError(null);
    setMealPlan(null);

    try {
      const response = await mealPlanApi.generateMealPlan(formData);
      if (response.success) {
        setMealPlan(response.data);
      } else {
        setError(response.message || '菜谱生成失败');
      }
    } catch (error) {
      console.error('生成菜谱失败:', error);
      setError(error.message || '菜谱生成失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setMealPlan(null);
    setError(null);
  };

  return (
    <div className="meal-plan-page">
      <div className="container">
        <header className="page-header">
          <h1>AI智能菜谱规划</h1>
          <p>让AI为您定制专属的营养菜谱，轻松规划每日三餐</p>
        </header>

        {error && (
          <div className="error-message">
            <i className="error-icon">⚠️</i>
            <span>{error}</span>
            <button onClick={() => setError(null)} className="close-btn">×</button>
          </div>
        )}

        <div className="meal-plan-content">
          {!mealPlan ? (
            <div className="form-section">
              <MealPlanForm
                preferences={preferences}
                onSubmit={handleGenerateMealPlan}
                loading={loading}
              />
            </div>
          ) : (
            <div className="result-section">
              <MealPlanResult
                mealPlan={mealPlan}
                onReset={handleReset}
                onRegenerate={handleGenerateMealPlan}
              />
            </div>
          )}
        </div>

        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>AI正在为您生成专属菜谱...</p>
              <small>这可能需要几秒钟时间</small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MealPlanPage;