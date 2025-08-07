from datetime import datetime
from app import db

class Recipe(db.Model):
    """菜谱模型"""
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20))  # 简单、中等、困难
    cooking_time = db.Column(db.Integer)  # 烹饪时间（分钟）
    servings = db.Column(db.Integer)  # 份量（人数）
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50), index=True)  # 分类：早餐、午餐、晚餐、小吃等
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    steps = db.relationship('Step', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    recipe_ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'difficulty': self.difficulty,
            'cooking_time': self.cooking_time,
            'servings': self.servings,
            'image_url': self.image_url,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'steps': [step.to_dict() for step in self.steps],
            'ingredients': [ri.to_dict() for ri in self.recipe_ingredients]
        }

class Step(db.Model):
    """菜谱步骤模型"""
    __tablename__ = 'steps'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)  # 步骤序号
    description = db.Column(db.Text, nullable=False)  # 步骤描述
    image_url = db.Column(db.String(255))  # 步骤图片
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'step_number': self.step_number,
            'description': self.description,
            'image_url': self.image_url
        }