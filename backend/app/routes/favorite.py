from flask import jsonify, request
from app import db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.favorite import FavoriteRecipe
from app.routes import api_bp

@api_bp.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    """获取用户收藏的菜谱"""
    User.query.get_or_404(user_id)  # 确认用户存在
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    pagination = FavoriteRecipe.query.filter_by(user_id=user_id).order_by(
        FavoriteRecipe.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    favorites = pagination.items
    
    return jsonify({
        'items': [{
            'id': fav.id,
            'recipe_id': fav.recipe_id,
            'recipe': fav.recipe.to_dict() if fav.recipe else None,
            'created_at': fav.created_at.isoformat() if fav.created_at else None
        } for fav in favorites],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@api_bp.route('/users/<int:user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    """添加收藏菜谱"""
    User.query.get_or_404(user_id)  # 确认用户存在
    data = request.get_json() or {}
    
    # 验证必填字段
    if 'recipe_id' not in data:
        return jsonify({'error': 'Missing required field: recipe_id'}), 400
    
    # 确认菜谱存在
    recipe = Recipe.query.get_or_404(data['recipe_id'])
    
    # 检查是否已收藏
    existing = FavoriteRecipe.query.filter_by(
        user_id=user_id, recipe_id=data['recipe_id']
    ).first()
    
    if existing:
        return jsonify({'error': 'Recipe already in favorites'}), 400
    
    # 创建收藏记录
    favorite = FavoriteRecipe(
        user_id=user_id,
        recipe_id=data['recipe_id']
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify(favorite.to_dict()), 201

@api_bp.route('/users/<int:user_id>/favorites/<int:recipe_id>', methods=['DELETE'])
def remove_favorite(user_id, recipe_id):
    """取消收藏菜谱"""
    favorite = FavoriteRecipe.query.filter_by(
        user_id=user_id, recipe_id=recipe_id
    ).first_or_404()
    
    db.session.delete(favorite)
    db.session.commit()
    
    return '', 204

@api_bp.route('/users/<int:user_id>/favorites/check/<int:recipe_id>', methods=['GET'])
def check_favorite(user_id, recipe_id):
    """检查菜谱是否已收藏"""
    favorite = FavoriteRecipe.query.filter_by(
        user_id=user_id, recipe_id=recipe_id
    ).first()
    
    return jsonify({'is_favorite': favorite is not None})