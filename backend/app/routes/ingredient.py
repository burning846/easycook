from flask import jsonify, request
from app import db
from app.models.ingredient import Ingredient
from app.routes import api_bp

@api_bp.route('/ingredients', methods=['GET'])
def get_ingredients():
    """获取食材列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    category = request.args.get('category')
    
    query = Ingredient.query
    
    if category:
        query = query.filter(Ingredient.category == category)
    
    pagination = query.order_by(Ingredient.name).paginate(page=page, per_page=per_page)
    ingredients = pagination.items
    
    return jsonify({
        'items': [ingredient.to_dict() for ingredient in ingredients],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@api_bp.route('/ingredients/<int:id>', methods=['GET'])
def get_ingredient(id):
    """获取单个食材详情"""
    ingredient = Ingredient.query.get_or_404(id)
    return jsonify(ingredient.to_dict())

@api_bp.route('/ingredients', methods=['POST'])
def create_ingredient():
    """创建新食材"""
    data = request.get_json() or {}
    
    # 验证必填字段
    if 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    
    # 检查食材是否已存在
    existing = Ingredient.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': 'Ingredient with this name already exists'}), 400
    
    # 创建食材
    ingredient = Ingredient(
        name=data['name'],
        unit=data.get('unit'),
        category=data.get('category'),
        image_url=data.get('image_url')
    )
    
    db.session.add(ingredient)
    db.session.commit()
    
    return jsonify(ingredient.to_dict()), 201

@api_bp.route('/ingredients/<int:id>', methods=['PUT'])
def update_ingredient(id):
    """更新食材"""
    ingredient = Ingredient.query.get_or_404(id)
    data = request.get_json() or {}
    
    # 更新字段
    for field in ['name', 'unit', 'category', 'image_url']:
        if field in data:
            setattr(ingredient, field, data[field])
    
    db.session.commit()
    return jsonify(ingredient.to_dict())

@api_bp.route('/ingredients/<int:id>', methods=['DELETE'])
def delete_ingredient(id):
    """删除食材"""
    ingredient = Ingredient.query.get_or_404(id)
    
    # 检查是否有关联的菜谱
    if ingredient.recipe_ingredients.count() > 0:
        return jsonify({'error': 'Cannot delete ingredient that is used in recipes'}), 400
    
    db.session.delete(ingredient)
    db.session.commit()
    return '', 204

@api_bp.route('/ingredients/categories', methods=['GET'])
def get_ingredient_categories():
    """获取所有食材分类"""
    categories = db.session.query(Ingredient.category).distinct().all()
    return jsonify([category[0] for category in categories if category[0]])

@api_bp.route('/ingredients/search', methods=['GET'])
def search_ingredients():
    """搜索食材"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    search_query = f'%{query}%'
    ingredients = Ingredient.query.filter(Ingredient.name.like(search_query)).all()
    
    return jsonify([ingredient.to_dict() for ingredient in ingredients])