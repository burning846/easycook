import requests
import json
from flask import current_app
from typing import Dict, List, Optional
from app.services.recipe_query_service import RecipeQueryService

class DeepSeekService:
    """DeepSeek AI API服务类"""
    
    @staticmethod
    def generate_meal_plan(days: int, dietary_preferences: List[str] = None, 
                          allergies: List[str] = None, cuisine_type: str = None,
                          budget_level: str = "medium") -> Dict:
        """
        生成指定天数的菜谱规划
        
        Args:
            days: 规划天数
            dietary_preferences: 饮食偏好列表 (如: ["vegetarian", "low-carb"])
            allergies: 过敏信息列表 (如: ["nuts", "dairy"])
            cuisine_type: 菜系类型 (如: "chinese", "western", "japanese")
            budget_level: 预算水平 ("low", "medium", "high")
            
        Returns:
            Dict: 包含菜谱规划的响应数据
        """
        try:
            # 查询数据库中的真实菜谱数据
            available_recipes = DeepSeekService._query_available_recipes(
                dietary_preferences, allergies, cuisine_type, budget_level
            )
            
            # 检查是否有有效的API密钥
            api_key = current_app.config.get('DEEPSEEK_API_KEY')
            if not api_key or api_key == 'your-deepseek-api-key-here':
                # 使用真实菜谱数据生成模拟规划
                return DeepSeekService._generate_meal_plan_with_real_recipes(
                    days, dietary_preferences, allergies, cuisine_type, budget_level, available_recipes
                )
            
            # 构建包含真实菜谱数据的提示词
            prompt = DeepSeekService._build_meal_plan_prompt_with_recipes(
                days, dietary_preferences, allergies, cuisine_type, budget_level, available_recipes
            )
            
            # 调用DeepSeek API
            response = DeepSeekService._call_deepseek_api(prompt)
            
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content']
                
                # 解析AI返回的JSON格式菜谱
                try:
                    meal_plan = json.loads(content)
                    return {
                        'success': True,
                        'data': meal_plan,
                        'message': '菜谱规划生成成功'
                    }
                except json.JSONDecodeError:
                    # 如果AI返回的不是标准JSON，尝试解析文本格式
                    return {
                        'success': True,
                        'data': {
                            'meal_plan': content,
                            'format': 'text'
                        },
                        'message': '菜谱规划生成成功'
                    }
            else:
                return {
                    'success': False,
                    'message': 'AI服务响应异常'
                }
                
        except Exception as e:
            current_app.logger.error(f"DeepSeek API调用失败: {str(e)}")
            return {
                'success': False,
                'message': f'菜谱生成失败: {str(e)}'
            }
    
    @staticmethod
    def _build_meal_plan_prompt(days: int, dietary_preferences: List[str] = None,
                               allergies: List[str] = None, cuisine_type: str = None,
                               budget_level: str = "medium") -> str:
        """构建菜谱规划的提示词"""
        
        prompt = f"""请为我制定一个{days}天的详细菜谱规划。

要求：
1. 每天包含早餐、午餐、晚餐的具体菜品
2. 营养搭配均衡，包含蛋白质、碳水化合物、维生素等
3. 菜品制作难度适中，适合家庭制作
4. 提供每道菜的主要食材清单
5. 考虑食材的重复利用，减少浪费

"""

        # 添加饮食偏好
        if dietary_preferences:
            preferences_str = "、".join(dietary_preferences)
            prompt += f"饮食偏好：{preferences_str}\n"
        
        # 添加过敏信息
        if allergies:
            allergies_str = "、".join(allergies)
            prompt += f"过敏禁忌：避免使用{allergies_str}\n"
        
        # 添加菜系偏好
        if cuisine_type:
            cuisine_map = {
                "chinese": "中式菜系",
                "western": "西式菜系", 
                "japanese": "日式菜系",
                "korean": "韩式菜系",
                "thai": "泰式菜系",
                "italian": "意式菜系"
            }
            cuisine_name = cuisine_map.get(cuisine_type, cuisine_type)
            prompt += f"菜系偏好：主要以{cuisine_name}为主\n"
        
        # 添加预算考虑
        budget_map = {
            "low": "经济实惠，多使用常见食材",
            "medium": "适中预算，营养与成本平衡",
            "high": "不限预算，可使用优质食材"
        }
        budget_desc = budget_map.get(budget_level, budget_map["medium"])
        prompt += f"预算考虑：{budget_desc}\n"
        
        prompt += """
请以JSON格式返回结果，格式如下：
{
  "meal_plan": {
    "day_1": {
      "date": "第1天",
      "breakfast": {
        "name": "菜品名称",
        "ingredients": ["食材1", "食材2"],
        "cooking_time": "制作时间",
        "difficulty": "简单/中等/困难"
      },
      "lunch": {
        "name": "菜品名称", 
        "ingredients": ["食材1", "食材2"],
        "cooking_time": "制作时间",
        "difficulty": "简单/中等/困难"
      },
      "dinner": {
        "name": "菜品名称",
        "ingredients": ["食材1", "食材2"], 
        "cooking_time": "制作时间",
        "difficulty": "简单/中等/困难"
      }
    }
  },
  "shopping_list": ["所有需要采购的食材汇总"],
  "nutrition_tips": ["营养搭配建议"],
  "cooking_tips": ["烹饪小贴士"]
}
"""
        
        return prompt
    
    @staticmethod
    def _query_available_recipes(
        dietary_preferences: List[str] = None,
        allergies: List[str] = None,
        cuisine_type: str = None,
        budget_level: str = "medium"
    ) -> Dict[str, List[Dict]]:
        """
        查询数据库中可用的菜谱
        
        Args:
            dietary_preferences: 饮食偏好
            allergies: 过敏信息
            cuisine_type: 菜系类型
            budget_level: 预算水平
            
        Returns:
            Dict: 按分类组织的菜谱数据
        """
        try:
            # 根据预算水平设置烹饪时间限制
            cooking_time_limits = {
                'low': 30,      # 经济实惠，简单快手菜
                'medium': 60,   # 适中预算，中等复杂度
                'high': 120     # 不限预算，可以复杂一些
            }
            cooking_time_max = cooking_time_limits.get(budget_level, 60)
            
            # 查询不同分类的菜谱
            breakfast_recipes = RecipeQueryService.search_recipes_by_criteria(
                dietary_preferences=dietary_preferences,
                allergies=allergies,
                cuisine_type=cuisine_type,
                cooking_time_max=cooking_time_max,
                category='早餐',
                limit=10
            )
            
            lunch_recipes = RecipeQueryService.search_recipes_by_criteria(
                dietary_preferences=dietary_preferences,
                allergies=allergies,
                cuisine_type=cuisine_type,
                cooking_time_max=cooking_time_max,
                category='午餐',
                limit=15
            )
            
            dinner_recipes = RecipeQueryService.search_recipes_by_criteria(
                dietary_preferences=dietary_preferences,
                allergies=allergies,
                cuisine_type=cuisine_type,
                cooking_time_max=cooking_time_max,
                category='晚餐',
                limit=15
            )
            
            # 如果特定分类菜谱不够，从所有菜谱中补充
            if len(breakfast_recipes) < 5:
                additional_recipes = RecipeQueryService.search_recipes_by_criteria(
                    dietary_preferences=dietary_preferences,
                    allergies=allergies,
                    cuisine_type=cuisine_type,
                    cooking_time_max=30,  # 早餐通常要快
                    limit=10
                )
                breakfast_recipes.extend(additional_recipes[:5-len(breakfast_recipes)])
            
            if len(lunch_recipes) < 8:
                additional_recipes = RecipeQueryService.search_recipes_by_criteria(
                    dietary_preferences=dietary_preferences,
                    allergies=allergies,
                    cuisine_type=cuisine_type,
                    cooking_time_max=cooking_time_max,
                    limit=15
                )
                lunch_recipes.extend(additional_recipes[:8-len(lunch_recipes)])
            
            if len(dinner_recipes) < 8:
                additional_recipes = RecipeQueryService.search_recipes_by_criteria(
                    dietary_preferences=dietary_preferences,
                    allergies=allergies,
                    cuisine_type=cuisine_type,
                    cooking_time_max=cooking_time_max,
                    limit=15
                )
                dinner_recipes.extend(additional_recipes[:8-len(dinner_recipes)])
            
            return {
                'breakfast': breakfast_recipes,
                'lunch': lunch_recipes,
                'dinner': dinner_recipes
            }
            
        except Exception as e:
            current_app.logger.error(f"查询菜谱数据失败: {str(e)}")
            return {
                'breakfast': [],
                'lunch': [],
                'dinner': []
            }
    
    @staticmethod
    def _call_deepseek_api(prompt: str) -> Optional[Dict]:
        """调用DeepSeek API"""
        
        api_key = current_app.config.get('DEEPSEEK_API_KEY')
        api_url = current_app.config.get('DEEPSEEK_API_URL')
        
        if not api_key or api_key == 'your-deepseek-api-key':
            raise
    
    @staticmethod
    def _generate_meal_plan_with_real_recipes(
        days: int, 
        dietary_preferences: List[str] = None,
        allergies: List[str] = None, 
        cuisine_type: str = None,
        budget_level: str = "medium",
        available_recipes: Dict[str, List[Dict]] = None
    ) -> Dict:
        """
        使用真实菜谱数据生成菜谱规划
        
        Args:
            days: 规划天数
            dietary_preferences: 饮食偏好
            allergies: 过敏信息
            cuisine_type: 菜系类型
            budget_level: 预算水平
            available_recipes: 可用菜谱数据
            
        Returns:
            Dict: 菜谱规划结果
        """
        if not available_recipes:
            available_recipes = {'breakfast': [], 'lunch': [], 'dinner': []}
        
        import random
        from datetime import datetime, timedelta
        
        meal_plan = []
        all_ingredients = set()
        
        # 为每一天生成菜谱
        for day in range(1, days + 1):
            date = datetime.now() + timedelta(days=day-1)
            day_meals = []
            
            # 早餐
            breakfast_options = available_recipes.get('breakfast', [])
            if breakfast_options:
                breakfast = random.choice(breakfast_options)
                day_meals.append({
                    "type": "breakfast",
                    "name": breakfast['name'],
                    "ingredients": breakfast['ingredient_summary'],
                    "prep_time": f"{breakfast['cooking_time']}分钟" if breakfast['cooking_time'] else "15分钟",
                    "calories": "350卡路里",  # 可以后续从营养数据库获取
                    "difficulty": breakfast['difficulty'],
                    "recipe_id": breakfast['id']
                })
                all_ingredients.update(breakfast['ingredient_summary'])
            else:
                # 如果没有真实菜谱，使用默认早餐
                day_meals.append({
                    "type": "breakfast",
                    "name": f"第{day}天营养早餐",
                    "ingredients": ["燕麦片", "牛奶", "香蕉"],
                    "prep_time": "10分钟",
                    "calories": "350卡路里",
                    "difficulty": "简单"
                })
                all_ingredients.update(["燕麦片", "牛奶", "香蕉"])
            
            # 午餐
            lunch_options = available_recipes.get('lunch', [])
            if lunch_options:
                lunch = random.choice(lunch_options)
                day_meals.append({
                    "type": "lunch",
                    "name": lunch['name'],
                    "ingredients": lunch['ingredient_summary'],
                    "prep_time": f"{lunch['cooking_time']}分钟" if lunch['cooking_time'] else "30分钟",
                    "calories": "500卡路里",
                    "difficulty": lunch['difficulty'],
                    "recipe_id": lunch['id']
                })
                all_ingredients.update(lunch['ingredient_summary'])
            else:
                day_meals.append({
                    "type": "lunch",
                    "name": f"第{day}天健康午餐",
                    "ingredients": ["鸡胸肉", "西兰花", "糙米"],
                    "prep_time": "25分钟",
                    "calories": "500卡路里",
                    "difficulty": "中等"
                })
                all_ingredients.update(["鸡胸肉", "西兰花", "糙米"])
            
            # 晚餐
            dinner_options = available_recipes.get('dinner', [])
            if dinner_options:
                dinner = random.choice(dinner_options)
                day_meals.append({
                    "type": "dinner",
                    "name": dinner['name'],
                    "ingredients": dinner['ingredient_summary'],
                    "prep_time": f"{dinner['cooking_time']}分钟" if dinner['cooking_time'] else "40分钟",
                    "calories": "450卡路里",
                    "difficulty": dinner['difficulty'],
                    "recipe_id": dinner['id']
                })
                all_ingredients.update(dinner['ingredient_summary'])
            else:
                day_meals.append({
                    "type": "dinner",
                    "name": f"第{day}天营养晚餐",
                    "ingredients": ["三文鱼", "蔬菜沙拉", "红薯"],
                    "prep_time": "30分钟",
                    "calories": "450卡路里",
                    "difficulty": "中等"
                })
                all_ingredients.update(["三文鱼", "蔬菜沙拉", "红薯"])
            
            meal_plan.append({
                "day": day,
                "date": date.strftime("%Y-%m-%d"),
                "meals": day_meals
            })
        
        # 生成购物清单
        shopping_list = list(all_ingredients)
        
        # 生成营养建议和小贴士
        tips = [
            "建议提前准备食材，可以节省每日烹饪时间",
            "多喝水，保持身体水分充足",
            "适量运动，配合健康饮食效果更佳"
        ]
        
        # 根据饮食偏好添加特定建议
        if dietary_preferences:
            if 'vegetarian' in dietary_preferences:
                tips.append("素食饮食请注意蛋白质和维生素B12的补充")
            if 'low-carb' in dietary_preferences:
                tips.append("低碳水饮食期间可适当增加健康脂肪摄入")
            if 'high-protein' in dietary_preferences:
                tips.append("高蛋白饮食请确保充足的水分摄入")
        
        return {
            'success': True,
            'data': {
                'meal_plan': meal_plan,
                'shopping_list': shopping_list,
                'tips': tips,
                'nutrition_summary': {
                    'total_calories': f"{days * 1300}卡路里",
                    'protein': "充足",
                    'carbs': "适中",
                    'fat': "健康脂肪为主"
                }
            },
            'message': f'菜谱规划生成成功（基于{len(available_recipes.get("breakfast", []))}个早餐、{len(available_recipes.get("lunch", []))}个午餐、{len(available_recipes.get("dinner", []))}个晚餐菜谱）'
        }
    
    @staticmethod
    def _build_meal_plan_prompt_with_recipes(
        days: int,
        dietary_preferences: List[str] = None,
        allergies: List[str] = None,
        cuisine_type: str = None,
        budget_level: str = "medium",
        available_recipes: Dict[str, List[Dict]] = None
    ) -> str:
        """
        构建包含真实菜谱数据的AI提示词
        
        Args:
            days: 规划天数
            dietary_preferences: 饮食偏好
            allergies: 过敏信息
            cuisine_type: 菜系类型
            budget_level: 预算水平
            available_recipes: 可用菜谱数据
            
        Returns:
            str: AI提示词
        """
        if not available_recipes:
            available_recipes = {'breakfast': [], 'lunch': [], 'dinner': []}
        
        # 构建基础提示词
        prompt = f"""你是一个专业的营养师和厨师，请根据以下要求和可用菜谱数据生成{days}天的菜谱规划：

## 用户需求：
- 规划天数：{days}天
- 饮食偏好：{', '.join(dietary_preferences) if dietary_preferences else '无特殊要求'}
- 过敏信息：{', '.join(allergies) if allergies else '无'}
- 菜系偏好：{cuisine_type if cuisine_type else '不限'}
- 预算水平：{budget_level}

## 可用菜谱数据：

### 早餐菜谱（{len(available_recipes.get('breakfast', []))}个）：
"""
        
        # 添加早餐菜谱
        breakfast_recipes = available_recipes.get('breakfast', [])
        if breakfast_recipes:
            for i, recipe in enumerate(breakfast_recipes[:10], 1):  # 限制显示前10个
                prompt += f"{i}. {recipe['name']} - 难度：{recipe['difficulty']} - 时间：{recipe['cooking_time']}分钟\n"
                prompt += f"   食材：{', '.join(recipe['ingredient_summary'][:5])}{'...' if len(recipe['ingredient_summary']) > 5 else ''}\n"
        else:
            prompt += "暂无早餐菜谱数据\n"
        
        # 添加午餐菜谱
        prompt += f"\n### 午餐菜谱（{len(available_recipes.get('lunch', []))}个）：\n"
        lunch_recipes = available_recipes.get('lunch', [])
        if lunch_recipes:
            for i, recipe in enumerate(lunch_recipes[:10], 1):
                prompt += f"{i}. {recipe['name']} - 难度：{recipe['difficulty']} - 时间：{recipe['cooking_time']}分钟\n"
                prompt += f"   食材：{', '.join(recipe['ingredient_summary'][:5])}{'...' if len(recipe['ingredient_summary']) > 5 else ''}\n"
        else:
            prompt += "暂无午餐菜谱数据\n"
        
        # 添加晚餐菜谱
        prompt += f"\n### 晚餐菜谱（{len(available_recipes.get('dinner', []))}个）：\n"
        dinner_recipes = available_recipes.get('dinner', [])
        if dinner_recipes:
            for i, recipe in enumerate(dinner_recipes[:10], 1):
                prompt += f"{i}. {recipe['name']} - 难度：{recipe['difficulty']} - 时间：{recipe['cooking_time']}分钟\n"
                prompt += f"   食材：{', '.join(recipe['ingredient_summary'][:5])}{'...' if len(recipe['ingredient_summary']) > 5 else ''}\n"
        else:
            prompt += "暂无晚餐菜谱数据\n"
        
        # 添加生成要求
        prompt += f"""

## 生成要求：
1. 优先从上述可用菜谱中选择，确保菜谱的多样性和营养均衡
2. 如果可用菜谱不足，可以适当补充类似的菜谱建议
3. 严格遵守用户的饮食偏好和过敏限制
4. 考虑预算水平，选择合适价位的食材
5. 提供详细的购物清单和营养建议
6. 包含实用的烹饪小贴士

## 输出格式：
请以JSON格式返回，包含以下字段：
- meal_plan: 每日菜谱安排（包含早中晚餐）
- shopping_list: 购物清单
- tips: 烹饪和营养建议
- nutrition_summary: 营养总结

请确保推荐的菜谱实用、营养均衡，并符合用户的具体需求。"""
        
        return prompt
    
    @staticmethod
    def _get_mock_meal_plan(days: int, dietary_preferences: List[str] = None, 
                           allergies: List[str] = None, cuisine_type: str = None,
                           budget_level: str = "medium") -> Dict:
        """
        返回模拟的菜谱规划数据用于演示
        """
        mock_data = {
            "meal_plan": [
                {
                    "day": 1,
                    "date": "2024-01-01",
                    "meals": [
                        {
                            "type": "breakfast",
                            "name": "燕麦粥配水果",
                            "ingredients": ["燕麦片", "牛奶", "香蕉", "蓝莓", "蜂蜜"],
                            "prep_time": "10分钟",
                            "calories": "350卡路里"
                        },
                        {
                            "type": "lunch", 
                            "name": "鸡胸肉沙拉",
                            "ingredients": ["鸡胸肉", "生菜", "西红柿", "黄瓜", "橄榄油"],
                            "prep_time": "20分钟",
                            "calories": "420卡路里"
                        },
                        {
                            "type": "dinner",
                            "name": "三文鱼配蒸蔬菜",
                            "ingredients": ["三文鱼", "西兰花", "胡萝卜", "柠檬", "橄榄油"],
                            "prep_time": "25分钟", 
                            "calories": "480卡路里"
                        }
                    ]
                },
                {
                    "day": 2,
                    "date": "2024-01-02",
                    "meals": [
                        {
                            "type": "breakfast",
                            "name": "全麦吐司配牛油果",
                            "ingredients": ["全麦面包", "牛油果", "鸡蛋", "西红柿"],
                            "prep_time": "15分钟",
                            "calories": "380卡路里"
                        },
                        {
                            "type": "lunch",
                            "name": "蔬菜炒饭",
                            "ingredients": ["糙米", "胡萝卜", "豌豆", "鸡蛋", "酱油"],
                            "prep_time": "18分钟",
                            "calories": "450卡路里"
                        },
                        {
                            "type": "dinner",
                            "name": "烤鸡腿配烤蔬菜",
                            "ingredients": ["鸡腿", "土豆", "洋葱", "彩椒", "迷迭香"],
                            "prep_time": "35分钟",
                            "calories": "520卡路里"
                        }
                    ]
                }
            ],
            "shopping_list": [
                "燕麦片", "牛奶", "香蕉", "蓝莓", "蜂蜜",
                "鸡胸肉", "生菜", "西红柿", "黄瓜", "橄榄油",
                "三文鱼", "西兰花", "胡萝卜", "柠檬",
                "全麦面包", "牛油果", "鸡蛋",
                "糙米", "豌豆", "酱油", "鸡腿", "土豆", "洋葱", "彩椒", "迷迭香"
            ],
            "tips": [
                "建议提前准备食材，可以节省每日烹饪时间",
                "多喝水，保持身体水分充足",
                "适量运动，配合健康饮食效果更佳",
                "可以根据个人口味调整调料用量"
            ],
            "nutrition_summary": {
                "total_calories": f"{days * 1250}卡路里",
                "protein": "充足",
                "carbs": "适中",
                "fat": "健康脂肪为主"
            }
        }
        
        # 根据天数调整数据
        if days > 2:
            for day in range(3, days + 1):
                mock_data["meal_plan"].append({
                    "day": day,
                    "date": f"2024-01-{day:02d}",
                    "meals": [
                        {
                            "type": "breakfast",
                            "name": f"第{day}天早餐",
                            "ingredients": ["营养早餐食材"],
                            "prep_time": "15分钟",
                            "calories": "350卡路里"
                        },
                        {
                            "type": "lunch",
                            "name": f"第{day}天午餐",
                            "ingredients": ["健康午餐食材"],
                            "prep_time": "20分钟",
                            "calories": "450卡路里"
                        },
                        {
                            "type": "dinner",
                            "name": f"第{day}天晚餐",
                            "ingredients": ["营养晚餐食材"],
                            "prep_time": "25分钟",
                            "calories": "450卡路里"
                        }
                    ]
                })
        
        return {
             'success': True,
             'data': mock_data,
             'message': '菜谱规划生成成功（演示数据）'
         }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"DeepSeek API请求失败: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"DeepSeek API调用异常: {str(e)}")
            raise