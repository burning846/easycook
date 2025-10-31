import React from 'react';
import { Layout } from 'antd';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
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
    <AuthProvider>
      <Layout className="layout" style={{ minHeight: '100vh' }}>
        <AppHeader />
        <Content style={{ padding: '0 50px', marginTop: 64 }}>
          <div className="site-layout-content" style={{ padding: 24, minHeight: 380 }}>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/login-success" element={<LoginSuccessPage />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <HomePage />
                </ProtectedRoute>
              } />
              <Route path="/recipes" element={
                <ProtectedRoute>
                  <RecipePage />
                </ProtectedRoute>
              } />
              <Route path="/recipes/:id" element={
                <ProtectedRoute>
                  <RecipeDetailPage />
                </ProtectedRoute>
              } />
              <Route path="/ingredients" element={
                <ProtectedRoute>
                  <IngredientPage />
                </ProtectedRoute>
              } />
              <Route path="/shopping-list" element={
                <ProtectedRoute>
                  <ShoppingListPage />
                </ProtectedRoute>
              } />
              <Route path="/favorites" element={
                <ProtectedRoute>
                  <FavoritePage />
                </ProtectedRoute>
              } />
              <Route path="/data-management" element={
                <ProtectedRoute>
                  <DataManagementPage />
                </ProtectedRoute>
              } />
              <Route path="/meal-plan" element={
                <ProtectedRoute>
                  <MealPlanPage />
                </ProtectedRoute>
              } />
            </Routes>
          </div>
        </Content>
        <AppFooter />
      </Layout>
    </AuthProvider>
  );
}

export default App;