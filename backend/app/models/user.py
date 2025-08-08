from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_id = db.Column(db.String(128), unique=True, nullable=True)  # Google OAuth ID
    
    # 关系
    user_ingredients = db.relationship('UserIngredient', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    shopping_lists = db.relationship('ShoppingList', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorite_recipes = db.relationship('FavoriteRecipe', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_favorites=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_google_account': self.google_id is not None
        }
        
        if include_favorites:
            data['favorite_recipes'] = [fr.to_dict() for fr in self.favorite_recipes]
        
        return data

class UserIngredient(db.Model):
    """用户食材库存模型"""
    __tablename__ = 'user_ingredients'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    amount = db.Column(db.Float)  # 数量
    expiry_date = db.Column(db.Date)  # 过期日期
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'amount': self.amount,
            'unit': self.ingredient.unit if self.ingredient else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None
        }

class ShoppingList(db.Model):
    """购物清单模型"""
    __tablename__ = 'shopping_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), default='购物清单')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    items = db.relationship('ShoppingListItem', backref='shopping_list', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class ShoppingListItem(db.Model):
    """购物清单项目模型"""
    __tablename__ = 'shopping_list_items'
    
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    amount = db.Column(db.Float)  # 数量
    is_purchased = db.Column(db.Boolean, default=False)  # 是否已购买
    
    # 关系
    ingredient = db.relationship('Ingredient')
    
    def to_dict(self):
        return {
            'id': self.id,
            'shopping_list_id': self.shopping_list_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'amount': self.amount,
            'unit': self.ingredient.unit if self.ingredient else None,
            'is_purchased': self.is_purchased
        }

class UserPreference(db.Model):
    """用户偏好模型"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preference_type = db.Column(db.String(50), nullable=False)  # 偏好类型：口味、禁忌、特殊要求等
    value = db.Column(db.String(100), nullable=False)  # 偏好值
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preference_type': self.preference_type,
            'value': self.value
        }