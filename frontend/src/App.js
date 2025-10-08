import React from 'react';
import { Layout } from 'antd';
import { Routes, Route } from 'react-router-dom';
import AppHeader from './components/AppHeader';
import AppFooter from './components/AppFooter';
import HomePage from './pages/HomePage';
import RecipePage from './pages/RecipePage';
import RecipeDetailPage from './pages/RecipeDetailPage';
import IngredientPage from './pages/IngredientPage';
import ShoppingListPage from './pages/ShoppingListPage';
import FavoritePage from './pages/FavoritePage';
import DataManagementPage from './pages/DataManagementPage';
import MealPlanPage from './pages/MealPlanPage';
import LoginPage from './pages/LoginPage';
import LoginSuccessPage from './pages/LoginSuccessPage';

const { Content } = Layout;

function App() {
  return (
    <Layout className="layout" style={{ minHeight: '100vh' }}>
      <AppHeader />
      <Content style={{ padding: '0 50px', marginTop: 64 }}>
        <div className="site-layout-content" style={{ padding: 24, minHeight: 380 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/recipes" element={<RecipePage />} />
            <Route path="/recipes/:id" element={<RecipeDetailPage />} />
            <Route path="/ingredients" element={<IngredientPage />} />
            <Route path="/shopping-list" element={<ShoppingListPage />} />
            <Route path="/favorites" element={<FavoritePage />} />
            <Route path="/data-management" element={<DataManagementPage />} />
            <Route path="/meal-plan" element={<MealPlanPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/login-success" element={<LoginSuccessPage />} />
          </Routes>
        </div>
      </Content>
      <AppFooter />
    </Layout>
  );
}

export default App;