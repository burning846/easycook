import React, { useState, useEffect } from 'react';
import { Typography, Row, Col, Card, Input, Select, Pagination, Spin, Empty, Tag, Space } from 'antd';
import { SearchOutlined, ClockCircleOutlined, FireOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import axios from 'axios';

const { Title } = Typography;
const { Meta } = Card;
const { Search } = Input;
const { Option } = Select;

function RecipePage() {
  const [loading, setLoading] = useState(true);
  const [recipes, setRecipes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  
  const difficulties = ['简单', '中等', '困难'];
  
  useEffect(() => {
    // 获取菜谱分类
    const fetchCategories = async () => {
      try {
        const response = await axios.get('/api/recipes/categories');
        setCategories(response.data);
      } catch (error) {
        console.error('获取菜谱分类失败:', error);
      }
    };
    
    fetchCategories();
  }, []);
  
  useEffect(() => {
    // 获取菜谱列表
    const fetchRecipes = async () => {
      try {
        setLoading(true);
        
        let url = '/api/recipes';
        let params = {
          page,
          per_page: pageSize
        };
        
        if (searchQuery) {
          url = '/api/recipes/search';
          params.q = searchQuery;
        }
        
        if (selectedCategory) {
          params.category = selectedCategory;
        }
        
        if (selectedDifficulty) {
          params.difficulty = selectedDifficulty;
        }
        
        const response = await axios.get(url, { params });
        setRecipes(response.data.items);
        setTotal(response.data.total);
      } catch (error) {
        console.error('获取菜谱列表失败:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRecipes();
  }, [page, pageSize, searchQuery, selectedCategory, selectedDifficulty]);
  
  const handleSearch = value => {
    setSearchQuery(value);
    setPage(1);
  };
  
  const handleCategoryChange = value => {
    setSelectedCategory(value);
    setPage(1);
  };
  
  const handleDifficultyChange = value => {
    setSelectedDifficulty(value);
    setPage(1);
  };
  
  const handlePageChange = (page, pageSize) => {
    setPage(page);
    setPageSize(pageSize);
  };
  
  return (
    <div>
      <Title level={2}>菜谱列表</Title>
      
      <div style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col xs={24} md={8}>
            <Search
              placeholder="搜索菜谱"
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              onSearch={handleSearch}
            />
          </Col>
          <Col xs={12} md={8}>
            <Select
              placeholder="选择分类"
              style={{ width: '100%' }}
              size="large"
              allowClear
              onChange={handleCategoryChange}
            >
              {categories.map(category => (
                <Option key={category} value={category}>{category}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={12} md={8}>
            <Select
              placeholder="选择难度"
              style={{ width: '100%' }}
              size="large"
              allowClear
              onChange={handleDifficultyChange}
            >
              {difficulties.map(difficulty => (
                <Option key={difficulty} value={difficulty}>{difficulty}</Option>
              ))}
            </Select>
          </Col>
        </Row>
      </div>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
        </div>
      ) : recipes.length > 0 ? (
        <>
          <Row gutter={[16, 16]}>
            {recipes.map(recipe => (
              <Col xs={24} sm={12} md={8} lg={6} key={recipe.id}>
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
                    title={<Link to={`/recipes/${recipe.id}`}>{recipe.name}</Link>} 
                    description={
                      <Space direction="vertical" size={4}>
                        <div>
                          <Tag color="blue">{recipe.category}</Tag>
                          <Tag color="orange">{recipe.difficulty}</Tag>
                        </div>
                        <div>
                          <ClockCircleOutlined /> {recipe.cooking_time || '?'}分钟
                          <span style={{ marginLeft: 8 }}>
                            <FireOutlined /> {recipe.servings || '?'}人份
                          </span>
                        </div>
                      </Space>
                    } 
                  />
                </Card>
              </Col>
            ))}
          </Row>
          
          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Pagination 
              current={page} 
              pageSize={pageSize} 
              total={total} 
              onChange={handlePageChange}
              showSizeChanger
              showQuickJumper
            />
          </div>
        </>
      ) : (
        <Empty description="暂无菜谱" />
      )}
    </div>
  );
}

export default RecipePage;