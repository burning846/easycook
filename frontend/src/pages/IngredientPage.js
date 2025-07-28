import React, { useState, useEffect } from 'react';
import { Typography, Tabs, Table, Button, Input, Form, Modal, Select, DatePicker, Tag, message, Popconfirm } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { Title } = Typography;
const { TabPane } = Tabs;
const { Search } = Input;
const { Option } = Select;

function IngredientPage() {
  const [activeTab, setActiveTab] = useState('1');
  const [ingredients, setIngredients] = useState([]);
  const [userIngredients, setUserIngredients] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState(null);
  const [form] = Form.useForm();
  
  // 假设用户ID为1
  const userId = 1;
  
  useEffect(() => {
    // 获取食材分类
    const fetchCategories = async () => {
      try {
        const response = await axios.get('/api/ingredients/categories');
        setCategories(response.data);
      } catch (error) {
        console.error('获取食材分类失败:', error);
      }
    };
    
    fetchCategories();
  }, []);
  
  useEffect(() => {
    // 根据当前标签页加载数据
    if (activeTab === '1') {
      fetchUserIngredients();
    } else {
      fetchAllIngredients();
    }
  }, [activeTab]);
  
  const fetchUserIngredients = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/users/${userId}/ingredients`);
      setUserIngredients(response.data);
    } catch (error) {
      console.error('获取用户食材失败:', error);
      message.error('获取用户食材失败');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchAllIngredients = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/ingredients');
      setIngredients(response.data.items);
    } catch (error) {
      console.error('获取食材列表失败:', error);
      message.error('获取食材列表失败');
    } finally {
      setLoading(false);
    }
  };
  
  const handleTabChange = key => {
    setActiveTab(key);
  };
  
  const showAddModal = () => {
    setEditingIngredient(null);
    form.resetFields();
    setModalVisible(true);
  };
  
  const showEditModal = record => {
    setEditingIngredient(record);
    form.setFieldsValue({
      ingredient_id: record.ingredient_id,
      ingredient_name: record.ingredient_name,
      amount: record.amount,
      unit: record.unit,
      expiry_date: record.expiry_date ? dayjs(record.expiry_date) : undefined
    });
    setModalVisible(true);
  };
  
  const handleModalCancel = () => {
    setModalVisible(false);
  };
  
  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingIngredient) {
        // 更新食材
        await axios.put(`/api/users/${userId}/ingredients/${values.ingredient_id}`, {
          amount: values.amount,
          expiry_date: values.expiry_date ? values.expiry_date.format('YYYY-MM-DD') : null
        });
        message.success('食材更新成功');
      } else {
        // 添加食材
        await axios.post(`/api/users/${userId}/ingredients`, {
          ingredient_id: values.ingredient_id,
          ingredient_name: values.ingredient_name,
          amount: values.amount,
          unit: values.unit,
          expiry_date: values.expiry_date ? values.expiry_date.format('YYYY-MM-DD') : null
        });
        message.success('食材添加成功');
      }
      
      setModalVisible(false);
      fetchUserIngredients();
    } catch (error) {
      console.error('保存食材失败:', error);
      message.error('保存食材失败');
    }
  };
  
  const handleDeleteIngredient = async (ingredientId) => {
    try {
      await axios.delete(`/api/users/${userId}/ingredients/${ingredientId}`);
      message.success('食材删除成功');
      fetchUserIngredients();
    } catch (error) {
      console.error('删除食材失败:', error);
      message.error('删除食材失败');
    }
  };
  
  const handleSearch = async (value) => {
    if (!value) {
      if (activeTab === '1') {
        fetchUserIngredients();
      } else {
        fetchAllIngredients();
      }
      return;
    }
    
    try {
      setLoading(true);
      const response = await axios.get('/api/ingredients/search', {
        params: { q: value }
      });
      
      if (activeTab === '1') {
        // 在用户食材中搜索
        const userIngredientIds = userIngredients.map(ui => ui.ingredient_id);
        const filteredIngredients = response.data.filter(ingredient => 
          userIngredientIds.includes(ingredient.id)
        );
        setUserIngredients(filteredIngredients);
      } else {
        // 在所有食材中搜索
        setIngredients(response.data);
      }
    } catch (error) {
      console.error('搜索食材失败:', error);
      message.error('搜索食材失败');
    } finally {
      setLoading(false);
    }
  };
  
  const userIngredientsColumns = [
    {
      title: '食材名称',
      dataIndex: 'ingredient_name',
      key: 'ingredient_name',
    },
    {
      title: '数量',
      dataIndex: 'amount',
      key: 'amount',
      render: (text, record) => `${text || 0} ${record.unit || ''}`
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      render: text => text ? <Tag color="blue">{text}</Tag> : '-'
    },
    {
      title: '过期日期',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      render: text => text || '-'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <>
          <Button 
            type="text" 
            icon={<EditOutlined />} 
            onClick={() => showEditModal(record)}
          />
          <Popconfirm
            title="确定要删除这个食材吗？"
            onConfirm={() => handleDeleteIngredient(record.ingredient_id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="text" 
              danger 
              icon={<DeleteOutlined />} 
            />
          </Popconfirm>
        </>
      )
    }
  ];
  
  const allIngredientsColumns = [
    {
      title: '食材名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      render: text => text ? <Tag color="blue">{text}</Tag> : '-'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button 
          type="primary" 
          onClick={() => {
            form.resetFields();
            form.setFieldsValue({
              ingredient_id: record.id,
              ingredient_name: record.name,
              unit: record.unit
            });
            setModalVisible(true);
          }}
        >
          添加到我的食材
        </Button>
      )
    }
  ];
  
  return (
    <div>
      <Title level={2}>食材管理</Title>
      
      <Tabs activeKey={activeTab} onChange={handleTabChange}>
        <TabPane tab="我的食材" key="1">
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
            <Search 
              placeholder="搜索我的食材" 
              style={{ width: 300 }} 
              onSearch={handleSearch} 
              allowClear 
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={showAddModal}>
              添加食材
            </Button>
          </div>
          
          <Table 
            columns={userIngredientsColumns} 
            dataSource={userIngredients} 
            rowKey="ingredient_id" 
            loading={loading}
          />
        </TabPane>
        
        <TabPane tab="所有食材" key="2">
          <div style={{ marginBottom: 16 }}>
            <Search 
              placeholder="搜索食材" 
              style={{ width: 300 }} 
              onSearch={handleSearch} 
              allowClear 
            />
          </div>
          
          <Table 
            columns={allIngredientsColumns} 
            dataSource={ingredients} 
            rowKey="id" 
            loading={loading}
          />
        </TabPane>
      </Tabs>
      
      <Modal
        title={editingIngredient ? '编辑食材' : '添加食材'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="ingredient_id"
            hidden={true}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="ingredient_name"
            label="食材名称"
            rules={[{ required: true, message: '请输入食材名称' }]}
          >
            <Input disabled={!!editingIngredient} />
          </Form.Item>
          
          <Form.Item
            name="amount"
            label="数量"
            rules={[{ required: true, message: '请输入数量' }]}
          >
            <Input type="number" min={0} step={0.1} />
          </Form.Item>
          
          <Form.Item
            name="unit"
            label="单位"
          >
            <Input disabled={!!editingIngredient} />
          </Form.Item>
          
          <Form.Item
            name="expiry_date"
            label="过期日期"
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default IngredientPage;