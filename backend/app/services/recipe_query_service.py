from typing import Dict, List, Optional
from app import db
from app.models.recipe import Recipe, Step
from app.models.ingredient import Ingredient, RecipeIngredient
from sqlalchemy import or_, and_

class RecipeQueryService:
    """菜谱查询服务，为AI提供结构化的菜谱数据"""
    
    @staticmethod
    def search_recipes_by_criteria(
        dietary_preferences: List[str] = None,
        allergies: List[str] = None,
        cuisine_type: str = None,
        difficulty: str = None,
        cooking_time_max: int = None,
        category: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        根据条件搜索菜谱
        
        Args:
            dietary_preferences: 饮食偏好 (如: ["vegetarian", "low-carb"])
            allergies: 过敏信息 (如: ["nuts", "dairy"])
            cuisine_type: 菜系类型
            difficulty: 难度级别
            cooking_time_max: 最大烹饪时间（分钟）
            category: 菜谱分类
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 符合条件的菜谱列表
        """
        query = Recipe.query
        
        # 根据菜系类型过滤
        if cuisine_type:
            cuisine_keywords = RecipeQueryService._get_cuisine_keywords(cuisine_type)
            if cuisine_keywords:
                conditions = []
                for keyword in cuisine_keywords:
                    conditions.append(Recipe.name.contains(keyword))
                    conditions.append(Recipe.description.contains(keyword))
                query = query.filter(or_(*conditions))
        
        # 根据难度过滤
        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty)
        
        # 根据烹饪时间过滤
        if cooking_time_max:
            query = query.filter(Recipe.cooking_time <= cooking_time_max)
        
        # 根据分类过滤
        if category:
            query = query.filter(Recipe.category == category)
        
        # 获取菜谱
        recipes = query.limit(limit).all()
        
        # 过滤过敏原
        if allergies:
            recipes = RecipeQueryService._filter_by_allergies(recipes, allergies)
        
        # 根据饮食偏好过滤
        if dietary_preferences:
            recipes = RecipeQueryService._filter_by_dietary_preferences(recipes, dietary_preferences)
        
        return [RecipeQueryService._format_recipe_for_ai(recipe) for recipe in recipes]
    
    @staticmethod
    def get_recipes_by_ingredients(available_ingredients: List[str], limit: int = 10) -> List[Dict]:
        """
        根据现有食材推荐菜谱
        
        Args:
            available_ingredients: 可用食材列表
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 推荐的菜谱列表
        """
        if not available_ingredients:
            return []
        
        # 查找包含这些食材的菜谱
        ingredient_ids = db.session.query(Ingredient.id).filter(
            Ingredient.name.in_(available_ingredients)
        ).subquery()
        
        recipe_ids = db.session.query(RecipeIngredient.recipe_id).filter(
            RecipeIngredient.ingredient_id.in_(ingredient_ids)
        ).distinct().subquery()
        
        recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).limit(limit).all()
        
        return [RecipeQueryService._format_recipe_for_ai(recipe) for recipe in recipes]
    
    @staticmethod
    def get_popular_recipes(category: str = None, limit: int = 10) -> List[Dict]:
        """
        获取热门菜谱
        
        Args:
            category: 菜谱分类
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 热门菜谱列表
        """
        query = Recipe.query
        
        if category:
            query = query.filter(Recipe.category == category)
        
        # 按创建时间排序（可以后续改为按收藏数或评分排序）
        recipes = query.order_by(Recipe.created_at.desc()).limit(limit).all()
        
        return [RecipeQueryService._format_recipe_for_ai(recipe) for recipe in recipes]
    
    @staticmethod
    def get_recipes_by_nutrition_goals(
        high_protein: bool = False,
        low_carb: bool = False,
        low_fat: bool = False,
        limit: int = 10
    ) -> List[Dict]:
        """
        根据营养目标推荐菜谱
        
        Args:
            high_protein: 是否需要高蛋白
            low_carb: 是否需要低碳水
            low_fat: 是否需要低脂肪
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 符合营养目标的菜谱列表
        """
        # 这里可以根据菜谱名称和描述中的关键词来筛选
        # 实际应用中可以添加营养成分字段到数据库
        query = Recipe.query
        
        conditions = []
        
        if high_protein:
            protein_keywords = ['鸡胸肉', '牛肉', '鱼', '蛋', '豆腐', '虾']
            for keyword in protein_keywords:
                conditions.append(or_(
                    Recipe.name.contains(keyword),
                    Recipe.description.contains(keyword)
                ))
        
        if low_carb:
            # 避免高碳水食材
            carb_keywords = ['米饭', '面条', '面包', '土豆']
            for keyword in carb_keywords:
                query = query.filter(and_(
                    ~Recipe.name.contains(keyword),
                    ~Recipe.description.contains(keyword)
                ))
        
        if low_fat:
            # 避免高脂肪食材
            fat_keywords = ['油炸', '红烧', '糖醋']
            for keyword in fat_keywords:
                query = query.filter(and_(
                    ~Recipe.name.contains(keyword),
                    ~Recipe.description.contains(keyword)
                ))
        
        if conditions:
            query = query.filter(or_(*conditions))
        
        recipes = query.limit(limit).all()
        
        return [RecipeQueryService._format_recipe_for_ai(recipe) for recipe in recipes]
    
    @staticmethod
    def _format_recipe_for_ai(recipe: Recipe) -> Dict:
        """
        将菜谱格式化为AI友好的格式
        
        Args:
            recipe: 菜谱对象
            
        Returns:
            Dict: 格式化后的菜谱数据
        """
        # 获取食材信息
        ingredients = []
        for ri in recipe.recipe_ingredients:
            ingredient_info = {
                'name': ri.ingredient.name if ri.ingredient else '未知食材',
                'amount': ri.amount,
                'unit': ri.ingredient.unit if ri.ingredient else '',
                'note': ri.note or ''
            }
            ingredients.append(ingredient_info)
        
        # 获取步骤信息
        steps = []
        for step in recipe.steps.order_by(Step.step_number):
            steps.append({
                'step_number': step.step_number,
                'description': step.description
            })
        
        return {
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'difficulty': recipe.difficulty,
            'cooking_time': recipe.cooking_time,
            'servings': recipe.servings,
            'category': recipe.category,
            'ingredients': ingredients,
            'steps': steps,
            'ingredient_summary': [ing['name'] for ing in ingredients]
        }
    
    @staticmethod
    def _get_cuisine_keywords(cuisine_type: str) -> List[str]:
        """
        获取菜系关键词
        
        Args:
            cuisine_type: 菜系类型
            
        Returns:
            List[str]: 关键词列表
        """
        cuisine_keywords = {
            'chinese': ['川菜', '粤菜', '湘菜', '鲁菜', '苏菜', '浙菜', '闽菜', '徽菜', '中式', '炒', '蒸', '煮', '炖'],
            'western': ['西式', '意大利', '法式', '美式', '烤', '煎', '焗'],
            'japanese': ['日式', '寿司', '刺身', '天妇罗', '拉面', '味噌', '照烧'],
            'korean': ['韩式', '泡菜', '烤肉', '石锅', '辣椒酱'],
            'thai': ['泰式', '咖喱', '冬阴功', '柠檬草', '椰浆'],
            'italian': ['意式', '披萨', '意面', '芝士', '番茄'],
            'indian': ['印度', '咖喱', '香料', '烤饼'],
            'mexican': ['墨西哥', '玉米', '辣椒', '牛油果']
        }
        
        return cuisine_keywords.get(cuisine_type, [])
    
    @staticmethod
    def _filter_by_allergies(recipes: List[Recipe], allergies: List[str]) -> List[Recipe]:
        """
        根据过敏信息过滤菜谱
        
        Args:
            recipes: 菜谱列表
            allergies: 过敏信息列表
            
        Returns:
            List[Recipe]: 过滤后的菜谱列表
        """
        allergy_keywords = {
            'nuts': ['花生', '核桃', '杏仁', '腰果', '榛子', '坚果'],
            'dairy': ['牛奶', '奶酪', '黄油', '酸奶', '奶油'],
            'eggs': ['鸡蛋', '蛋', '蛋白', '蛋黄'],
            'seafood': ['鱼', '虾', '蟹', '贝', '海鲜'],
            'shellfish': ['虾', '蟹', '贝类', '扇贝', '生蚝'],
            'soy': ['豆腐', '豆浆', '酱油', '豆瓣酱', '大豆'],
            'wheat': ['面粉', '面条', '面包', '小麦'],
            'sesame': ['芝麻', '香油', '芝麻酱']
        }
        
        filtered_recipes = []
        
        for recipe in recipes:
            has_allergen = False
            
            # 检查菜谱名称和描述
            for allergy in allergies:
                keywords = allergy_keywords.get(allergy, [allergy])
                for keyword in keywords:
                    if keyword in recipe.name or keyword in (recipe.description or ''):
                        has_allergen = True
                        break
                if has_allergen:
                    break
            
            # 检查食材
            if not has_allergen:
                for ri in recipe.recipe_ingredients:
                    ingredient_name = ri.ingredient.name if ri.ingredient else ''
                    for allergy in allergies:
                        keywords = allergy_keywords.get(allergy, [allergy])
                        for keyword in keywords:
                            if keyword in ingredient_name:
                                has_allergen = True
                                break
                        if has_allergen:
                            break
                    if has_allergen:
                        break
            
            if not has_allergen:
                filtered_recipes.append(recipe)
        
        return filtered_recipes
    
    @staticmethod
    def _categorize_recipes_by_meal(recipes: List[Recipe]) -> Dict[str, List[Dict]]:
        """
        将菜谱按餐次分类
        
        Args:
            recipes: 菜谱列表
            
        Returns:
            Dict: 按餐次分类的菜谱
        """
        categorized = {
            'breakfast': [],
            'lunch': [],
            'dinner': []
        }
        
        for recipe in recipes:
            recipe_dict = RecipeQueryService._format_recipe_for_ai(recipe)
            
            # 根据菜谱类型和特征分类
            category = recipe.category.lower() if recipe.category else ''
            name = recipe.name.lower()
            
            # 早餐分类 - 轻食、粥类、简单快手菜
            if (any(keyword in category or keyword in name for keyword in ['早餐', 'breakfast', '粥', '包子', '豆浆', '油条', '蛋']) or
                (recipe.cooking_time and recipe.cooking_time <= 15 and any(keyword in name for keyword in ['蛋', '粥', '面包', '牛奶']))):
                categorized['breakfast'].append(recipe_dict)
            # 晚餐分类 - 汤类、炖菜、需要较长时间的菜
            elif (any(keyword in category or keyword in name for keyword in ['晚餐', 'dinner', '汤', '炖', '煲', '红烧']) or
                  (recipe.cooking_time and recipe.cooking_time >= 60)):
                categorized['dinner'].append(recipe_dict)
            # 午餐分类 - 家常菜、川菜、凉菜等主要菜品
            else:
                categorized['lunch'].append(recipe_dict)
        
        # 如果某个餐次没有菜谱，从其他餐次中分配一些
        total_recipes = len(recipes)
        if total_recipes > 0:
            # 确保每个餐次至少有一些菜谱
            if not categorized['breakfast'] and categorized['lunch']:
                # 将一些简单的午餐菜移到早餐
                simple_lunch = [r for r in categorized['lunch'] if r.get('difficulty') == '简单']
                if simple_lunch:
                    categorized['breakfast'].extend(simple_lunch[:2])
                    for recipe in simple_lunch[:2]:
                        categorized['lunch'].remove(recipe)
            
            if not categorized['dinner'] and categorized['lunch']:
                # 将一些午餐菜移到晚餐
                categorized['dinner'].extend(categorized['lunch'][-2:])
        
        return categorized
    
    @staticmethod
    def _filter_by_dietary_preferences(recipes: List[Recipe], dietary_preferences: List[str]) -> List[Recipe]:
        """
        根据饮食偏好过滤菜谱
        
        Args:
            recipes: 菜谱列表
            dietary_preferences: 饮食偏好列表
            
        Returns:
            List[Recipe]: 过滤后的菜谱列表
        """
        preference_keywords = {
            'vegetarian': {
                'exclude': ['肉', '鸡', '牛', '猪', '羊', '鱼', '虾', '蟹'],
                'include': []
            },
            'vegan': {
                'exclude': ['肉', '鸡', '牛', '猪', '羊', '鱼', '虾', '蟹', '蛋', '奶', '蜂蜜'],
                'include': []
            },
            'low-carb': {
                'exclude': ['米饭', '面条', '面包', '土豆', '红薯'],
                'include': []
            },
            'high-protein': {
                'exclude': [],
                'include': ['鸡胸肉', '牛肉', '鱼', '蛋', '豆腐', '虾']
            },
            'low-fat': {
                'exclude': ['油炸', '红烧', '糖醋', '肥肉'],
                'include': []
            }
        }
        
        filtered_recipes = []
        
        for recipe in recipes:
            matches_preferences = True
            
            for preference in dietary_preferences:
                if preference not in preference_keywords:
                    continue
                
                keywords = preference_keywords[preference]
                
                # 检查排除关键词
                for exclude_keyword in keywords['exclude']:
                    if (exclude_keyword in recipe.name or 
                        exclude_keyword in (recipe.description or '')):
                        matches_preferences = False
                        break
                    
                    # 检查食材
                    for ri in recipe.recipe_ingredients:
                        ingredient_name = ri.ingredient.name if ri.ingredient else ''
                        if exclude_keyword in ingredient_name:
                            matches_preferences = False
                            break
                    
                    if not matches_preferences:
                        break
                
                if not matches_preferences:
                    break
                
                # 检查包含关键词（如果有的话）
                if keywords['include']:
                    has_required = False
                    for include_keyword in keywords['include']:
                        if (include_keyword in recipe.name or 
                            include_keyword in (recipe.description or '')):
                            has_required = True
                            break
                        
                        # 检查食材
                        for ri in recipe.recipe_ingredients:
                            ingredient_name = ri.ingredient.name if ri.ingredient else ''
                            if include_keyword in ingredient_name:
                                has_required = True
                                break
                        
                        if has_required:
                            break
                    
                    if not has_required:
                        matches_preferences = False
                        break
            
            if matches_preferences:
                filtered_recipes.append(recipe)
        
        return filtered_recipes