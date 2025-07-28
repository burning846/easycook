import React, { useState, useEffect } from 'react';
import { Layout, Typography, Form, Input, Button, Divider, message, Card, Row, Col } from 'antd';
import { UserOutlined, LockOutlined, GoogleOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { userApi } from '../services/api';

const { Content } = Layout;
const { Title, Text } = Typography;

const LoginPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // 检查URL参数中是否有用户ID（Google登录回调）
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const userId = params.get('user_id');
    
    if (userId) {
      // 从后端获取用户信息
      const fetchUserInfo = async () => {
        try {
          const response = await userApi.getUser(userId);
          const user = response.data;
          
          // 保存用户信息到本地存储
          localStorage.setItem('currentUser', JSON.stringify(user));
          
          message.success(`欢迎回来，${user.username}！`);
          navigate('/');
        } catch (error) {
          console.error('获取用户信息失败:', error);
          message.error('登录失败，请重试');
        }
      };
      
      fetchUserInfo();
    }
  }, [location, navigate]);
  
  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      // 这里应该有实际的登录API调用
      // 简化起见，我们假设用户名为"test"，密码为"password"的用户可以登录
      if (values.username === 'test' && values.password === 'password') {
        // 模拟获取用户信息
        const user = {
          id: 1,
          username: 'test',
          email: 'test@example.com'
        };
        
        // 保存用户信息到本地存储
        localStorage.setItem('currentUser', JSON.stringify(user));
        
        message.success(`欢迎回来，${user.username}！`);
        navigate('/');
      } else {
        message.error('用户名或密码错误');
      }
    } catch (error) {
      console.error('登录失败:', error);
      message.error('登录失败，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  const handleGoogleLogin = () => {
    // 重定向到后端的Google登录路由
    window.location.href = '/api/auth/google';
  };
  
  const handleRegister = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      
      // 创建新用户
      const response = await userApi.createUser({
        username: values.username,
        email: values.username + '@example.com', // 简化处理
        password: values.password
      });
      
      const user = response.data;
      
      // 保存用户信息到本地存储
      localStorage.setItem('currentUser', JSON.stringify(user));
      
      message.success('注册成功！');
      navigate('/');
    } catch (error) {
      if (error.errorFields) {
        // 表单验证错误
        return;
      }
      console.error('注册失败:', error);
      message.error('注册失败，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Content style={{ padding: '50px 0' }}>
      <Row justify="center" align="middle">
        <Col xs={22} sm={16} md={12} lg={8}>
          <Card>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Title level={2}>EasyCook</Title>
              <Text type="secondary">登录您的帮助做饭小程序账号</Text>
            </div>
            
            <Form
              form={form}
              name="login"
              onFinish={handleSubmit}
              layout="vertical"
            >
              <Form.Item
                name="username"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input prefix={<UserOutlined />} placeholder="用户名" size="large" />
              </Form.Item>
              
              <Form.Item
                name="password"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input.Password prefix={<LockOutlined />} placeholder="密码" size="large" />
              </Form.Item>
              
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} block size="large">
                  登录
                </Button>
              </Form.Item>
              
              <Form.Item>
                <Button type="default" onClick={handleRegister} loading={loading} block size="large">
                  注册新账号
                </Button>
              </Form.Item>
              
              <Divider>或</Divider>
              
              <Button 
                icon={<GoogleOutlined />} 
                onClick={handleGoogleLogin} 
                block 
                size="large"
                style={{ backgroundColor: '#4285F4', color: 'white' }}
              >
                使用Google账号登录
              </Button>
            </Form>
          </Card>
        </Col>
      </Row>
    </Content>
  );
};

export default LoginPage;