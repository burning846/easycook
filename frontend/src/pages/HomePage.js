import React, { useState, useEffect } from 'react';
import { Typography, Row, Col, Card, Button, Spin, Empty } from 'antd';
import { Link } from 'react-router-dom';
import { recipeApi } from '../services/api';

const { Title, Paragraph } = Typography;
const { Meta } = Card;

function HomePage() {
  const [loading, setLoading] = useState(true);
  const [featuredRecipes, setFeaturedRecipes] = useState([]);
  
  useEffect(() => {
    // 获取推荐菜谱
    const fetchFeaturedRecipes = async () => {
      try {
        setLoading(true);
        const response = await recipeApi.getRecipes({ per_page: 6 });
        setFeaturedRecipes(response.items || []);
      } catch (error) {
        console.error('获取推荐菜谱失败:', error);
        setFeaturedRecipes([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchFeaturedRecipes();
  }, []);
  
  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <Title>欢迎使用 EasyCook</Title>
        <Paragraph style={{ fontSize: 18 }}>
          EasyCook 是您的私人厨房助手，帮助您发现美食、规划菜单、管理食材。
        </Paragraph>
        <div style={{ margin: '24px 0' }}>
          <Button type="primary" size="large">
            <Link to="/recipes">浏览菜谱</Link>
          </Button>
          <Button size="large" style={{ marginLeft: 16 }}>
            <Link to="/shopping-list">我的购物清单</Link>
          </Button>
        </div>
      </div>
      
      <div>
        <Title level={2} style={{ marginBottom: 24 }}>推荐菜谱</Title>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
          </div>
        ) : featuredRecipes.length > 0 ? (
          <Row gutter={[16, 16]}>
            {featuredRecipes.map(recipe => (
              <Col xs={24} sm={12} md={8} key={recipe.id}>
                <Card
                  hoverable
                  className="recipe-card"
                  cover={
                    <img 
                      alt={recipe.name} 
                      src={recipe.image_url || 'https://via.placeholder.com/300x200?text=暂无图片'} 
                    />
                  }
                >
                  <Meta 
                    title={recipe.name} 
                    description={`${recipe.difficulty || '未知难度'} · ${recipe.cooking_time || '?'}分钟`} 
                  />
                  <div style={{ marginTop: 16 }}>
                    <Button type="primary" block>
                      <Link to={`/recipes/${recipe.id}`}>查看详情</Link>
                    </Button>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        ) : (
          <Empty description="暂无推荐菜谱" />
        )}
      </div>
      
      <div style={{ marginTop: 48 }}>
        <Title level={2}>EasyCook 功能</Title>
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          <Col xs={24} md={8}>
            <Card title="菜谱推荐" bordered={false}>
              <p>浏览丰富的菜谱库，按照分类、难度、烹饪时间等筛选，找到适合您的美食。</p>
              <Button type="link">
                <Link to="/recipes">浏览菜谱</Link>
              </Button>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card title="备料管理" bordered={false}>
              <p>管理您的食材库存，根据选择的菜谱自动生成购物清单，轻松备齐所需食材。</p>
              <Button type="link">
                <Link to="/ingredients">管理食材</Link>
              </Button>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card title="健康饮食" bordered={false}>
              <p>根据您的口味偏好、饮食禁忌和特殊要求，为您推荐健康均衡的菜谱组合。</p>
              <Button type="link">
                <Link to="/recipes">探索更多</Link>
              </Button>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}

export default HomePage;