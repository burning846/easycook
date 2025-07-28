import React, { useState, useEffect } from 'react';
import { Layout, Typography, Row, Col, Card, Button, Empty, message, Spin, Pagination } from 'antd';
import { HeartFilled, DeleteOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { userApi } from '../services/api';

const { Content } = Layout;
const { Title, Text } = Typography;
const { Meta } = Card;

const FavoritePage = () => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 12,
    total: 0
  });
  
  // 假设当前用户ID为1，实际应用中应该从登录状态或上下文中获取
  const userId = 1;
  
  const fetchFavorites = async (page = 1, pageSize = 12) => {
    setLoading(true);
    try {
      const response = await userApi.getFavorites(userId, {
        page: page,
        per_page: pageSize
      });
      
      setFavorites(response.data.items);
      setPagination({
        current: page,
        pageSize: pageSize,
        total: response.data.total
      });
    } catch (error) {
      console.error('获取收藏菜谱失败:', error);
      message.error('获取收藏菜谱失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchFavorites(pagination.current, pagination.pageSize);
  }, []);
  
  const handleRemoveFavorite = async (recipeId) => {
    try {
      await userApi.removeFavorite(userId, recipeId);
      message.success('已从收藏中移除');
      // 刷新收藏列表
      fetchFavorites(pagination.current, pagination.pageSize);
    } catch (error) {
      console.error('移除收藏失败:', error);
      message.error('移除收藏失败，请稍后重试');
    }
  };
  
  const handlePageChange = (page, pageSize) => {
    fetchFavorites(page, pageSize);
  };
  
  return (
    <Content style={{ padding: '0 50px', marginTop: 20 }}>
      <div className="site-layout-content" style={{ background: '#fff', padding: 24, minHeight: 280 }}>
        <Title level={2}>
          <HeartFilled style={{ color: '#ff4d4f', marginRight: 8 }} />
          我的收藏
        </Title>
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spin size="large" />
          </div>
        ) : favorites.length > 0 ? (
          <>
            <Row gutter={[16, 16]}>
              {favorites.map(favorite => {
                const recipe = favorite.recipe;
                if (!recipe) return null;
                
                return (
                  <Col xs={24} sm={12} md={8} lg={6} key={favorite.id}>
                    <Card
                      hoverable
                      cover={
                        <div style={{ height: 200, overflow: 'hidden' }}>
                          <img 
                            alt={recipe.name} 
                            src={recipe.image_url || 'https://via.placeholder.com/300x200?text=No+Image'} 
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          />
                        </div>
                      }
                      actions={[
                        <Button 
                          type="text" 
                          danger 
                          icon={<DeleteOutlined />} 
                          onClick={() => handleRemoveFavorite(recipe.id)}
                        >
                          取消收藏
                        </Button>
                      ]}
                    >
                      <Meta
                        title={
                          <Link to={`/recipes/${recipe.id}`}>{recipe.name}</Link>
                        }
                        description={
                          <>
                            <Text type="secondary">难度: {recipe.difficulty || '未知'}</Text>
                            <br />
                            <Text type="secondary">烹饪时间: {recipe.cooking_time || '未知'} 分钟</Text>
                          </>
                        }
                      />
                    </Card>
                  </Col>
                );
              })}
            </Row>
            
            <div style={{ textAlign: 'center', marginTop: 20 }}>
              <Pagination 
                current={pagination.current} 
                pageSize={pagination.pageSize} 
                total={pagination.total} 
                onChange={handlePageChange} 
                showSizeChanger={false}
              />
            </div>
          </>
        ) : (
          <Empty 
            description="暂无收藏的菜谱" 
            image={Empty.PRESENTED_IMAGE_SIMPLE} 
          />
        )}
      </div>
    </Content>
  );
};

export default FavoritePage;