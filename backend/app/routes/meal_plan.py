from flask import Blueprint, request, jsonify, current_app
from app.services.deepseek_service import DeepSeekService
from app.routes import api_bp
import logging

@api_bp.route('/meal-plan/generate', methods=['POST'])
def generate_meal_plan():
    """
    生成AI菜谱规划
    
    请求参数:
    {
        "days": 7,                                    # 规划天数 (1-14)
        "dietary_preferences": ["vegetarian"],        # 饮食偏好 (可选)
        "allergies": ["nuts", "dairy"],              # 过敏信息 (可选)
        "cuisine_type": "chinese",                   # 菜系类型 (可选)
        "budget_level": "medium"                     # 预算水平 (可选)
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证必需参数
        days = data.get('days')
        if not days or not isinstance(days, int) or days < 1 or days > 14:
            return jsonify({
                'success': False,
                'message': '天数必须是1-14之间的整数'
            }), 400
        
        # 获取可选参数
        dietary_preferences = data.get('dietary_preferences', [])
        allergies = data.get('allergies', [])
        cuisine_type = data.get('cuisine_type')
        budget_level = data.get('budget_level', 'medium')
        
        # 验证参数类型
        if not isinstance(dietary_preferences, list):
            dietary_preferences = []
        if not isinstance(allergies, list):
            allergies = []
        if budget_level not in ['low', 'medium', 'high']:
            budget_level = 'medium'
        
        # 调用DeepSeek服务生成菜谱
        result = DeepSeekService.generate_meal_plan(
            days=days,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
            cuisine_type=cuisine_type,
            budget_level=budget_level
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        current_app.logger.error(f"菜谱规划生成失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@api_bp.route('/meal-plan/preferences', methods=['GET'])
def get_meal_plan_preferences():
    """
    获取菜谱规划的可选偏好设置
    """
    try:
        preferences = {
            'dietary_preferences': [
                {'value': 'vegetarian', 'label': '素食主义'},
                {'value': 'vegan', 'label': '纯素食'},
                {'value': 'low-carb', 'label': '低碳水'},
                {'value': 'high-protein', 'label': '高蛋白'},
                {'value': 'low-fat', 'label': '低脂肪'},
                {'value': 'gluten-free', 'label': '无麸质'},
                {'value': 'keto', 'label': '生酮饮食'},
                {'value': 'mediterranean', 'label': '地中海饮食'}
            ],
            'common_allergies': [
                {'value': 'nuts', 'label': '坚果'},
                {'value': 'dairy', 'label': '乳制品'},
                {'value': 'eggs', 'label': '鸡蛋'},
                {'value': 'seafood', 'label': '海鲜'},
                {'value': 'shellfish', 'label': '贝类'},
                {'value': 'soy', 'label': '大豆'},
                {'value': 'wheat', 'label': '小麦'},
                {'value': 'sesame', 'label': '芝麻'}
            ],
            'cuisine_types': [
                {'value': 'chinese', 'label': '中式菜系'},
                {'value': 'western', 'label': '西式菜系'},
                {'value': 'japanese', 'label': '日式菜系'},
                {'value': 'korean', 'label': '韩式菜系'},
                {'value': 'thai', 'label': '泰式菜系'},
                {'value': 'italian', 'label': '意式菜系'},
                {'value': 'indian', 'label': '印度菜系'},
                {'value': 'mexican', 'label': '墨西哥菜系'}
            ],
            'budget_levels': [
                {'value': 'low', 'label': '经济实惠'},
                {'value': 'medium', 'label': '适中预算'},
                {'value': 'high', 'label': '不限预算'}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': preferences,
            'message': '偏好设置获取成功'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取偏好设置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取偏好设置失败: {str(e)}'
        }), 500

@api_bp.route('/meal-plan/test', methods=['GET'])
def test_meal_plan():
    """测试菜谱规划API"""
    return jsonify({
        'success': True,
        'message': '菜谱规划API正常运行',
        'service': 'meal_plan'
    }), 200