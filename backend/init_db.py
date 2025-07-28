import os
import sys
from datetime import datetime, timedelta
import random

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.recipe import Recipe, Step
from app.models.ingredient import Ingredient, RecipeIngredient
from app.models.user import User, UserIngredient, ShoppingList, ShoppingListItem, UserPreference
from app.models.favorite import FavoriteRecipe

app = create_app()

def init_db():
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有数据
        if Ingredient.query.count() > 0:
            print("数据库已初始化，跳过")
            return
        
        # 添加食材
        ingredients = [
            # 肉类
            Ingredient(name="猪肉", unit="克", category="肉类"),
            Ingredient(name="牛肉", unit="克", category="肉类"),
            Ingredient(name="鸡胸肉", unit="克", category="肉类"),
            Ingredient(name="鸡腿", unit="个", category="肉类"),
            Ingredient(name="五花肉", unit="克", category="肉类"),
            
            # 蔬菜
            Ingredient(name="西红柿", unit="个", category="蔬菜"),
            Ingredient(name="黄瓜", unit="根", category="蔬菜"),
            Ingredient(name="土豆", unit="个", category="蔬菜"),
            Ingredient(name="洋葱", unit="个", category="蔬菜"),
            Ingredient(name="胡萝卜", unit="根", category="蔬菜"),
            Ingredient(name="青椒", unit="个", category="蔬菜"),
            Ingredient(name="白菜", unit="颗", category="蔬菜"),
            Ingredient(name="菠菜", unit="把", category="蔬菜"),
            Ingredient(name="生菜", unit="颗", category="蔬菜"),
            Ingredient(name="豆芽", unit="把", category="蔬菜"),
            
            # 调味料
            Ingredient(name="盐", unit="克", category="调味料"),
            Ingredient(name="糖", unit="克", category="调味料"),
            Ingredient(name="生抽", unit="毫升", category="调味料"),
            Ingredient(name="老抽", unit="毫升", category="调味料"),
            Ingredient(name="料酒", unit="毫升", category="调味料"),
            Ingredient(name="醋", unit="毫升", category="调味料"),
            Ingredient(name="蚝油", unit="毫升", category="调味料"),
            Ingredient(name="花椒", unit="克", category="调味料"),
            Ingredient(name="八角", unit="个", category="调味料"),
            Ingredient(name="辣椒粉", unit="克", category="调味料"),
            
            # 主食
            Ingredient(name="米饭", unit="克", category="主食"),
            Ingredient(name="面条", unit="克", category="主食"),
            Ingredient(name="面粉", unit="克", category="主食"),
            
            # 其他
            Ingredient(name="鸡蛋", unit="个", category="其他"),
            Ingredient(name="豆腐", unit="块", category="其他"),
            Ingredient(name="香菇", unit="朵", category="其他"),
            Ingredient(name="木耳", unit="把", category="其他"),
            Ingredient(name="葱", unit="根", category="其他"),
            Ingredient(name="姜", unit="块", category="其他"),
            Ingredient(name="蒜", unit="瓣", category="其他"),
        ]
        
        for ingredient in ingredients:
            db.session.add(ingredient)
        
        db.session.commit()
        print(f"添加了 {len(ingredients)} 种食材")
        
        # 添加菜谱
        recipes = [
            {
                "name": "西红柿炒鸡蛋",
                "description": "家常美味，简单易做",
                "cooking_time": 15,
                "difficulty": "简单",
                "category": "家常菜",
                "image_url": "https://example.com/tomato_egg.jpg",
                "steps": [
                    {"step_number": 1, "description": "西红柿切块，鸡蛋打散", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "锅中倒油，油热后倒入鸡蛋翻炒至金黄", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "倒入西红柿翻炒，加入适量盐和糖", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "炒至西红柿软烂出汁，撒上葱花即可", "image_url": "https://example.com/step4.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "西红柿", "amount": 2, "note": "切块"},
                    {"ingredient_name": "鸡蛋", "amount": 3, "note": "打散"},
                    {"ingredient_name": "盐", "amount": 2, "note": "适量"},
                    {"ingredient_name": "糖", "amount": 5, "note": "适量"},
                    {"ingredient_name": "葱", "amount": 1, "note": "切段"},
                ]
            },
            {
                "name": "土豆炖牛肉",
                "description": "营养丰富，味道浓郁",
                "cooking_time": 90,
                "difficulty": "中等",
                "category": "炖菜",
                "image_url": "https://example.com/beef_potato.jpg",
                "steps": [
                    {"step_number": 1, "description": "牛肉切块，土豆切块", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "锅中倒油，放入姜片和牛肉翻炒至变色", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "加入料酒、生抽、老抽、八角，倒入没过牛肉的水", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "大火烧开后转小火炖40分钟", "image_url": "https://example.com/step4.jpg"},
                    {"step_number": 5, "description": "放入土豆继续炖30分钟，加盐调味即可", "image_url": "https://example.com/step5.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "牛肉", "amount": 500, "note": "切块"},
                    {"ingredient_name": "土豆", "amount": 3, "note": "切块"},
                    {"ingredient_name": "姜", "amount": 1, "note": "切片"},
                    {"ingredient_name": "料酒", "amount": 15, "note": "调味"},
                    {"ingredient_name": "生抽", "amount": 15, "note": "调味"},
                    {"ingredient_name": "老抽", "amount": 5, "note": "调色"},
                    {"ingredient_name": "八角", "amount": 2, "note": "增香"},
                    {"ingredient_name": "盐", "amount": 5, "note": "调味"},
                ]
            },
            {
                "name": "青椒炒肉",
                "description": "下饭神器，香辣可口",
                "cooking_time": 20,
                "difficulty": "简单",
                "category": "家常菜",
                "image_url": "https://example.com/pepper_pork.jpg",
                "steps": [
                    {"step_number": 1, "description": "猪肉切片，青椒切块", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "猪肉加入生抽、料酒、淀粉腌制10分钟", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "锅中倒油，放入蒜末爆香，倒入猪肉翻炒至变色", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "加入青椒翻炒，加盐、生抽调味即可", "image_url": "https://example.com/step4.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "猪肉", "amount": 300, "note": "切片"},
                    {"ingredient_name": "青椒", "amount": 3, "note": "切块"},
                    {"ingredient_name": "蒜", "amount": 3, "note": "切末"},
                    {"ingredient_name": "生抽", "amount": 10, "note": "调味"},
                    {"ingredient_name": "料酒", "amount": 5, "note": "去腥"},
                    {"ingredient_name": "盐", "amount": 3, "note": "调味"},
                ]
            },
            {
                "name": "麻婆豆腐",
                "description": "川菜经典，麻辣鲜香",
                "cooking_time": 30,
                "difficulty": "中等",
                "category": "川菜",
                "image_url": "https://example.com/mapo_tofu.jpg",
                "steps": [
                    {"step_number": 1, "description": "豆腐切块，猪肉剁成肉末", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "锅中倒油，放入花椒和辣椒粉炒出香味", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "加入肉末翻炒至变色，加入豆瓣酱继续翻炒", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "倒入适量水，放入豆腐块，小火煮5分钟", "image_url": "https://example.com/step4.jpg"},
                    {"step_number": 5, "description": "加入盐、糖、生抽调味，勾芡后撒上葱花即可", "image_url": "https://example.com/step5.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "豆腐", "amount": 1, "note": "切块"},
                    {"ingredient_name": "猪肉", "amount": 100, "note": "剁成肉末"},
                    {"ingredient_name": "花椒", "amount": 5, "note": "炒香"},
                    {"ingredient_name": "辣椒粉", "amount": 10, "note": "增辣"},
                    {"ingredient_name": "盐", "amount": 3, "note": "调味"},
                    {"ingredient_name": "糖", "amount": 5, "note": "提鲜"},
                    {"ingredient_name": "生抽", "amount": 10, "note": "调味"},
                    {"ingredient_name": "葱", "amount": 1, "note": "切花"},
                ]
            },
            {
                "name": "蔬菜沙拉",
                "description": "健康低卡，清爽可口",
                "cooking_time": 10,
                "difficulty": "简单",
                "category": "凉菜",
                "image_url": "https://example.com/salad.jpg",
                "steps": [
                    {"step_number": 1, "description": "生菜洗净撕小块，黄瓜切片，西红柿切块", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "将所有蔬菜放入大碗中", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "调制酱汁：橄榄油、柠檬汁、盐、黑胡椒混合", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "将酱汁淋在蔬菜上，轻轻拌匀即可", "image_url": "https://example.com/step4.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "生菜", "amount": 1, "note": "撕小块"},
                    {"ingredient_name": "黄瓜", "amount": 1, "note": "切片"},
                    {"ingredient_name": "西红柿", "amount": 1, "note": "切块"},
                    {"ingredient_name": "盐", "amount": 2, "note": "调味"},
                ]
            },
            {
                "name": "红烧鱼",
                "description": "鲜香美味，色泽红亮",
                "cooking_time": 40,
                "difficulty": "中等",
                "category": "家常菜",
                "image_url": "https://example.com/braised_fish.jpg",
                "steps": [
                    {"step_number": 1, "description": "鱼洗净，两面划几刀，用盐、料酒腌制10分钟", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "锅中倒油，油热后放入鱼煎至两面金黄", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "加入葱姜蒜爆香，倒入生抽、老抽、料酒", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "加入适量水，大火烧开后转小火焖煮15分钟", "image_url": "https://example.com/step4.jpg"},
                    {"step_number": 5, "description": "大火收汁，撒上葱花即可", "image_url": "https://example.com/step5.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "鱼", "amount": 1, "note": "洗净"},
                    {"ingredient_name": "葱", "amount": 2, "note": "切段"},
                    {"ingredient_name": "姜", "amount": 1, "note": "切片"},
                    {"ingredient_name": "蒜", "amount": 3, "note": "拍碎"},
                    {"ingredient_name": "生抽", "amount": 15, "note": "调味"},
                    {"ingredient_name": "老抽", "amount": 5, "note": "上色"},
                    {"ingredient_name": "料酒", "amount": 10, "note": "去腥"},
                    {"ingredient_name": "盐", "amount": 3, "note": "调味"},
                ]
            },
            {
                "name": "宫保鸡丁",
                "description": "经典川菜，麻辣鲜香",
                "cooking_time": 25,
                "difficulty": "中等",
                "category": "川菜",
                "image_url": "https://example.com/kungpao_chicken.jpg",
                "steps": [
                    {"step_number": 1, "description": "鸡胸肉切丁，用盐、料酒、淀粉腌制10分钟", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "青椒、红椒切丁，花生米准备好", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "锅中倒油，放入干辣椒和花椒炒香", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "放入鸡丁翻炒至变色，加入青红椒丁继续翻炒", "image_url": "https://example.com/step4.jpg"},
                    {"step_number": 5, "description": "加入盐、糖、醋、生抽调味，放入花生米翻炒均匀即可", "image_url": "https://example.com/step5.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "鸡胸肉", "amount": 300, "note": "切丁"},
                    {"ingredient_name": "青椒", "amount": 1, "note": "切丁"},
                    {"ingredient_name": "花椒", "amount": 5, "note": "炒香"},
                    {"ingredient_name": "醋", "amount": 10, "note": "提味"},
                    {"ingredient_name": "生抽", "amount": 15, "note": "调味"},
                    {"ingredient_name": "盐", "amount": 3, "note": "调味"},
                    {"ingredient_name": "糖", "amount": 5, "note": "调味"},
                ]
            },
            {
                "name": "清蒸鲈鱼",
                "description": "鲜嫩可口，营养丰富",
                "cooking_time": 20,
                "difficulty": "简单",
                "category": "粤菜",
                "image_url": "https://example.com/steamed_fish.jpg",
                "steps": [
                    {"step_number": 1, "description": "鲈鱼洗净，两面划几刀，用盐、料酒腌制10分钟", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "葱切丝，姜切片，铺在盘底", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "将鱼放在葱姜上，上锅蒸10分钟", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "取出鱼，倒掉盘中水分，撒上葱丝", "image_url": "https://example.com/step4.jpg"},
                    {"step_number": 5, "description": "锅中热油，浇在葱丝上，淋上生抽即可", "image_url": "https://example.com/step5.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "鱼", "amount": 1, "note": "洗净"},
                    {"ingredient_name": "葱", "amount": 2, "note": "切丝"},
                    {"ingredient_name": "姜", "amount": 1, "note": "切片"},
                    {"ingredient_name": "生抽", "amount": 10, "note": "调味"},
                    {"ingredient_name": "料酒", "amount": 5, "note": "去腥"},
                    {"ingredient_name": "盐", "amount": 3, "note": "调味"},
                ]
            },
            {
                "name": "糖醋排骨",
                "description": "酸甜可口，色泽诱人",
                "cooking_time": 45,
                "difficulty": "中等",
                "category": "家常菜",
                "image_url": "https://example.com/sweet_sour_ribs.jpg",
                "steps": [
                    {"step_number": 1, "description": "排骨洗净，切段，用清水浸泡30分钟去血水", "image_url": "https://example.com/step1.jpg"},
                    {"step_number": 2, "description": "锅中倒油，放入排骨煎至两面金黄", "image_url": "https://example.com/step2.jpg"},
                    {"step_number": 3, "description": "加入料酒、生抽、醋、糖、适量水", "image_url": "https://example.com/step3.jpg"},
                    {"step_number": 4, "description": "大火烧开后转小火焖煮20分钟", "image_url": "https://example.com/step4.jpg"},
                    {"step_number": 5, "description": "大火收汁，撒上葱花即可", "image_url": "https://example.com/step5.jpg"},
                ],
                "ingredients": [
                    {"ingredient_name": "排骨", "amount": 500, "note": "切段"},
                    {"ingredient_name": "葱", "amount": 1, "note": "切段"},
                    {"ingredient_name": "料酒", "amount": 10, "note": "去腥"},
                    {"ingredient_name": "生抽", "amount": 15, "note": "调味"},
                    {"ingredient_name": "醋", "amount": 20, "note": "提味"},
                    {"ingredient_name": "糖", "amount": 30, "note": "调味"},
                ]
            },
        ]
        
        for recipe_data in recipes:
            recipe = Recipe(
                name=recipe_data["name"],
                description=recipe_data["description"],
                cooking_time=recipe_data["cooking_time"],
                difficulty=recipe_data["difficulty"],
                category=recipe_data["category"],
                image_url=recipe_data["image_url"]
            )
            db.session.add(recipe)
            db.session.flush()  # 获取 recipe.id
            
            # 添加步骤
            for step_data in recipe_data["steps"]:
                step = Step(
                    recipe_id=recipe.id,
                    step_number=step_data["step_number"],
                    description=step_data["description"],
                    image_url=step_data["image_url"]
                )
                db.session.add(step)
            
            # 添加食材
            for ingredient_data in recipe_data["ingredients"]:
                ingredient = Ingredient.query.filter_by(name=ingredient_data["ingredient_name"]).first()
                if ingredient:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        amount=ingredient_data["amount"],
                        note=ingredient_data.get("note", "")
                    )
                    db.session.add(recipe_ingredient)
        
        db.session.commit()
        print(f"添加了 {len(recipes)} 个菜谱")
        
        # 添加测试用户
        users = [
            {
                "username": "test_user",
                "email": "test@example.com",
                "password": "password123",
                "google_id": None
            },
            {
                "username": "google_user",
                "email": "google@example.com",
                "password": "google123",
                "google_id": "google_123456789"
            },
            {
                "username": "food_lover",
                "email": "foodlover@example.com",
                "password": "ilovefood",
                "google_id": None
            }
        ]
        
        created_users = []
        for user_data in users:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                google_id=user_data["google_id"]
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.flush()  # 获取 user.id
            created_users.append(user)
        
        test_user = created_users[0]
        
        # 添加用户食材库
        user_ingredients = [
            {"ingredient_name": "鸡蛋", "amount": 6, "expiry_date": datetime.now() + timedelta(days=14)},
            {"ingredient_name": "西红柿", "amount": 3, "expiry_date": datetime.now() + timedelta(days=5)},
            {"ingredient_name": "黄瓜", "amount": 2, "expiry_date": datetime.now() + timedelta(days=7)},
            {"ingredient_name": "盐", "amount": 500, "expiry_date": datetime.now() + timedelta(days=365)},
            {"ingredient_name": "糖", "amount": 400, "expiry_date": datetime.now() + timedelta(days=365)},
        ]
        
        for ingredient_data in user_ingredients:
            ingredient = Ingredient.query.filter_by(name=ingredient_data["ingredient_name"]).first()
            if ingredient:
                user_ingredient = UserIngredient(
                    user_id=test_user.id,
                    ingredient_id=ingredient.id,
                    amount=ingredient_data["amount"],
                    expiry_date=ingredient_data["expiry_date"]
                )
                db.session.add(user_ingredient)
        
        # 添加购物清单
        shopping_list = ShoppingList(
            user_id=test_user.id,
            name="周末采购"
        )
        db.session.add(shopping_list)
        db.session.flush()  # 获取 shopping_list.id
        
        # 添加购物清单项
        shopping_items = [
            {"ingredient_name": "猪肉", "amount": 500, "purchased": False},
            {"ingredient_name": "青椒", "amount": 3, "purchased": False},
            {"ingredient_name": "土豆", "amount": 4, "purchased": True},
        ]
        
        for item_data in shopping_items:
            ingredient = Ingredient.query.filter_by(name=item_data["ingredient_name"]).first()
            if ingredient:
                shopping_item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=ingredient.id,
                    amount=item_data["amount"],
                    is_purchased=item_data["purchased"]
                )
                db.session.add(shopping_item)
        
        # 添加用户偏好
        preferences = [
            {"preference_type": "disliked_ingredient", "value": "洋葱"},
            {"preference_type": "preferred_category", "value": "家常菜"},
            {"preference_type": "health_preference", "value": "low_calorie"}
        ]
        
        for pref in preferences:
            user_pref = UserPreference(
                user_id=test_user.id,
                preference_type=pref["preference_type"],
                value=pref["value"]
            )
            db.session.add(user_pref)
        
        # 添加收藏菜谱
        # 为第一个用户添加收藏
        favorite_recipes_user1 = [
            {"recipe_name": "西红柿炒鸡蛋"},
            {"recipe_name": "土豆炖牛肉"},
            {"recipe_name": "宫保鸡丁"}
        ]
        
        for fav_data in favorite_recipes_user1:
            recipe = Recipe.query.filter_by(name=fav_data["recipe_name"]).first()
            if recipe:
                favorite = FavoriteRecipe(
                    user_id=created_users[0].id,
                    recipe_id=recipe.id,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(favorite)
        
        # 为第二个用户添加收藏
        favorite_recipes_user2 = [
            {"recipe_name": "麻婆豆腐"},
            {"recipe_name": "清蒸鲈鱼"},
            {"recipe_name": "糖醋排骨"},
            {"recipe_name": "红烧鱼"}
        ]
        
        for fav_data in favorite_recipes_user2:
            recipe = Recipe.query.filter_by(name=fav_data["recipe_name"]).first()
            if recipe:
                favorite = FavoriteRecipe(
                    user_id=created_users[1].id,
                    recipe_id=recipe.id,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(favorite)
        
        # 为第三个用户添加收藏
        favorite_recipes_user3 = [
            {"recipe_name": "西红柿炒鸡蛋"},
            {"recipe_name": "青椒炒肉"},
            {"recipe_name": "蔬菜沙拉"},
            {"recipe_name": "宫保鸡丁"},
            {"recipe_name": "糖醋排骨"}
        ]
        
        for fav_data in favorite_recipes_user3:
            recipe = Recipe.query.filter_by(name=fav_data["recipe_name"]).first()
            if recipe:
                favorite = FavoriteRecipe(
                    user_id=created_users[2].id,
                    recipe_id=recipe.id,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(favorite)
        
        db.session.commit()
        print(f"添加了{len(created_users)}个测试用户和相关数据，包括收藏菜谱")

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成")