import asyncio
import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
from bson import ObjectId
import pytz

# Adjust path to import backend modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import db as database_instance, get_database
from backend.models import Dish, User, LogBehavior

# Timezone configuration
TZ_SHANGHAI = pytz.timezone('Asia/Shanghai')

async def seed_data():
    print("🚀 Starting Data Seeding (Phase 6 - Timezone Fix)...")
    start_time = time.time()

    # 1. Connect & Clear
    should_close = False
    if not database_instance.client:
        await database_instance.connect_db()
        should_close = True
    
    db = database_instance.db
    redis = database_instance.redis_client

    print("🔥 Clearing old data...")
    await db.dishes.delete_many({})
    await db.users.delete_many({})
    await db.logs_behavior.delete_many({})
    if redis:
        await redis.flushall()

    # 2. Define Dishes (50+ items, Balanced)
    print("🍱 Seeding Dishes (50+ Items, Balanced)...")
    
    # Breakfast Items (10)
    breakfast_dishes = [
        {"name": "鲜肉大包", "category": "面食", "price": 2.5, "calories": 250, "tags": ["早餐", "热销", "面食"]},
        {"name": "香菇菜包", "category": "面食", "price": 2.0, "calories": 200, "tags": ["早餐", "素食", "健康"]},
        {"name": "豆浆", "category": "饮品", "price": 1.5, "calories": 100, "tags": ["早餐", "健康", "饮品"]},
        {"name": "油条", "category": "面食", "price": 2.0, "calories": 300, "tags": ["早餐", "传统", "油炸"]},
        {"name": "皮蛋瘦肉粥", "category": "面食", "price": 4.0, "calories": 200, "tags": ["早餐", "暖胃", "清淡"]},
        {"name": "小米粥", "category": "面食", "price": 2.0, "calories": 150, "tags": ["早餐", "健康", "清淡"]},
        {"name": "茶叶蛋", "category": "小吃", "price": 1.5, "calories": 80, "tags": ["早餐", "蛋白质"]},
        {"name": "葱油饼", "category": "面食", "price": 3.0, "calories": 350, "tags": ["早餐", "香脆"]},
        {"name": "生煎包", "category": "面食", "price": 6.0, "calories": 400, "tags": ["早餐", "特色"]},
        {"name": "豆腐脑(咸)", "category": "小吃", "price": 3.0, "calories": 150, "tags": ["早餐", "传统"]},
    ]

    # Main Meals (40+)
    main_dishes = [
        # Spicy (川菜/湘菜) - Reduced ratio
        {"name": "麻婆豆腐", "category": "川菜", "price": 8.0, "calories": 400, "tags": ["辣", "下饭", "豆腐"]},
        {"name": "辣子鸡丁", "category": "川菜", "price": 15.0, "calories": 500, "tags": ["辣", "肉食", "鸡肉"]},
        {"name": "水煮鱼", "category": "川菜", "price": 28.0, "calories": 600, "tags": ["辣", "海鲜", "大菜"]},
        {"name": "宫保鸡丁", "category": "川菜", "price": 16.0, "calories": 550, "tags": ["微辣", "经典", "鸡肉"]},
        {"name": "酸辣土豆丝", "category": "川菜", "price": 8.0, "calories": 250, "tags": ["辣", "素食", "开胃"]},
        {"name": "小炒肉", "category": "湘菜", "price": 20.0, "calories": 550, "tags": ["辣", "猪肉", "下饭"]},
        {"name": "剁椒鱼头", "category": "湘菜", "price": 35.0, "calories": 450, "tags": ["辣", "海鲜", "硬菜"]},
        {"name": "回锅肉", "category": "川菜", "price": 22.0, "calories": 700, "tags": ["微辣", "猪肉", "经典"]},

        # Sweet/Savory (本帮菜/粤菜/江浙菜)
        {"name": "红烧肉", "category": "本帮菜", "price": 22.0, "calories": 700, "tags": ["甜", "肉食", "经典"]},
        {"name": "糖醋排骨", "category": "本帮菜", "price": 25.0, "calories": 650, "tags": ["甜", "酸甜", "排骨"]},
        {"name": "西红柿炒蛋", "category": "本帮菜", "price": 10.0, "calories": 300, "tags": ["家常", "酸甜", "鸡蛋"]},
        {"name": "狮子头", "category": "本帮菜", "price": 18.0, "calories": 500, "tags": ["咸鲜", "肉食"]},
        {"name": "干炒牛河", "category": "粤菜", "price": 18.0, "calories": 600, "tags": ["主食", "牛肉", "镬气"]},
        {"name": "白切鸡", "category": "粤菜", "price": 25.0, "calories": 400, "tags": ["清淡", "鸡肉", "经典"]},
        {"name": "菠萝咕咾肉", "category": "粤菜", "price": 22.0, "calories": 550, "tags": ["酸甜", "猪肉"]},
        {"name": "蚝油生菜", "category": "粤菜", "price": 12.0, "calories": 100, "tags": ["清淡", "素食", "健康"]},
        {"name": "西湖醋鱼", "category": "江浙菜", "price": 30.0, "calories": 400, "tags": ["酸甜", "鱼"]},
        {"name": "龙井虾仁", "category": "江浙菜", "price": 38.0, "calories": 300, "tags": ["清淡", "海鲜", "精致"]},

        # Healthy/Veg (素菜/轻食)
        {"name": "清炒时蔬", "category": "素菜", "price": 8.0, "calories": 150, "tags": ["健康", "素食", "清淡"]},
        {"name": "地三鲜", "category": "素菜", "price": 12.0, "calories": 400, "tags": ["家常", "素食"]},
        {"name": "荷塘月色", "category": "素菜", "price": 15.0, "calories": 120, "tags": ["健康", "素食", "精致"]},
        {"name": "水果沙拉", "category": "轻食", "price": 15.0, "calories": 200, "tags": ["健康", "生鲜", "低卡"]},
        {"name": "鸡胸肉沙拉", "category": "轻食", "price": 18.0, "calories": 300, "tags": ["健康", "低脂", "增肌"]},
        {"name": "玉米排骨汤", "category": "汤品", "price": 12.0, "calories": 250, "tags": ["健康", "汤", "滋补"]},

        # Staples (面食/主食)
        {"name": "扬州炒饭", "category": "面食", "price": 15.0, "calories": 500, "tags": ["主食", "米饭"]},
        {"name": "牛肉面", "category": "面食", "price": 18.0, "calories": 550, "tags": ["主食", "汤面", "热乎"]},
        {"name": "炸酱面", "category": "面食", "price": 16.0, "calories": 500, "tags": ["主食", "干拌"]},
        {"name": "咖喱鸡肉饭", "category": "异国料理", "price": 20.0, "calories": 600, "tags": ["主食", "咖喱"]},
        {"name": "意大利肉酱面", "category": "西餐", "price": 22.0, "calories": 550, "tags": ["主食", "西式"]},
        
        # Drinks & Snacks
        {"name": "珍珠奶茶", "category": "饮品", "price": 12.0, "calories": 400, "tags": ["甜", "饮品", "快乐水"]},
        {"name": "柠檬茶", "category": "饮品", "price": 10.0, "calories": 150, "tags": ["酸甜", "饮品", "解腻"]},
        {"name": "鲜榨橙汁", "category": "饮品", "price": 15.0, "calories": 120, "tags": ["健康", "饮品", "果汁"]},
        {"name": "薯条", "category": "小吃", "price": 8.0, "calories": 350, "tags": ["油炸", "零食"]},
        {"name": "奥尔良烤翅", "category": "小吃", "price": 12.0, "calories": 300, "tags": ["肉食", "小吃"]},
    ]

    all_dishes_data = breakfast_dishes + main_dishes
    
    # Insert Dishes
    breakfast_ids = []
    main_ids = []
    
    for d in breakfast_dishes:
        dish = Dish(**d)
        res = await db.dishes.insert_one(dish.model_dump(by_alias=True, exclude={"id"}))
        breakfast_ids.append(res.inserted_id)
        if redis:
            dish.id = str(res.inserted_id)
            await redis.set(f"dish:{res.inserted_id}", dish.model_dump_json())

    for d in main_dishes:
        dish = Dish(**d)
        res = await db.dishes.insert_one(dish.model_dump(by_alias=True, exclude={"id"}))
        main_ids.append(res.inserted_id)
        if redis:
            dish.id = str(res.inserted_id)
            await redis.set(f"dish:{res.inserted_id}", dish.model_dump_json())

    print(f"✅ Inserted {len(breakfast_ids)} breakfast items and {len(main_ids)} main items.")

    # 3. Create Users
    print("👥 Seeding Users...")
    users = [
        {"username": "demo_spicy", "email": "spicy@demo.com", "preferences": {"辣": 5.0, "川菜": 4.0}},
        {"username": "demo_sweet", "email": "sweet@demo.com", "preferences": {"甜": 5.0, "本帮菜": 4.0}},
        {"username": "demo_veg", "email": "veg@demo.com", "preferences": {"素食": 5.0, "健康": 4.0}},
        {"username": "demo_meat", "email": "meat@demo.com", "preferences": {"肉食": 5.0, "高热量": 3.0}},
        {"username": "demo_light", "email": "light@demo.com", "preferences": {"清淡": 5.0, "粤菜": 4.0}},
        {"username": "demo_interactive", "email": "interactive@demo.com", "preferences": {"个性化": 5.0, "探索": 4.0}},
    ]
    
    for _ in range(45):  # 45 regular users + 6 demo users = 51 total
        users.append({
            "username": f"user_{_+1}",
            "email": f"user{_+1}@example.com",
            "preferences": {}
        })
    
    await db.users.insert_many(users)
    user_ids = [u["_id"] for u in await db.users.find().to_list(length=100)]

    # 4. Generate Logs (Realistic Patterns with Timezone Fix)
    print("📊 Seeding Logs (Realistic Patterns with Timezone Fix)...")
    logs = []
    
    # Use current time in Shanghai timezone as reference
    now_shanghai = datetime.now(TZ_SHANGHAI)
    
    total_logs = 100000
    
    # Get demo user IDs to EXCLUDE from random generation
    demo_users_db = await db.users.find({"username": {"$regex": "^demo_"}}).to_list(length=10)
    demo_user_ids = [u["_id"] for u in demo_users_db]
    
    # Filter regular users (non-demo)
    regular_user_ids = [uid for uid in user_ids if uid not in demo_user_ids]
    
    # 4.1 Generate Random Logs (for regular users only)
    for i in range(total_logs):
        # 1. Determine Time (Strict Meal Times in Shanghai Time)
        # Breakfast: 7-9 (15%), Lunch: 11-13 (45%), Dinner: 17-19 (30%), Snack: 14-16 (10%)
        rand_time = random.random()
        if rand_time < 0.15:
            hour = random.randint(7, 9)
            is_breakfast = True
        elif rand_time < 0.60:
            hour = random.randint(11, 13)
            is_breakfast = False
        elif rand_time < 0.90:
            hour = random.randint(17, 19)
            is_breakfast = False
        else:
            hour = random.randint(14, 16)
            is_breakfast = False
            
        day_offset = random.randint(1, 30) # 1 to 30 days ago
        
        # Construct time in Shanghai timezone
        base_date = now_shanghai - timedelta(days=day_offset)
        log_time_shanghai = base_date.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0)
        
        # Convert to UTC for storage
        log_time_utc = log_time_shanghai.astimezone(pytz.UTC)
        
        # 2. Determine Dish (Strict Context Aware)
        if is_breakfast:
            # Breakfast time: 95% breakfast items, 5% others (maybe drinks)
            if random.random() < 0.95:
                did = random.choice(breakfast_ids)
            else:
                did = random.choice(main_ids)
        else:
            # Non-breakfast time: 98% main items, 2% breakfast (maybe drinks)
            if random.random() < 0.98:
                did = random.choice(main_ids)
            else:
                did = random.choice(breakfast_ids)
                
        # 3. Determine User (ONLY regular users, not demo users)
        uid = random.choice(regular_user_ids)
        
        log = {
            "user_id": uid,
            "dish_id": did,
            "action": "order",
            "timestamp": log_time_utc # Store as UTC
        }
        logs.append(log)
        
        if len(logs) >= 5000:
            await db.logs_behavior.insert_many(logs)
            logs = []
            print(f"   Inserted {i+1} logs...")

    if logs:
        await db.logs_behavior.insert_many(logs)
        logs = []

    # 4.2 Generate Specific History for Demo Users (Distinctive Profiles)
    print("👤 Seeding Demo User History (Distinctive Profiles)...")
    demo_logs = []
    
    # Fetch all dishes to a map
    all_dishes_db = await db.dishes.find().to_list(length=100)
    dish_map = {d["name"]: d["_id"] for d in all_dishes_db}
    
    # Get demo users (excluding demo_interactive - it should start clean)
    demo_users_db = await db.users.find({
        "username": {"$regex": "^demo_"},
        "username": {"$ne": "demo_interactive"}  # Exclude interactive user
    }).to_list(length=10)
    
    # Define VERY specific dish preferences for each user
    user_profiles = {
        "demo_spicy": {
            "dishes": ["麻婆豆腐", "辣子鸡丁", "水煮鱼", "宫保鸡丁", "酸辣土豆丝", "小炒肉", "剁椒鱼头", "回锅肉"],
            "count": 60  # Heavy ordering
        },
        "demo_sweet": {
            "dishes": ["红烧肉", "糖醋排骨", "西红柿炒蛋", "狮子头", "菠萝咕咾肉", "西湖醋鱼"],
            "count": 50
        },
        "demo_veg": {
            "dishes": ["清炒时蔬", "地三鲜", "荷塘月色", "水果沙拉", "鸡胸肉沙拉", "蚝油生菜", "玉米排骨汤"],
            "count": 55
        },
        "demo_meat": {
            "dishes": ["红烧肉", "辣子鸡丁", "回锅肉", "狮子头", "白切鸡", "糖醋排骨", "奥尔良烤翅", "菠萝咕咾肉"],
            "count": 65
        },
        "demo_light": {
            "dishes": ["白切鸡", "蚝油生菜", "龙井虾仁", "清炒时蔬", "西湖醋鱼", "鸡胸肉沙拉", "鲜榨橙汁", "水果沙拉"],
            "count": 50
        }
        # demo_interactive intentionally excluded - starts with no history
    }
    
    for u in demo_users_db:
        username = u["username"]
        if username not in user_profiles:
            continue
            
        profile = user_profiles[username]
        target_dish_names = profile["dishes"]
        order_count = profile["count"]
        
        # Map dish names to IDs
        user_target_ids = []
        for dish_name in target_dish_names:
            if dish_name in dish_map:
                user_target_ids.append(dish_map[dish_name])
        
        if not user_target_ids:
            continue
            
        # Generate orders over the past 30 days
        for _ in range(order_count):
            did = random.choice(user_target_ids)
            # Spread orders over past 30 days with realistic times
            days_ago = random.randint(1, 30)
            hour = random.choice([11, 12, 13, 17, 18, 19])  # Lunch/Dinner times
            
            base_date = now_shanghai - timedelta(days=days_ago)
            log_time_shanghai = base_date.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0)
            log_time_utc = log_time_shanghai.astimezone(pytz.UTC)
            
            demo_logs.append({
                "user_id": u["_id"],
                "dish_id": did,
                "action": "order",
                "timestamp": log_time_utc
            })
            
    if demo_logs:
        await db.logs_behavior.insert_many(demo_logs)
        print(f"   Inserted {len(demo_logs)} demo user logs.")

    # 5. Rebuild Redis Leaderboard
    print("🏆 Rebuilding Redis Leaderboard...")
    if redis:
        pipeline = [
            {"$match": {"action": "order"}},
            {"$group": {"_id": "$dish_id", "count": {"$sum": 1}}}
        ]
        agg_res = await db.logs_behavior.aggregate(pipeline).to_list(length=None)
        for item in agg_res:
            await redis.zadd("rank:daily:sales", {str(item["_id"]): item["count"]})

    duration = time.time() - start_time
    print(f"✅ Seeding Completed in {duration:.2f} seconds!")
    
    if should_close:
        await database_instance.close_db()

if __name__ == "__main__":
    asyncio.run(seed_data())
