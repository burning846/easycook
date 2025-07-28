import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Divider, Row, Col, Card, Steps, Tag, Button, Image, Spin, message, List } from 'antd';
import { ClockCircleOutlined, FireOutlined, ShoppingOutlined, ArrowLeftOutlined, HeartOutlined, HeartFilled } from '@ant-design/icons';
import { recipeApi, userApi } from '../services/api';

const { Title, Paragraph } = Typography;
const { Step } = Steps;

function RecipeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recipe, setRecipe] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);
  
  useEffect(() => {
    // 获取菜谱详情
    const fetchRecipeDetail = async () => {
      try {
        setLoading(true);
        const response = await recipeApi.getRecipe(id);
        setRecipe(response.data);
      } catch (error) {
        console.error('获取菜谱详情失败:', error);
        message.error('获取菜谱详情失败');
      } finally {
        setLoading(false);
      }
    };
    
    // 检查是否已收藏
    const checkFavorite = async () => {
      try {
        // 这里应该有用户登录逻辑，暂时使用固定用户ID
        const userId = 1;
        const response = await userApi.checkFavorite(userId, id);
        setIsFavorite(response.data.is_favorite);
      } catch (error) {
        console.error('检查收藏状态失败:', error);
      }
    };
    
    fetchRecipeDetail();
    checkFavorite();
  }, [id]);
  
  const addToShoppingList = async () => {
    try {
      // 这里应该有用户登录逻辑，暂时使用固定用户ID
      const userId = 1;
      
      // 创建购物清单
      const response = await userApi.createShoppingList(userId, {
        name: `${recipe.name}的食材`,
        items: recipe.ingredients.map(ingredient => ({
          ingredient_id: ingredient.ingredient_id,
          ingredient_name: ingredient.ingredient_name,
          amount: ingredient.amount,
          unit: ingredient.unit
        }))
      });
      
      message.success('已添加到购物清单');
      navigate('/shopping-list');
    } catch (error) {
      console.error('添加到购物清单失败:', error);
      message.error('添加到购物清单失败');
    }
  };
  
  const toggleFavorite = async () => {
    try {
      setFavoriteLoading(true);
      // 这里应该有用户登录逻辑，暂时使用固定用户ID
      const userId = 1;
      
      if (isFavorite) {
        // 取消收藏
        await userApi.removeFavorite(userId, id);
        message.success('已取消收藏');
        setIsFavorite(false);
      } else {
        // 添加收藏
        await userApi.addFavorite(userId, id);
        message.success('已添加到收藏');
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('操作收藏失败:', error);
      message.error('操作收藏失败，请稍后重试');
    } finally {
      setFavoriteLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <Spin size="large" />
      </div>
    );
  }
  
  if (!recipe) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <Title level={3}>菜谱不存在</Title>
        <Button type="primary" onClick={() => navigate('/recipes')}>
          <ArrowLeftOutlined /> 返回菜谱列表
        </Button>
      </div>
    );
  }
  
  // 对步骤进行排序
  const sortedSteps = [...(recipe.steps || [])].sort((a, b) => a.step_number - b.step_number);
  
  return (
    <div>
      <Button 
        type="link" 
        icon={<ArrowLeftOutlined />} 
        onClick={() => navigate('/recipes')}
        style={{ marginBottom: 16, padding: 0 }}
      >
        返回菜谱列表
      </Button>
      
      <Row gutter={[24, 24]}>
        <Col xs={24} md={16}>
          <div>
            <Title>{recipe.name}</Title>
            <div style={{ marginBottom: 16 }}>
              <Tag color="blue">{recipe.category}</Tag>
              <Tag color="orange">{recipe.difficulty}</Tag>
              <Tag icon={<ClockCircleOutlined />}>{recipe.cooking_time || '?'}分钟</Tag>
              <Tag icon={<FireOutlined />}>{recipe.servings || '?'}人份</Tag>
              <Button 
                type="text"
                icon={isFavorite ? <HeartFilled style={{ color: '#ff4d4f' }} /> : <HeartOutlined />}
                loading={favoriteLoading}
                onClick={toggleFavorite}
                style={{ marginLeft: 8 }}
              >
                {isFavorite ? '已收藏' : '收藏'}
              </Button>
            </div>
            <Paragraph>{recipe.description}</Paragraph>
          </div>
          
          <Divider orientation="left">烹饪步骤</Divider>
          
          <div className="recipe-steps-container">
            <Steps 
              direction="vertical" 
              current={currentStep}
              onChange={setCurrentStep}
              items={sortedSteps.map((step, index) => ({
                title: `步骤 ${index + 1}`,
                description: (
                  <div className="recipe-step">
                    <Paragraph>{step.description}</Paragraph>
                    {step.image_url && (
                      <Image 
                        src={step.image_url} 
                        alt={`步骤 ${index + 1}`} 
                        className="recipe-step-image"
                      />
                    )}
                  </div>
                )
              }))}
            />
          </div>
        </Col>
        
        <Col xs={24} md={8}>
          <Card title="食材清单" extra={<Button type="primary" icon={<ShoppingOutlined />} onClick={addToShoppingList}>添加到购物清单</Button>}>
            <List
              dataSource={recipe.ingredients || []}
              renderItem={item => (
                <List.Item>
                  <div>
                    <span style={{ fontWeight: 'bold' }}>{item.ingredient_name}</span>
                    <span style={{ marginLeft: 8 }}>{item.amount} {item.unit}</span>
                    {item.note && <div style={{ color: '#999' }}>{item.note}</div>}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default RecipeDetailPage;