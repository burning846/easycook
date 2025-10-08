#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜谱数据收集脚本
从多个数据源收集菜谱信息并存储到数据库
"""

import os
import sys
import json
import time
import random
import requests
from typing import List, Dict, Any
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.recipe import Recipe, Step
from app.models.ingredient import Ingredient, RecipeIngredient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recipe_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RecipeCollector:
    """菜谱收集器"""
    
    def __init__(self):
        self.app = create_app()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # 预定义的中文菜谱数据
        self.sample_recipes = [
            {
                "name": "宫保鸡丁",
                "description": "经典川菜，酸甜微辣，口感丰富",
                "category": "川菜",
                "difficulty": "中等",
                "cooking_time": 25,
                "ingredients": [
                    {"name": "鸡胸肉", "amount": 300, "unit": "克"},
                    {"name": "花生米", "amount": 100, "unit": "克"},
                    {"name": "干辣椒", "amount": 10, "unit": "个"},
                    {"name": "花椒", "amount": 1, "unit": "茶匙"},
                    {"name": "葱", "amount": 2, "unit": "根"},
                    {"name": "姜", "amount": 10, "unit": "克"},
                    {"name": "蒜", "amount": 3, "unit": "瓣"},
                    {"name": "生抽", "amount": 2, "unit": "汤匙"},
                    {"name": "老抽", "amount": 1, "unit": "茶匙"},
                    {"name": "料酒", "amount": 1, "unit": "汤匙"},
                    {"name": "糖", "amount": 1, "unit": "汤匙"},
                    {"name": "醋", "amount": 1, "unit": "茶匙"},
                    {"name": "淀粉", "amount": 1, "unit": "汤匙"},
                    {"name": "食用油", "amount": 3, "unit": "汤匙"}
                ],
                "steps": [
                    "鸡胸肉切丁，用料酒、生抽、淀粉腌制15分钟",
                    "花生米用油炸至金黄色，捞起备用",
                    "热锅下油，爆香干辣椒和花椒",
                    "下鸡丁炒至变色",
                    "加入葱姜蒜爆香",
                    "调入生抽、老抽、糖、醋炒匀",
                    "最后加入花生米炒匀即可"
                ]
            },
            {
                "name": "红烧肉",
                "description": "传统家常菜，肥而不腻，入口即化",
                "category": "家常菜",
                "difficulty": "中等",
                "cooking_time": 90,
                "ingredients": [
                    {"name": "五花肉", "amount": 500, "unit": "克"},
                    {"name": "冰糖", "amount": 30, "unit": "克"},
                    {"name": "生抽", "amount": 3, "unit": "汤匙"},
                    {"name": "老抽", "amount": 1, "unit": "汤匙"},
                    {"name": "料酒", "amount": 2, "unit": "汤匙"},
                    {"name": "葱", "amount": 2, "unit": "根"},
                    {"name": "姜", "amount": 15, "unit": "克"},
                    {"name": "八角", "amount": 2, "unit": "个"},
                    {"name": "桂皮", "amount": 1, "unit": "小段"},
                    {"name": "香叶", "amount": 2, "unit": "片"}
                ],
                "steps": [
                    "五花肉切块，冷水下锅焯水去腥",
                    "热锅下冰糖炒糖色至焦糖色",
                    "下五花肉炒至上色",
                    "加入料酒、生抽、老抽炒匀",
                    "加入葱姜和香料",
                    "加开水没过肉块，大火烧开",
                    "转小火炖煮1小时至软烂",
                    "大火收汁即可"
                ]
            },
            {
                "name": "麻婆豆腐",
                "description": "四川名菜，麻辣鲜香，嫩滑爽口",
                "category": "川菜",
                "difficulty": "简单",
                "cooking_time": 20,
                "ingredients": [
                    {"name": "嫩豆腐", "amount": 400, "unit": "克"},
                    {"name": "牛肉末", "amount": 100, "unit": "克"},
                    {"name": "豆瓣酱", "amount": 2, "unit": "汤匙"},
                    {"name": "花椒粉", "amount": 1, "unit": "茶匙"},
                    {"name": "葱", "amount": 2, "unit": "根"},
                    {"name": "姜", "amount": 10, "unit": "克"},
                    {"name": "蒜", "amount": 3, "unit": "瓣"},
                    {"name": "生抽", "amount": 1, "unit": "汤匙"},
                    {"name": "淀粉", "amount": 1, "unit": "汤匙"},
                    {"name": "食用油", "amount": 2, "unit": "汤匙"}
                ],
                "steps": [
                    "豆腐切块，用盐水焯一下",
                    "热锅下油，炒牛肉末至变色",
                    "加入豆瓣酱炒出红油",
                    "加入葱姜蒜爆香",
                    "加水烧开，下豆腐块",
                    "用水淀粉勾芡",
                    "撒上花椒粉和葱花即可"
                ]
            },
            {
                "name": "糖醋里脊",
                "description": "酸甜可口的经典菜品，老少皆宜",
                "category": "家常菜",
                "difficulty": "中等",
                "cooking_time": 30,
                "ingredients": [
                    {"name": "里脊肉", "amount": 300, "unit": "克"},
                    {"name": "鸡蛋", "amount": 1, "unit": "个"},
                    {"name": "淀粉", "amount": 50, "unit": "克"},
                    {"name": "面粉", "amount": 30, "unit": "克"},
                    {"name": "番茄酱", "amount": 3, "unit": "汤匙"},
                    {"name": "白糖", "amount": 2, "unit": "汤匙"},
                    {"name": "白醋", "amount": 2, "unit": "汤匙"},
                    {"name": "生抽", "amount": 1, "unit": "茶匙"},
                    {"name": "食用油", "amount": 500, "unit": "毫升"}
                ],
                "steps": [
                    "里脊肉切条，用盐和料酒腌制",
                    "调制面糊：鸡蛋、淀粉、面粉加水调匀",
                    "肉条裹面糊，油炸至金黄",
                    "调糖醋汁：番茄酱、糖、醋、生抽",
                    "热锅下糖醋汁炒至浓稠",
                    "倒入炸好的里脊条炒匀即可"
                ]
            },
            {
                "name": "鱼香茄子",
                "description": "川菜经典，茄子软糯，鱼香味浓",
                "category": "川菜",
                "difficulty": "简单",
                "cooking_time": 25,
                "ingredients": [
                    {"name": "茄子", "amount": 2, "unit": "根"},
                    {"name": "肉末", "amount": 100, "unit": "克"},
                    {"name": "豆瓣酱", "amount": 1, "unit": "汤匙"},
                    {"name": "葱", "amount": 2, "unit": "根"},
                    {"name": "姜", "amount": 10, "unit": "克"},
                    {"name": "蒜", "amount": 3, "unit": "瓣"},
                    {"name": "生抽", "amount": 2, "unit": "汤匙"},
                    {"name": "老抽", "amount": 1, "unit": "茶匙"},
                    {"name": "糖", "amount": 1, "unit": "汤匙"},
                    {"name": "醋", "amount": 1, "unit": "茶匙"},
                    {"name": "淀粉", "amount": 1, "unit": "汤匙"},
                    {"name": "食用油", "amount": 3, "unit": "汤匙"}
                ],
                "steps": [
                    "茄子切条，用盐腌制10分钟",
                    "热锅下油，炸茄子至软身",
                    "另起锅炒肉末至变色",
                    "加入豆瓣酱炒出红油",
                    "加入葱姜蒜爆香",
                    "调入生抽、老抽、糖、醋",
                    "倒入茄子炒匀，用淀粉勾芡即可"
                ]
            },
            {
                "name": "白切鸡",
                "description": "粤菜经典，鸡肉嫩滑，清香不腻",
                "category": "粤菜",
                "difficulty": "简单",
                "cooking_time": 40,
                "ingredients": [
                    {"name": "土鸡", "amount": 1, "unit": "只"},
                    {"name": "姜", "amount": 30, "unit": "克"},
                    {"name": "葱", "amount": 3, "unit": "根"},
                    {"name": "料酒", "amount": 2, "unit": "汤匙"},
                    {"name": "盐", "amount": 1, "unit": "茶匙"},
                    {"name": "生抽", "amount": 3, "unit": "汤匙"},
                    {"name": "香油", "amount": 1, "unit": "茶匙"},
                    {"name": "白糖", "amount": 1, "unit": "茶匙"}
                ],
                "steps": [
                    "鸡洗净，用盐和料酒腌制30分钟",
                    "锅内加水，放入姜片和葱段",
                    "水开后放入鸡，煮25分钟",
                    "关火焖10分钟",
                    "捞起鸡放入冰水中冷却",
                    "调蘸料：生抽、香油、糖、姜蓉",
                    "鸡切块装盘，配蘸料食用"
                ]
            },
            {
                "name": "蒸蛋羹",
                "description": "嫩滑如豆腐的蒸蛋，营养丰富",
                "category": "家常菜",
                "difficulty": "简单",
                "cooking_time": 15,
                "ingredients": [
                    {"name": "鸡蛋", "amount": 3, "unit": "个"},
                    {"name": "温水", "amount": 150, "unit": "毫升"},
                    {"name": "盐", "amount": 0.5, "unit": "茶匙"},
                    {"name": "生抽", "amount": 1, "unit": "茶匙"},
                    {"name": "香油", "amount": 0.5, "unit": "茶匙"},
                    {"name": "葱花", "amount": 1, "unit": "汤匙"}
                ],
                "steps": [
                    "鸡蛋打散，加盐调味",
                    "加入温水搅拌均匀",
                    "过筛去除泡沫",
                    "蒸锅水开后放入蛋液",
                    "盖上盘子，蒸10分钟",
                    "出锅后淋生抽和香油",
                    "撒上葱花即可"
                ]
            },
            {
                "name": "西红柿鸡蛋面",
                "description": "简单快手的家常面条，酸甜开胃",
                "category": "面食",
                "difficulty": "简单",
                "cooking_time": 15,
                "ingredients": [
                    {"name": "挂面", "amount": 200, "unit": "克"},
                    {"name": "西红柿", "amount": 2, "unit": "个"},
                    {"name": "鸡蛋", "amount": 2, "unit": "个"},
                    {"name": "葱", "amount": 1, "unit": "根"},
                    {"name": "蒜", "amount": 2, "unit": "瓣"},
                    {"name": "生抽", "amount": 1, "unit": "汤匙"},
                    {"name": "盐", "amount": 1, "unit": "茶匙"},
                    {"name": "糖", "amount": 0.5, "unit": "茶匙"},
                    {"name": "食用油", "amount": 2, "unit": "汤匙"}
                ],
                "steps": [
                    "西红柿去皮切块",
                    "鸡蛋打散炒熟盛起",
                    "热锅下油爆香蒜末",
                    "下西红柿炒出汁水",
                    "加水烧开，下面条",
                    "面条快熟时加入鸡蛋",
                    "调味后撒葱花即可"
                ]
            },
            {
                "name": "可乐鸡翅",
                "description": "孩子最爱的甜味鸡翅，简单易做",
                "category": "家常菜",
                "difficulty": "简单",
                "cooking_time": 30,
                "ingredients": [
                    {"name": "鸡翅", "amount": 8, "unit": "个"},
                    {"name": "可乐", "amount": 250, "unit": "毫升"},
                    {"name": "生抽", "amount": 2, "unit": "汤匙"},
                    {"name": "老抽", "amount": 1, "unit": "茶匙"},
                    {"name": "料酒", "amount": 1, "unit": "汤匙"},
                    {"name": "姜", "amount": 10, "unit": "克"},
                    {"name": "葱", "amount": 1, "unit": "根"},
                    {"name": "食用油", "amount": 1, "unit": "汤匙"}
                ],
                "steps": [
                    "鸡翅洗净，两面划几刀",
                    "用料酒腌制15分钟",
                    "热锅下油，煎鸡翅至两面金黄",
                    "加入姜片和葱段爆香",
                    "倒入可乐没过鸡翅",
                    "加生抽和老抽调色",
                    "大火烧开转小火炖20分钟",
                    "大火收汁即可"
                ]
            },
            {
                "name": "蒜蓉西兰花",
                "description": "清爽健康的素菜，营养价值高",
                "category": "素菜",
                "difficulty": "简单",
                "cooking_time": 10,
                "ingredients": [
                    {"name": "西兰花", "amount": 300, "unit": "克"},
                    {"name": "蒜", "amount": 4, "unit": "瓣"},
                    {"name": "生抽", "amount": 1, "unit": "汤匙"},
                    {"name": "盐", "amount": 0.5, "unit": "茶匙"},
                    {"name": "食用油", "amount": 2, "unit": "汤匙"},
                    {"name": "鸡精", "amount": 0.5, "unit": "茶匙"}
                ],
                "steps": [
                    "西兰花切小朵，焯水1分钟",
                    "蒜切末备用",
                    "热锅下油，爆香蒜末",
                    "下西兰花大火炒1分钟",
                    "加生抽、盐、鸡精调味",
                    "炒匀即可出锅"
                ]
            }
        ]
    
    def get_or_create_ingredient(self, name: str, unit: str = "克") -> Ingredient:
        """获取或创建食材"""
        ingredient = Ingredient.query.filter_by(name=name).first()
        if not ingredient:
            ingredient = Ingredient(
                name=name,
                category="其他",
                unit=unit
            )
            db.session.add(ingredient)
            db.session.flush()
        return ingredient
    
    def save_recipe_to_db(self, recipe_data: Dict[str, Any]) -> bool:
        """保存菜谱到数据库"""
        try:
            # 检查菜谱是否已存在
            existing_recipe = Recipe.query.filter_by(name=recipe_data['name']).first()
            if existing_recipe:
                logger.info(f"菜谱 '{recipe_data['name']}' 已存在，跳过")
                return False
            
            # 创建菜谱
            recipe = Recipe(
                name=recipe_data['name'],
                description=recipe_data.get('description', ''),
                category=recipe_data.get('category', '家常菜'),
                difficulty=recipe_data.get('difficulty', '中等'),
                cooking_time=recipe_data.get('cooking_time', 30),
                image_url=recipe_data.get('image_url', f'https://example.com/{recipe_data["name"]}.jpg')
            )
            
            db.session.add(recipe)
            db.session.flush()  # 获取recipe.id
            
            # 添加制作步骤
            for i, step_content in enumerate(recipe_data.get('steps', []), 1):
                step = Step(
                    recipe_id=recipe.id,
                    step_number=i,
                    description=step_content
                )
                db.session.add(step)
            
            # 添加食材
            for ingredient_data in recipe_data.get('ingredients', []):
                ingredient = self.get_or_create_ingredient(
                    ingredient_data['name'], 
                    ingredient_data.get('unit', '克')
                )
                
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    amount=ingredient_data.get('amount', 0),
                    note=ingredient_data.get('note', '')
                )
                db.session.add(recipe_ingredient)
            
            db.session.commit()
            logger.info(f"成功保存菜谱: {recipe_data['name']}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存菜谱失败 {recipe_data['name']}: {str(e)}")
            return False
    
    def collect_sample_recipes(self) -> int:
        """收集预定义的示例菜谱"""
        success_count = 0
        
        with self.app.app_context():
            for recipe_data in self.sample_recipes:
                if self.save_recipe_to_db(recipe_data):
                    success_count += 1
                
                # 添加延迟避免过快操作
                time.sleep(0.1)
        
        return success_count
    
    def collect_from_api(self, api_url: str, params: Dict[str, Any] = None) -> int:
        """从API收集菜谱数据"""
        success_count = 0
        
        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"从API获取到数据: {api_url}")
            
            # 这里需要根据具体API的响应格式来解析数据
            # 由于不同API格式不同，这里只是示例框架
            
        except Exception as e:
            logger.error(f"从API收集数据失败 {api_url}: {str(e)}")
        
        return success_count
    
    def run_collection(self):
        """运行数据收集"""
        logger.info("开始收集菜谱数据...")
        
        total_collected = 0
        
        # 收集预定义的示例菜谱
        logger.info("收集预定义菜谱...")
        sample_count = self.collect_sample_recipes()
        total_collected += sample_count
        logger.info(f"收集预定义菜谱完成，成功: {sample_count}")
        
        logger.info(f"数据收集完成，总共收集: {total_collected} 个菜谱")
        return total_collected

def main():
    """主函数"""
    collector = RecipeCollector()
    
    try:
        total = collector.run_collection()
        print(f"\n✅ 菜谱数据收集完成！")
        print(f"📊 总共收集: {total} 个菜谱")
        print(f"📝 详细日志请查看: recipe_collection.log")
        
    except Exception as e:
        logger.error(f"数据收集过程中出现错误: {str(e)}")
        print(f"\n❌ 数据收集失败: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())