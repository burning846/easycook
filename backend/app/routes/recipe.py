from flask import jsonify, request, current_app
from app import db
from app.models.recipe import Recipe, Step
from app.models.ingredient import RecipeIngredient, Ingredient
from app.routes import api_bp

@api_bp.route('/recipes', methods=['GET'])
def get_recipes():
    """获取菜谱列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    
    query = Recipe.query
    
    if category:
        query = query.filter(Recipe.category == category)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    
    pagination = query.order_by(Recipe.created_at.desc()).paginate(page=page, per_page=per_page)
    recipes = pagination.items
    
    return jsonify({
        'items': [recipe.to_dict() for recipe in recipes],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@api_bp.route('/recipes/<int:id>', methods=['GET'])
def get_recipe(id):
    """获取单个菜谱详情"""
    recipe = Recipe.query.get_or_404(id)
    return jsonify(recipe.to_dict())

@api_bp.route('/recipes', methods=['POST'])
def create_recipe():
    """创建新菜谱"""
    data = request.get_json() or {}
    
    # 验证必填字段
    required_fields = ['name', 'description', 'difficulty', 'cooking_time', 'servings', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # 创建菜谱
    recipe = Recipe(
        name=data['name'],
        description=data['description'],
        difficulty=data['difficulty'],
        cooking_time=data['cooking_time'],
        servings=data['servings'],
        category=data['category'],
        image_url=data.get('image_url')
    )
    
    db.session.add(recipe)
    db.session.flush()  # 获取recipe.id
    
    # 添加步骤
    if 'steps' in data and isinstance(data['steps'], list):
        for i, step_data in enumerate(data['steps']):
            step = Step(
                recipe_id=recipe.id,
                step_number=i + 1,
                description=step_data.get('description', ''),
                image_url=step_data.get('image_url')
            )
            db.session.add(step)
    
    # 添加食材
    if 'ingredients' in data and isinstance(data['ingredients'], list):
        for ingredient_data in data['ingredients']:
            # 检查食材是否存在，不存在则创建
            ingredient_id = ingredient_data.get('ingredient_id')
            ingredient = None
            
            if ingredient_id:
                ingredient = Ingredient.query.get(ingredient_id)
            
            if not ingredient and 'ingredient_name' in ingredient_data:
                # 按名称查找食材
                ingredient = Ingredient.query.filter_by(name=ingredient_data['ingredient_name']).first()
                
                # 如果食材不存在，创建新食材
                if not ingredient:
                    ingredient = Ingredient(
                        name=ingredient_data['ingredient_name'],
                        unit=ingredient_data.get('unit'),
                        category=ingredient_data.get('category')
                    )
                    db.session.add(ingredient)
                    db.session.flush()  # 获取ingredient.id
            
            if ingredient:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    amount=ingredient_data.get('amount', 0),
                    note=ingredient_data.get('note')
                )
                db.session.add(recipe_ingredient)
    
    db.session.commit()
    return jsonify(recipe.to_dict()), 201

@api_bp.route('/recipes/<int:id>', methods=['PUT'])
def update_recipe(id):
    """更新菜谱"""
    recipe = Recipe.query.get_or_404(id)
    data = request.get_json() or {}
    
    # 更新基本信息
    for field in ['name', 'description', 'difficulty', 'cooking_time', 'servings', 'category', 'image_url']:
        if field in data:
            setattr(recipe, field, data[field])
    
    # 更新步骤
    if 'steps' in data and isinstance(data['steps'], list):
        # 删除现有步骤
        Step.query.filter_by(recipe_id=recipe.id).delete()
        
        # 添加新步骤
        for i, step_data in enumerate(data['steps']):
            step = Step(
                recipe_id=recipe.id,
                step_number=i + 1,
                description=step_data.get('description', ''),
                image_url=step_data.get('image_url')
            )
            db.session.add(step)
    
    # 更新食材
    if 'ingredients' in data and isinstance(data['ingredients'], list):
        # 删除现有食材关联
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()
        
        # 添加新食材关联
        for ingredient_data in data['ingredients']:
            # 检查食材是否存在，不存在则创建
            ingredient_id = ingredient_data.get('ingredient_id')
            ingredient = None
            
            if ingredient_id:
                ingredient = Ingredient.query.get(ingredient_id)
            
            if not ingredient and 'ingredient_name' in ingredient_data:
                # 按名称查找食材
                ingredient = Ingredient.query.filter_by(name=ingredient_data['ingredient_name']).first()
                
                # 如果食材不存在，创建新食材
                if not ingredient:
                    ingredient = Ingredient(
                        name=ingredient_data['ingredient_name'],
                        unit=ingredient_data.get('unit'),
                        category=ingredient_data.get('category')
                    )
                    db.session.add(ingredient)
                    db.session.flush()  # 获取ingredient.id
            
            if ingredient:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    amount=ingredient_data.get('amount', 0),
                    note=ingredient_data.get('note')
                )
                db.session.add(recipe_ingredient)
    
    db.session.commit()
    return jsonify(recipe.to_dict())

@api_bp.route('/recipes/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    """删除菜谱"""
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return '', 204

@api_bp.route('/recipes/categories', methods=['GET'])
def get_recipe_categories():
    """获取所有菜谱分类"""
    categories = db.session.query(Recipe.category).distinct().all()
    return jsonify([category[0] for category in categories if category[0]])

@api_bp.route('/recipes/search', methods=['GET'])
def search_recipes():
    """搜索菜谱"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # 简单搜索实现，可以根据需要扩展为全文搜索
    search_query = f'%{query}%'
    pagination = Recipe.query.filter(
        Recipe.name.like(search_query) | 
        Recipe.description.like(search_query)
    ).paginate(page=page, per_page=per_page)
    
    recipes = pagination.items
    
    return jsonify({
        'items': [recipe.to_dict() for recipe in recipes],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })