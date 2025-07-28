from app import db
from datetime import datetime

class FavoriteRecipe(db.Model):
    """用户收藏菜谱模型"""
    __tablename__ = 'favorite_recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    recipe = db.relationship('Recipe')
    
    # 添加唯一约束，确保用户不会重复收藏同一个菜谱
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recipe_id': self.recipe_id,
            'recipe': self.recipe.to_dict() if self.recipe else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }