from flask import jsonify, request, current_app
from app import db
from app.models.user import User, UserIngredient, ShoppingList, ShoppingListItem, UserPreference
from app.models.ingredient import Ingredient
from app.routes import api_bp
from datetime import datetime

# 用户相关路由
@api_bp.route('/users', methods=['POST'])
def create_user():
    """创建新用户"""
    data = request.get_json() or {}
    
    # 验证必填字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # 创建用户
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """获取用户信息"""
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

# 用户食材库存相关路由
@api_bp.route('/users/<int:user_id>/ingredients', methods=['GET'])
def get_user_ingredients(user_id):
    """获取用户食材库存"""
    User.query.get_or_404(user_id)  # 确认用户存在
    
    user_ingredients = UserIngredient.query.filter_by(user_id=user_id).all()
    return jsonify([ui.to_dict() for ui in user_ingredients])

@api_bp.route('/users/<int:user_id>/ingredients', methods=['POST'])
def add_user_ingredient(user_id):
    """添加用户食材库存"""
    User.query.get_or_404(user_id)  # 确认用户存在
    data = request.get_json() or {}
    
    # 验证必填字段
    if 'ingredient_id' not in data and 'ingredient_name' not in data:
        return jsonify({'error': 'Either ingredient_id or ingredient_name is required'}), 400
    
    # 获取或创建食材
    ingredient = None
    if 'ingredient_id' in data:
        ingredient = Ingredient.query.get(data['ingredient_id'])
    
    if not ingredient and 'ingredient_name' in data:
        # 按名称查找食材
        ingredient = Ingredient.query.filter_by(name=data['ingredient_name']).first()
        
        # 如果食材不存在，创建新食材
        if not ingredient:
            ingredient = Ingredient(
                name=data['ingredient_name'],
                unit=data.get('unit'),
                category=data.get('category')
            )
            db.session.add(ingredient)
            db.session.flush()  # 获取ingredient.id
    
    if not ingredient:
        return jsonify({'error': 'Ingredient not found'}), 404
    
    # 检查是否已存在该用户的该食材记录
    user_ingredient = UserIngredient.query.filter_by(
        user_id=user_id, ingredient_id=ingredient.id
    ).first()
    
    if user_ingredient:
        # 更新现有记录
        if 'amount' in data:
            user_ingredient.amount = data['amount']
        if 'expiry_date' in data and data['expiry_date']:
            user_ingredient.expiry_date = datetime.fromisoformat(data['expiry_date'])
    else:
        # 创建新记录
        user_ingredient = UserIngredient(
            user_id=user_id,
            ingredient_id=ingredient.id,
            amount=data.get('amount'),
            expiry_date=datetime.fromisoformat(data['expiry_date']) if 'expiry_date' in data and data['expiry_date'] else None
        )
        db.session.add(user_ingredient)
    
    db.session.commit()
    return jsonify(user_ingredient.to_dict()), 201

@api_bp.route('/users/<int:user_id>/ingredients/<int:ingredient_id>', methods=['DELETE'])
def delete_user_ingredient(user_id, ingredient_id):
    """删除用户食材库存"""
    user_ingredient = UserIngredient.query.filter_by(
        user_id=user_id, ingredient_id=ingredient_id
    ).first_or_404()
    
    db.session.delete(user_ingredient)
    db.session.commit()
    return '', 204

# 购物清单相关路由
@api_bp.route('/users/<int:user_id>/shopping-lists', methods=['GET'])
def get_user_shopping_lists(user_id):
    """获取用户的购物清单"""
    User.query.get_or_404(user_id)  # 确认用户存在
    
    shopping_lists = ShoppingList.query.filter_by(user_id=user_id).all()
    return jsonify([sl.to_dict() for sl in shopping_lists])

@api_bp.route('/users/<int:user_id>/shopping-lists', methods=['POST'])
def create_shopping_list(user_id):
    """创建购物清单"""
    User.query.get_or_404(user_id)  # 确认用户存在
    data = request.get_json() or {}
    
    shopping_list = ShoppingList(
        user_id=user_id,
        name=data.get('name', '购物清单')
    )
    
    db.session.add(shopping_list)
    db.session.flush()  # 获取shopping_list.id
    
    # 添加购物清单项目
    if 'items' in data and isinstance(data['items'], list):
        for item_data in data['items']:
            # 获取或创建食材
            ingredient = None
            if 'ingredient_id' in item_data:
                ingredient = Ingredient.query.get(item_data['ingredient_id'])
            
            if not ingredient and 'ingredient_name' in item_data:
                # 按名称查找食材
                ingredient = Ingredient.query.filter_by(name=item_data['ingredient_name']).first()
                
                # 如果食材不存在，创建新食材
                if not ingredient:
                    ingredient = Ingredient(
                        name=item_data['ingredient_name'],
                        unit=item_data.get('unit'),
                        category=item_data.get('category')
                    )
                    db.session.add(ingredient)
                    db.session.flush()  # 获取ingredient.id
            
            if ingredient:
                shopping_list_item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=ingredient.id,
                    amount=item_data.get('amount'),
                    is_purchased=item_data.get('is_purchased', False)
                )
                db.session.add(shopping_list_item)
    
    db.session.commit()
    return jsonify(shopping_list.to_dict()), 201

@api_bp.route('/shopping-lists/<int:id>', methods=['GET'])
def get_shopping_list(id):
    """获取购物清单详情"""
    shopping_list = ShoppingList.query.get_or_404(id)
    return jsonify(shopping_list.to_dict())

@api_bp.route('/shopping-lists/<int:id>/items', methods=['POST'])
def add_shopping_list_item(id):
    """添加购物清单项目"""
    shopping_list = ShoppingList.query.get_or_404(id)
    data = request.get_json() or {}
    
    # 验证必填字段
    if 'ingredient_id' not in data and 'ingredient_name' not in data:
        return jsonify({'error': 'Either ingredient_id or ingredient_name is required'}), 400
    
    # 获取或创建食材
    ingredient = None
    if 'ingredient_id' in data:
        ingredient = Ingredient.query.get(data['ingredient_id'])
    
    if not ingredient and 'ingredient_name' in data:
        # 按名称查找食材
        ingredient = Ingredient.query.filter_by(name=data['ingredient_name']).first()
        
        # 如果食材不存在，创建新食材
        if not ingredient:
            ingredient = Ingredient(
                name=data['ingredient_name'],
                unit=data.get('unit'),
                category=data.get('category')
            )
            db.session.add(ingredient)
            db.session.flush()  # 获取ingredient.id
    
    if not ingredient:
        return jsonify({'error': 'Ingredient not found'}), 404
    
    # 检查是否已存在该购物清单的该食材记录
    item = ShoppingListItem.query.filter_by(
        shopping_list_id=id, ingredient_id=ingredient.id
    ).first()
    
    if item:
        # 更新现有记录
        if 'amount' in data:
            item.amount = data['amount']
        if 'is_purchased' in data:
            item.is_purchased = data['is_purchased']
    else:
        # 创建新记录
        item = ShoppingListItem(
            shopping_list_id=id,
            ingredient_id=ingredient.id,
            amount=data.get('amount'),
            is_purchased=data.get('is_purchased', False)
        )
        db.session.add(item)
    
    db.session.commit()
    return jsonify(item.to_dict()), 201

@api_bp.route('/shopping-list-items/<int:id>', methods=['PUT'])
def update_shopping_list_item(id):
    """更新购物清单项目"""
    item = ShoppingListItem.query.get_or_404(id)
    data = request.get_json() or {}
    
    # 更新字段
    if 'amount' in data:
        item.amount = data['amount']
    if 'is_purchased' in data:
        item.is_purchased = data['is_purchased']
    
    db.session.commit()
    return jsonify(item.to_dict())

@api_bp.route('/shopping-list-items/<int:id>', methods=['DELETE'])
def delete_shopping_list_item(id):
    """删除购物清单项目"""
    item = ShoppingListItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return '', 204

# 用户偏好相关路由
@api_bp.route('/users/<int:user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    """获取用户偏好"""
    User.query.get_or_404(user_id)  # 确认用户存在
    
    preferences = UserPreference.query.filter_by(user_id=user_id).all()
    return jsonify([pref.to_dict() for pref in preferences])

@api_bp.route('/users/<int:user_id>/preferences', methods=['POST'])
def add_user_preference(user_id):
    """添加用户偏好"""
    User.query.get_or_404(user_id)  # 确认用户存在
    data = request.get_json() or {}
    
    # 验证必填字段
    required_fields = ['preference_type', 'value']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # 检查是否已存在该类型的偏好
    existing = UserPreference.query.filter_by(
        user_id=user_id, preference_type=data['preference_type'], value=data['value']
    ).first()
    
    if existing:
        return jsonify({'error': 'This preference already exists'}), 400
    
    # 创建新偏好
    preference = UserPreference(
        user_id=user_id,
        preference_type=data['preference_type'],
        value=data['value']
    )
    
    db.session.add(preference)
    db.session.commit()
    
    return jsonify(preference.to_dict()), 201

@api_bp.route('/user-preferences/<int:id>', methods=['DELETE'])
def delete_user_preference(id):
    """删除用户偏好"""
    preference = UserPreference.query.get_or_404(id)
    db.session.delete(preference)
    db.session.commit()
    return '', 204