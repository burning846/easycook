import React, { useState, useEffect } from 'react';
import { Layout, Typography, Tabs, Form, Input, Button, Select, InputNumber, Upload, message, Table, Space, Modal } from 'antd';
import { PlusOutlined, UploadOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { recipeApi, ingredientApi } from '../services/api';

const { Content } = Layout;
const { Title } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

const DataManagementPage = () => {
  // 食材相关状态
  const [ingredients, setIngredients] = useState([]);
  const [ingredientCategories, setIngredientCategories] = useState([]);
  const [ingredientLoading, setIngredientLoading] = useState(false);
  const [ingredientForm] = Form.useForm();
  const [editingIngredient, setEditingIngredient] = useState(null);
  
  // 菜谱相关状态
  const [recipes, setRecipes] = useState([]);
  const [recipeCategories, setRecipeCategories] = useState([]);
  const [recipeLoading, setRecipeLoading] = useState(false);
  const [recipeForm] = Form.useForm();
  const [editingRecipe, setEditingRecipe] = useState(null);
  const [recipeSteps, setRecipeSteps] = useState([]);
  const [recipeIngredients, setRecipeIngredients] = useState([]);
  
  // 模态框状态
  const [ingredientModalVisible, setIngredientModalVisible] = useState(false);
  const [recipeModalVisible, setRecipeModalVisible] = useState(false);
  
  // 获取食材列表
  const fetchIngredients = async () => {
    setIngredientLoading(true);
    try {
      const response = await ingredientApi.getIngredients();
      setIngredients(response.data.items);
    } catch (error) {
      console.error('获取食材列表失败:', error);
      message.error('获取食材列表失败');
    } finally {
      setIngredientLoading(false);
    }
  };
  
  // 获取食材分类
  const fetchIngredientCategories = async () => {
    try {
      const response = await ingredientApi.getCategories();
      setIngredientCategories(response.data);
    } catch (error) {
      console.error('获取食材分类失败:', error);
    }
  };
  
  // 获取菜谱列表
  const fetchRecipes = async () => {
    setRecipeLoading(true);
    try {
      const response = await recipeApi.getRecipes();
      setRecipes(response.data.items);
    } catch (error) {
      console.error('获取菜谱列表失败:', error);
      message.error('获取菜谱列表失败');
    } finally {
      setRecipeLoading(false);
    }
  };
  
  // 获取菜谱分类
  const fetchRecipeCategories = async () => {
    try {
      const response = await recipeApi.getCategories();
      setRecipeCategories(response.data);
    } catch (error) {
      console.error('获取菜谱分类失败:', error);
    }
  };
  
  useEffect(() => {
    fetchIngredients();
    fetchIngredientCategories();
    fetchRecipes();
    fetchRecipeCategories();
  }, []);
  
  // 添加或更新食材
  const handleIngredientSubmit = async (values) => {
    try {
      if (editingIngredient) {
        // 更新食材
        await ingredientApi.updateIngredient(editingIngredient.id, values);
        message.success('食材更新成功');
      } else {
        // 添加食材
        await ingredientApi.createIngredient(values);
        message.success('食材添加成功');
      }
      setIngredientModalVisible(false);
      ingredientForm.resetFields();
      setEditingIngredient(null);
      fetchIngredients();
    } catch (error) {
      console.error('操作食材失败:', error);
      message.error('操作失败，请稍后重试');
    }
  };
  
  // 删除食材
  const handleDeleteIngredient = async (id) => {
    try {
      await ingredientApi.deleteIngredient(id);
      message.success('食材删除成功');
      fetchIngredients();
    } catch (error) {
      console.error('删除食材失败:', error);
      message.error('删除失败，请稍后重试');
    }
  };
  
  // 编辑食材
  const handleEditIngredient = (record) => {
    setEditingIngredient(record);
    ingredientForm.setFieldsValue({
      name: record.name,
      category: record.category,
      description: record.description,
      unit: record.unit,
      image_url: record.image_url
    });
    setIngredientModalVisible(true);
  };
  
  // 添加步骤
  const addStep = () => {
    const newStep = {
      step_number: recipeSteps.length + 1,
      description: '',
      image_url: ''
    };
    setRecipeSteps([...recipeSteps, newStep]);
  };
  
  // 更新步骤
  const updateStep = (index, field, value) => {
    const newSteps = [...recipeSteps];
    newSteps[index][field] = value;
    setRecipeSteps(newSteps);
  };
  
  // 删除步骤
  const removeStep = (index) => {
    const newSteps = [...recipeSteps];
    newSteps.splice(index, 1);
    // 重新编号
    newSteps.forEach((step, i) => {
      step.step_number = i + 1;
    });
    setRecipeSteps(newSteps);
  };
  
  // 添加食材
  const addIngredient = () => {
    const newIngredient = {
      ingredient_id: null,
      ingredient_name: '',
      amount: 0,
      unit: '',
      note: ''
    };
    setRecipeIngredients([...recipeIngredients, newIngredient]);
  };
  
  // 更新食材
  const updateIngredient = (index, field, value) => {
    const newIngredients = [...recipeIngredients];
    newIngredients[index][field] = value;
    
    // 如果选择了食材ID，自动填充名称和单位
    if (field === 'ingredient_id' && value) {
      const selectedIngredient = ingredients.find(ing => ing.id === value);
      if (selectedIngredient) {
        newIngredients[index].ingredient_name = selectedIngredient.name;
        newIngredients[index].unit = selectedIngredient.unit;
      }
    }
    
    setRecipeIngredients(newIngredients);
  };
  
  // 删除食材
  const removeIngredient = (index) => {
    const newIngredients = [...recipeIngredients];
    newIngredients.splice(index, 1);
    setRecipeIngredients(newIngredients);
  };
  
  // 添加或更新菜谱
  const handleRecipeSubmit = async (values) => {
    try {
      const recipeData = {
        ...values,
        steps: recipeSteps,
        ingredients: recipeIngredients
      };
      
      if (editingRecipe) {
        // 更新菜谱
        await recipeApi.updateRecipe(editingRecipe.id, recipeData);
        message.success('菜谱更新成功');
      } else {
        // 添加菜谱
        await recipeApi.createRecipe(recipeData);
        message.success('菜谱添加成功');
      }
      
      setRecipeModalVisible(false);
      recipeForm.resetFields();
      setEditingRecipe(null);
      setRecipeSteps([]);
      setRecipeIngredients([]);
      fetchRecipes();
    } catch (error) {
      console.error('操作菜谱失败:', error);
      message.error('操作失败，请稍后重试');
    }
  };
  
  // 删除菜谱
  const handleDeleteRecipe = async (id) => {
    try {
      await recipeApi.deleteRecipe(id);
      message.success('菜谱删除成功');
      fetchRecipes();
    } catch (error) {
      console.error('删除菜谱失败:', error);
      message.error('删除失败，请稍后重试');
    }
  };
  
  // 编辑菜谱
  const handleEditRecipe = async (record) => {
    try {
      setEditingRecipe(record);
      
      // 获取菜谱详情
      const response = await recipeApi.getRecipe(record.id);
      const recipeDetail = response.data;
      
      recipeForm.setFieldsValue({
        name: recipeDetail.name,
        category: recipeDetail.category,
        description: recipeDetail.description,
        difficulty: recipeDetail.difficulty,
        cooking_time: recipeDetail.cooking_time,
        servings: recipeDetail.servings,
        image_url: recipeDetail.image_url
      });
      
      setRecipeSteps(recipeDetail.steps || []);
      setRecipeIngredients(recipeDetail.ingredients || []);
      setRecipeModalVisible(true);
    } catch (error) {
      console.error('获取菜谱详情失败:', error);
      message.error('获取菜谱详情失败');
    }
  };
  
  // 食材表格列定义
  const ingredientColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            type="text" 
            icon={<EditOutlined />} 
            onClick={() => handleEditIngredient(record)}
          >
            编辑
          </Button>
          <Button 
            type="text" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDeleteIngredient(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];
  
  // 菜谱表格列定义
  const recipeColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
    },
    {
      title: '烹饪时间',
      dataIndex: 'cooking_time',
      key: 'cooking_time',
      render: (text) => text ? `${text}分钟` : '-'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            type="text" 
            icon={<EditOutlined />} 
            onClick={() => handleEditRecipe(record)}
          >
            编辑
          </Button>
          <Button 
            type="text" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDeleteRecipe(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];
  
  return (
    <Content style={{ padding: '0 50px', marginTop: 20 }}>
      <div className="site-layout-content" style={{ background: '#fff', padding: 24, minHeight: 280 }}>
        <Title level={2}>数据管理</Title>
        
        <Tabs defaultActiveKey="1">
          <TabPane tab="食材管理" key="1">
            <div style={{ marginBottom: 16 }}>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={() => {
                  setEditingIngredient(null);
                  ingredientForm.resetFields();
                  setIngredientModalVisible(true);
                }}
              >
                添加食材
              </Button>
            </div>
            
            <Table 
              columns={ingredientColumns} 
              dataSource={ingredients} 
              rowKey="id" 
              loading={ingredientLoading}
              pagination={{ pageSize: 10 }}
            />
            
            <Modal
              title={editingIngredient ? '编辑食材' : '添加食材'}
              visible={ingredientModalVisible}
              onCancel={() => setIngredientModalVisible(false)}
              footer={null}
            >
              <Form
                form={ingredientForm}
                layout="vertical"
                onFinish={handleIngredientSubmit}
              >
                <Form.Item
                  name="name"
                  label="食材名称"
                  rules={[{ required: true, message: '请输入食材名称' }]}
                >
                  <Input placeholder="请输入食材名称" />
                </Form.Item>
                
                <Form.Item
                  name="category"
                  label="分类"
                  rules={[{ required: true, message: '请选择分类' }]}
                >
                  <Select placeholder="请选择分类">
                    {ingredientCategories.map(category => (
                      <Option key={category} value={category}>{category}</Option>
                    ))}
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="unit"
                  label="单位"
                  rules={[{ required: true, message: '请输入单位' }]}
                >
                  <Input placeholder="请输入单位，如克、个等" />
                </Form.Item>
                
                <Form.Item
                  name="description"
                  label="描述"
                >
                  <TextArea rows={4} placeholder="请输入食材描述" />
                </Form.Item>
                
                <Form.Item
                  name="image_url"
                  label="图片URL"
                >
                  <Input placeholder="请输入图片URL" />
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit">
                    {editingIngredient ? '更新' : '添加'}
                  </Button>
                  <Button 
                    style={{ marginLeft: 8 }} 
                    onClick={() => setIngredientModalVisible(false)}
                  >
                    取消
                  </Button>
                </Form.Item>
              </Form>
            </Modal>
          </TabPane>
          
          <TabPane tab="菜谱管理" key="2">
            <div style={{ marginBottom: 16 }}>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={() => {
                  setEditingRecipe(null);
                  recipeForm.resetFields();
                  setRecipeSteps([]);
                  setRecipeIngredients([]);
                  setRecipeModalVisible(true);
                }}
              >
                添加菜谱
              </Button>
            </div>
            
            <Table 
              columns={recipeColumns} 
              dataSource={recipes} 
              rowKey="id" 
              loading={recipeLoading}
              pagination={{ pageSize: 10 }}
            />
            
            <Modal
              title={editingRecipe ? '编辑菜谱' : '添加菜谱'}
              visible={recipeModalVisible}
              onCancel={() => setRecipeModalVisible(false)}
              footer={null}
              width={800}
            >
              <Form
                form={recipeForm}
                layout="vertical"
                onFinish={handleRecipeSubmit}
              >
                <Form.Item
                  name="name"
                  label="菜谱名称"
                  rules={[{ required: true, message: '请输入菜谱名称' }]}
                >
                  <Input placeholder="请输入菜谱名称" />
                </Form.Item>
                
                <Form.Item
                  name="category"
                  label="分类"
                  rules={[{ required: true, message: '请选择分类' }]}
                >
                  <Select placeholder="请选择分类">
                    {recipeCategories.map(category => (
                      <Option key={category} value={category}>{category}</Option>
                    ))}
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="description"
                  label="描述"
                >
                  <TextArea rows={4} placeholder="请输入菜谱描述" />
                </Form.Item>
                
                <Form.Item
                  name="difficulty"
                  label="难度"
                  rules={[{ required: true, message: '请选择难度' }]}
                >
                  <Select placeholder="请选择难度">
                    <Option value="简单">简单</Option>
                    <Option value="中等">中等</Option>
                    <Option value="困难">困难</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="cooking_time"
                  label="烹饪时间（分钟）"
                  rules={[{ required: true, message: '请输入烹饪时间' }]}
                >
                  <InputNumber min={1} placeholder="请输入烹饪时间" style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name="servings"
                  label="份量（人份）"
                >
                  <InputNumber min={1} placeholder="请输入份量" style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name="image_url"
                  label="图片URL"
                >
                  <Input placeholder="请输入图片URL" />
                </Form.Item>
                
                <Divider orientation="left">烹饪步骤</Divider>
                
                {recipeSteps.map((step, index) => (
                  <div key={index} style={{ marginBottom: 16, border: '1px dashed #d9d9d9', padding: 16, borderRadius: 4 }}>
                    <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Title level={5}>步骤 {step.step_number}</Title>
                      <Button 
                        type="text" 
                        danger 
                        icon={<DeleteOutlined />} 
                        onClick={() => removeStep(index)}
                      />
                    </div>
                    
                    <Form.Item label="步骤描述">
                      <TextArea 
                        rows={3} 
                        value={step.description} 
                        onChange={(e) => updateStep(index, 'description', e.target.value)} 
                        placeholder="请输入步骤描述"
                      />
                    </Form.Item>
                    
                    <Form.Item label="步骤图片URL">
                      <Input 
                        value={step.image_url} 
                        onChange={(e) => updateStep(index, 'image_url', e.target.value)} 
                        placeholder="请输入步骤图片URL"
                      />
                    </Form.Item>
                  </div>
                ))}
                
                <Form.Item>
                  <Button type="dashed" onClick={addStep} block icon={<PlusOutlined />}>
                    添加步骤
                  </Button>
                </Form.Item>
                
                <Divider orientation="left">食材清单</Divider>
                
                {recipeIngredients.map((ingredient, index) => (
                  <div key={index} style={{ marginBottom: 16, border: '1px dashed #d9d9d9', padding: 16, borderRadius: 4 }}>
                    <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Title level={5}>食材 {index + 1}</Title>
                      <Button 
                        type="text" 
                        danger 
                        icon={<DeleteOutlined />} 
                        onClick={() => removeIngredient(index)}
                      />
                    </div>
                    
                    <Form.Item label="选择食材">
                      <Select
                        showSearch
                        value={ingredient.ingredient_id}
                        onChange={(value) => updateIngredient(index, 'ingredient_id', value)}
                        placeholder="请选择食材"
                        optionFilterProp="children"
                        filterOption={(input, option) =>
                          option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                        }
                        style={{ width: '100%' }}
                      >
                        {ingredients.map(ing => (
                          <Option key={ing.id} value={ing.id}>{ing.name}</Option>
                        ))}
                      </Select>
                    </Form.Item>
                    
                    <Form.Item label="食材名称">
                      <Input 
                        value={ingredient.ingredient_name} 
                        onChange={(e) => updateIngredient(index, 'ingredient_name', e.target.value)} 
                        placeholder="请输入食材名称"
                      />
                    </Form.Item>
                    
                    <Form.Item label="数量">
                      <InputNumber 
                        min={0} 
                        value={ingredient.amount} 
                        onChange={(value) => updateIngredient(index, 'amount', value)} 
                        placeholder="请输入数量"
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                    
                    <Form.Item label="单位">
                      <Input 
                        value={ingredient.unit} 
                        onChange={(e) => updateIngredient(index, 'unit', e.target.value)} 
                        placeholder="请输入单位"
                      />
                    </Form.Item>
                    
                    <Form.Item label="备注">
                      <Input 
                        value={ingredient.note} 
                        onChange={(e) => updateIngredient(index, 'note', e.target.value)} 
                        placeholder="请输入备注"
                      />
                    </Form.Item>
                  </div>
                ))}
                
                <Form.Item>
                  <Button type="dashed" onClick={addIngredient} block icon={<PlusOutlined />}>
                    添加食材
                  </Button>
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit">
                    {editingRecipe ? '更新' : '添加'}
                  </Button>
                  <Button 
                    style={{ marginLeft: 8 }} 
                    onClick={() => setRecipeModalVisible(false)}
                  >
                    取消
                  </Button>
                </Form.Item>
              </Form>
            </Modal>
          </TabPane>
        </Tabs>
      </div>
    </Content>
  );
};

export default DataManagementPage;