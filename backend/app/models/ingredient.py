from app import db

class Ingredient(db.Model):
    """食材模型"""
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    unit = db.Column(db.String(20))  # 单位：克、个、杯等
    category = db.Column(db.String(50))  # 分类：肉类、蔬菜、调料等
    image_url = db.Column(db.String(255))
    
    # 关系
    recipe_ingredients = db.relationship('RecipeIngredient', backref='ingredient', lazy='dynamic')
    user_ingredients = db.relationship('UserIngredient', backref='ingredient', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'unit': self.unit,
            'category': self.category,
            'image_url': self.image_url
        }

class RecipeIngredient(db.Model):
    """菜谱食材关联模型"""
    __tablename__ = 'recipe_ingredients'
    
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    amount = db.Column(db.Float, nullable=False)  # 数量
    note = db.Column(db.String(100))  # 备注，如"切片"、"切丁"等
    
    def to_dict(self):
        return {
            'recipe_id': self.recipe_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'amount': self.amount,
            'unit': self.ingredient.unit if self.ingredient else None,
            'note': self.note
        }