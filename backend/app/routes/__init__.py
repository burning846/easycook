from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 导入路由模块
from app.routes import recipe, ingredient, user, favorite, auth, meal_plan