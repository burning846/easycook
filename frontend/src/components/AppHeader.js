import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, Avatar, Dropdown } from 'antd';
import { HomeOutlined, BookOutlined, ShoppingOutlined, UserOutlined, HeartOutlined, DatabaseOutlined, LoginOutlined, LogoutOutlined, CalendarOutlined } from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const { Header } = Layout;

function AppHeader() {
  const location = useLocation();
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);
  
  useEffect(() => {
    // 从本地存储获取用户信息
    const userJson = localStorage.getItem('currentUser');
    if (userJson) {
      try {
        const user = JSON.parse(userJson);
        setCurrentUser(user);
      } catch (e) {
        console.error('解析用户信息失败', e);
        localStorage.removeItem('currentUser');
      }
    }
  }, []);
  
  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    setCurrentUser(null);
    navigate('/');
  };
  
  const userMenuItems = [
    {
      key: 'favorites',
      label: <Link to="/favorites">我的收藏</Link>,
      icon: <HeartOutlined />
    },
    {
      key: 'logout',
      label: <span onClick={handleLogout}>退出登录</span>,
      icon: <LogoutOutlined />
    }
  ];
  
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/recipes',
      icon: <BookOutlined />,
      label: <Link to="/recipes">菜谱</Link>,
    },
    {
      key: '/ingredients',
      icon: <ShoppingOutlined />,
      label: <Link to="/ingredients">食材</Link>,
    },
    {
      key: '/shopping-list',
      icon: <ShoppingOutlined />,
      label: <Link to="/shopping-list">购物清单</Link>,
    },
    {
      key: '/meal-plan',
      icon: <CalendarOutlined />,
      label: <Link to="/meal-plan">菜谱规划</Link>,
    },
    {
      key: '/favorites',
      icon: <HeartOutlined />,
      label: <Link to="/favorites">我的收藏</Link>,
    },
    {
      key: '/data-management',
      icon: <DatabaseOutlined />,
      label: <Link to="/data-management">数据管理</Link>,
    },
  ];

  return (
    <Header style={{ position: 'fixed', zIndex: 1, width: '100%', display: 'flex', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div className="logo">EasyCook</div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ marginLeft: 20 }}
        />
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center' }}>
        {currentUser ? (
          <Dropdown 
            menu={{ items: userMenuItems }} 
            placement="bottomRight"
          >
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <Avatar icon={<UserOutlined />} style={{ marginRight: 8 }} />
              <span style={{ color: 'white' }}>{currentUser.username}</span>
            </div>
          </Dropdown>
        ) : (
          <Button 
            type="primary" 
            icon={<LoginOutlined />} 
            onClick={() => navigate('/login')}
          >
            登录
          </Button>
        )}
      </div>
    </Header>
  );
}

export default AppHeader;