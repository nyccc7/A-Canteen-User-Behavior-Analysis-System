from fastapi import APIRouter, HTTPException
from database import get_database, get_redis
from models import Dish, LogBehavior
from pydantic import BaseModel
from datetime import datetime
from typing import List
import json

router = APIRouter()

@router.get("/leaderboard", response_model=List[Dish])
async def get_leaderboard():
    """
    获取热销榜单。
    策略：优先从 Redis 读取 (ZSET rank:daily:sales)，
    如果 Redis 不可用或为空，则降级查 MongoDB。
    体现了“分布式缓存”和“高可用”设计。
    """
    redis = await get_redis()
    db = await get_database()
    
    dishes = []
    
    # 1. 尝试从 Redis 获取排行榜 (前 10 名)
    try:
        if redis:
            # ZREVRANGE 返回有序集合中指定区间内的成员，通过索引，分数从高到低
            top_dish_ids = await redis.zrevrange("rank:daily:sales", 0, 9)
            
            if top_dish_ids:
                print("Cache Hit: Loading leaderboard from Redis")
                from bson import ObjectId
                for dish_id in top_dish_ids:
                    # 尝试获取菜品详情缓存
                    # seed.py uses "dish:{id}"
                    cached_detail = await redis.get(f"dish:{dish_id}")
                    if cached_detail:
                        dishes.append(Dish(**json.loads(cached_detail)))
                    else:
                        # 缓存缺失，查 Mongo 并回填
                        # Convert string ID from Redis to ObjectId for MongoDB lookup
                        try:
                            oid = ObjectId(dish_id)
                            dish_data = await db.dishes.find_one({"_id": oid})
                            if dish_data:
                                dish = Dish(**dish_data)
                                dishes.append(dish)
                                # 异步回填缓存 (过期时间 1 小时)
                                await redis.setex(f"dish:{dish_id}", 3600, dish.model_dump_json())
                        except Exception as e:
                            print(f"Error fetching dish {dish_id}: {e}")
                return dishes
    except Exception as e:
        print(f"Redis Error: {e}. Falling back to MongoDB.")

    # 2. 降级逻辑：Redis 挂了或为空，直接查 MongoDB 聚合统计
    print("Cache Miss: Loading leaderboard from MongoDB")
    pipeline = [
        {"$group": {"_id": "$dish_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    # 注意：这里假设 logs_behavior 表中有数据
    cursor = db.logs_behavior.aggregate(pipeline)
    top_dishes = await cursor.to_list(length=10)
    
    for item in top_dishes:
        dish_data = await db.dishes.find_one({"_id": item["_id"]})
        if dish_data:
            dishes.append(Dish(**dish_data))
            
    return dishes

@router.get("/dishes", response_model=List[Dish])
async def get_all_dishes():
    """
    获取所有菜品列表。
    """
    db = await get_database()
    dishes = await db.dishes.find().to_list(length=100)
    return [Dish(**d) for d in dishes]

class OrderRequest(BaseModel):
    user_id: str
    dish_id: str

@router.post("/order")
async def order_dish(order: OrderRequest):
    """
    用户点餐接口。
    1. 写入 MongoDB 日志 (logs_behavior)
    2. 更新 Redis 实时销量榜 (ZINCRBY)
    """
    db = await get_database()
    redis = await get_redis()
    
    # 1. 写入日志
    from bson import ObjectId
    log_dict = {
        "user_id": ObjectId(order.user_id),
        "dish_id": ObjectId(order.dish_id),
        "action": "order",
        "timestamp": datetime.now()
    }
    await db.logs_behavior.insert_one(log_dict)
    
    # 2. 更新 Redis 排行榜
    if redis:
        try:
            await redis.zincrby("rank:daily:sales", 1, order.dish_id)
        except Exception as e:
            print(f"Redis Error during order update: {e}")
            # Continue execution, do not fail the order
        
    return {"message": "Order placed successfully"}

@router.get("/traffic_prediction")
async def get_traffic_prediction():
    """
    获取食堂实时拥挤度预测及全天趋势。
    基于历史数据（过去 30 天）计算每小时的平均订单量。
    """
    db = await get_database()
    
    # Last 30 days
    import pytz
    from datetime import timedelta
    
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=30)
    
    pipeline = [
        {
            "$match": {
                "action": "order",
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$project": {
                "hour": {
                    "$hour": {
                        "date": "$timestamp",
                        "timezone": "Asia/Shanghai"
                    }
                },
                "day": {
                    "$dayOfYear": {
                        "date": "$timestamp",
                        "timezone": "Asia/Shanghai"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": {"day": "$day", "hour": "$hour"},
                "count": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": "$_id.hour",
                "avg_count": {"$avg": "$count"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    results = await db.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    # Fill missing hours with 0
    hours_data = {r["_id"]: r["avg_count"] for r in results}
    hours = list(range(24))
    predicted_traffic = [int(hours_data.get(h, 0)) for h in hours]
    
    # Current status
    now_shanghai = datetime.now(pytz.timezone('Asia/Shanghai'))
    current_hour = now_shanghai.hour
    current_val = hours_data.get(current_hour, 0)
    
    # Normalize to 0-100% (Dynamic capacity based on daily max, min 200)
    daily_max = max(hours_data.values()) if hours_data else 0
    MAX_CAPACITY = max(200, int(daily_max * 1.1))
    traffic_percent = min(100, int((current_val / MAX_CAPACITY) * 100))
    
    status = "空闲"
    if traffic_percent > 80:
        status = "爆满"
    elif traffic_percent > 50:
        status = "繁忙"
        
    return {
        "traffic": traffic_percent,
        "status": status,
        "hours": [f"{h}点" for h in hours],
        "predicted_trend": predicted_traffic,
        "current_hour": current_hour
    }
