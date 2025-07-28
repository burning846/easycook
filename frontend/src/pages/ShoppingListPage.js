import React, { useState, useEffect } from 'react';
import { Typography, List, Button, Input, Form, Modal, Select, Checkbox, Divider, message, Popconfirm } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined, ShoppingCartOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;
const { Option } = Select;

function ShoppingListPage() {
  const [shoppingLists, setShoppingLists] = useState([]);
  const [currentList, setCurrentList] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [itemModalVisible, setItemModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [form] = Form.useForm();
  const [itemForm] = Form.useForm();
  
  // 假设用户ID为1
  const userId = 1;
  
  useEffect(() => {
    fetchShoppingLists();
    fetchIngredients();
  }, []);
  
  const fetchShoppingLists = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/users/${userId}/shopping_lists`);
      setShoppingLists(response.data);
      
      // 如果有购物清单，默认选择第一个
      if (response.data.length > 0 && !currentList) {
        setCurrentList(response.data[0]);
      }
    } catch (error) {
      console.error('获取购物清单失败:', error);
      message.error('获取购物清单失败');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchIngredients = async () => {
    try {
      const response = await axios.get('/api/ingredients');
      setIngredients(response.data.items);
    } catch (error) {
      console.error('获取食材列表失败:', error);
    }
  };
  
  const showAddListModal = () => {
    form.resetFields();
    setModalVisible(true);
  };
  
  const handleListModalCancel = () => {
    setModalVisible(false);
  };
  
  const handleListModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      await axios.post(`/api/users/${userId}/shopping_lists`, {
        name: values.name,
        description: values.description || ''
      });
      
      message.success('购物清单创建成功');
      setModalVisible(false);
      fetchShoppingLists();
    } catch (error) {
      console.error('创建购物清单失败:', error);
      message.error('创建购物清单失败');
    }
  };
  
  const showAddItemModal = () => {
    setEditingItem(null);
    itemForm.resetFields();
    setItemModalVisible(true);
  };
  
  const showEditItemModal = (item) => {
    setEditingItem(item);
    itemForm.setFieldsValue({
      ingredient_id: item.ingredient_id,
      amount: item.amount,
      unit: item.unit,
      note: item.note || ''
    });
    setItemModalVisible(true);
  };
  
  const handleItemModalCancel = () => {
    setItemModalVisible(false);
  };
  
  const handleItemModalOk = async () => {
    try {
      const values = await itemForm.validateFields();
      
      if (editingItem) {
        // 更新购物清单项
        await axios.put(
          `/api/users/${userId}/shopping_lists/${currentList.id}/items/${editingItem.id}`,
          {
            amount: values.amount,
            note: values.note || ''
          }
        );
        message.success('购物清单项更新成功');
      } else {
        // 添加购物清单项
        const selectedIngredient = ingredients.find(i => i.id === values.ingredient_id);
        
        await axios.post(
          `/api/users/${userId}/shopping_lists/${currentList.id}/items`,
          {
            ingredient_id: values.ingredient_id,
            amount: values.amount,
            unit: selectedIngredient.unit,
            note: values.note || ''
          }
        );
        message.success('购物清单项添加成功');
      }
      
      setItemModalVisible(false);
      refreshCurrentList();
    } catch (error) {
      console.error('保存购物清单项失败:', error);
      message.error('保存购物清单项失败');
    }
  };
  
  const handleDeleteItem = async (itemId) => {
    try {
      await axios.delete(`/api/users/${userId}/shopping_lists/${currentList.id}/items/${itemId}`);
      message.success('购物清单项删除成功');
      refreshCurrentList();
    } catch (error) {
      console.error('删除购物清单项失败:', error);
      message.error('删除购物清单项失败');
    }
  };
  
  const handleToggleItemPurchased = async (item) => {
    try {
      await axios.put(
        `/api/users/${userId}/shopping_lists/${currentList.id}/items/${item.id}`,
        {
          purchased: !item.purchased,
          amount: item.amount,
          note: item.note || ''
        }
      );
      refreshCurrentList();
    } catch (error) {
      console.error('更新购物清单项状态失败:', error);
      message.error('更新购物清单项状态失败');
    }
  };
  
  const refreshCurrentList = async () => {
    if (!currentList) return;
    
    try {
      const response = await axios.get(`/api/users/${userId}/shopping_lists/${currentList.id}`);
      setCurrentList(response.data);
    } catch (error) {
      console.error('刷新购物清单失败:', error);
    }
  };
  
  const handleDeleteList = async () => {
    if (!currentList) return;
    
    try {
      await axios.delete(`/api/users/${userId}/shopping_lists/${currentList.id}`);
      message.success('购物清单删除成功');
      setCurrentList(null);
      fetchShoppingLists();
    } catch (error) {
      console.error('删除购物清单失败:', error);
      message.error('删除购物清单失败');
    }
  };
  
  const handleAddToInventory = async (item) => {
    try {
      // 添加到用户食材库
      await axios.post(`/api/users/${userId}/ingredients`, {
        ingredient_id: item.ingredient_id,
        amount: item.amount,
        unit: item.unit
      });
      
      // 标记为已购买
      await axios.put(
        `/api/users/${userId}/shopping_lists/${currentList.id}/items/${item.id}`,
        {
          purchased: true,
          amount: item.amount,
          note: item.note || ''
        }
      );
      
      message.success('已添加到食材库');
      refreshCurrentList();
    } catch (error) {
      console.error('添加到食材库失败:', error);
      message.error('添加到食材库失败');
    }
  };
  
  return (
    <div>
      <Title level={2}>购物清单</Title>
      
      <div style={{ display: 'flex', marginBottom: 16 }}>
        <Select
          style={{ width: 200, marginRight: 16 }}
          placeholder="选择购物清单"
          value={currentList ? currentList.id : undefined}
          onChange={(value) => {
            const selected = shoppingLists.find(list => list.id === value);
            setCurrentList(selected);
          }}
        >
          {shoppingLists.map(list => (
            <Option key={list.id} value={list.id}>{list.name}</Option>
          ))}
        </Select>
        
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={showAddListModal}
          style={{ marginRight: 8 }}
        >
          新建清单
        </Button>
        
        {currentList && (
          <Popconfirm
            title="确定要删除这个购物清单吗？"
            onConfirm={handleDeleteList}
            okText="确定"
            cancelText="取消"
          >
            <Button danger icon={<DeleteOutlined />}>删除清单</Button>
          </Popconfirm>
        )}
      </div>
      
      {currentList ? (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <Title level={4}>{currentList.name}</Title>
              {currentList.description && <p>{currentList.description}</p>}
            </div>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={showAddItemModal}
            >
              添加食材
            </Button>
          </div>
          
          <Divider orientation="left">待购买</Divider>
          <List
            itemLayout="horizontal"
            dataSource={currentList.items?.filter(item => !item.purchased) || []}
            renderItem={item => (
              <List.Item
                actions={[
                  <Button 
                    type="text" 
                    icon={<EditOutlined />} 
                    onClick={() => showEditItemModal(item)}
                  />,
                  <Button 
                    type="text" 
                    icon={<ShoppingCartOutlined />} 
                    onClick={() => handleAddToInventory(item)}
                    title="添加到食材库并标记为已购买"
                  />,
                  <Popconfirm
                    title="确定要删除这个食材吗？"
                    onConfirm={() => handleDeleteItem(item.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button 
                      type="text" 
                      danger 
                      icon={<DeleteOutlined />} 
                    />
                  </Popconfirm>
                ]}
              >
                <Checkbox 
                  checked={item.purchased} 
                  onChange={() => handleToggleItemPurchased(item)}
                  style={{ marginRight: 8 }}
                />
                <List.Item.Meta
                  title={item.ingredient_name}
                  description={
                    <>
                      {`${item.amount} ${item.unit}`}
                      {item.note && <div style={{ color: '#888' }}>{item.note}</div>}
                    </>
                  }
                />
              </List.Item>
            )}
            locale={{ emptyText: '没有待购买的食材' }}
          />
          
          <Divider orientation="left">已购买</Divider>
          <List
            itemLayout="horizontal"
            dataSource={currentList.items?.filter(item => item.purchased) || []}
            renderItem={item => (
              <List.Item
                actions={[
                  <Button 
                    type="text" 
                    icon={<EditOutlined />} 
                    onClick={() => showEditItemModal(item)}
                  />,
                  <Popconfirm
                    title="确定要删除这个食材吗？"
                    onConfirm={() => handleDeleteItem(item.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button 
                      type="text" 
                      danger 
                      icon={<DeleteOutlined />} 
                    />
                  </Popconfirm>
                ]}
              >
                <Checkbox 
                  checked={item.purchased} 
                  onChange={() => handleToggleItemPurchased(item)}
                  style={{ marginRight: 8 }}
                />
                <List.Item.Meta
                  title={<span style={{ textDecoration: 'line-through' }}>{item.ingredient_name}</span>}
                  description={
                    <>
                      <span style={{ textDecoration: 'line-through' }}>{`${item.amount} ${item.unit}`}</span>
                      {item.note && <div style={{ color: '#888', textDecoration: 'line-through' }}>{item.note}</div>}
                    </>
                  }
                />
              </List.Item>
            )}
            locale={{ emptyText: '没有已购买的食材' }}
          />
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <p>请选择或创建一个购物清单</p>
          <Button type="primary" icon={<PlusOutlined />} onClick={showAddListModal}>
            创建购物清单
          </Button>
        </div>
      )}
      
      {/* 创建购物清单的模态框 */}
      <Modal
        title="创建购物清单"
        open={modalVisible}
        onOk={handleListModalOk}
        onCancel={handleListModalCancel}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="清单名称"
            rules={[{ required: true, message: '请输入清单名称' }]}
          >
            <Input placeholder="例如：周末采购" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea placeholder="清单描述（可选）" />
          </Form.Item>
        </Form>
      </Modal>
      
      {/* 添加/编辑购物清单项的模态框 */}
      <Modal
        title={editingItem ? '编辑食材' : '添加食材'}
        open={itemModalVisible}
        onOk={handleItemModalOk}
        onCancel={handleItemModalCancel}
      >
        <Form
          form={itemForm}
          layout="vertical"
        >
          <Form.Item
            name="ingredient_id"
            label="食材"
            rules={[{ required: true, message: '请选择食材' }]}
          >
            <Select
              placeholder="选择食材"
              disabled={!!editingItem}
              showSearch
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
            >
              {ingredients.map(ingredient => (
                <Option key={ingredient.id} value={ingredient.id}>{ingredient.name}</Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="amount"
            label="数量"
            rules={[{ required: true, message: '请输入数量' }]}
          >
            <Input type="number" min={0} step={0.1} />
          </Form.Item>
          
          <Form.Item
            name="note"
            label="备注"
          >
            <Input.TextArea placeholder="例如：选新鲜的" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default ShoppingListPage;