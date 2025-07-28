import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Typography, Spin } from 'antd';
import { userApi } from '../services/api';

const { Content } = Layout;
const { Title } = Typography;

const LoginSuccessPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const userId = params.get('user_id');
    
    if (!userId) {
      navigate('/login');
      return;
    }
    
    const fetchUserInfo = async () => {
      try {
        const response = await userApi.getUser(userId);
        const user = response.data;
        
        // 保存用户信息到本地存储
        localStorage.setItem('currentUser', JSON.stringify(user));
        
        // 延迟一下，让用户看到成功页面
        setTimeout(() => {
          navigate('/');
        }, 1500);
      } catch (error) {
        console.error('获取用户信息失败:', error);
        navigate('/login');
      }
    };
    
    fetchUserInfo();
  }, [location, navigate]);
  
  return (
    <Content style={{ padding: '50px 0' }}>
      <div style={{ textAlign: 'center', marginTop: 100 }}>
        <Spin size="large" />
        <Title level={2} style={{ marginTop: 24 }}>登录成功，正在跳转...</Title>
      </div>
    </Content>
  );
};

export default LoginSuccessPage;