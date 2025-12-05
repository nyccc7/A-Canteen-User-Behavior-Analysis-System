from fastapi import APIRouter, Depends
from database import db, get_database
from datetime import datetime, timedelta
import pytz
from bson import ObjectId

router = APIRouter()

@router.get("/analytics/sales_trend")
async def get_sales_trend():
    # Last 7 days
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=6)
    
    database = await get_database()
    
    pipeline = [
        {
            "$match": {
                "action": "order",
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d %H:00", 
                        "date": "$timestamp",
                        "timezone": "Asia/Shanghai"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    results = await database.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    dates = [r["_id"] for r in results]
    counts = [r["count"] for r in results]
    
    return {"dates": dates, "counts": counts}

@router.get("/analytics/revenue")
async def get_revenue_trend():
    # Last 30 days
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=29)
    
    database = await get_database()
    
    # OPTIMIZATION: Pre-load all dishes into memory to avoid $lookup
    all_dishes = await database.dishes.find({}, {"_id": 1, "price": 1}).to_list(length=1000)
    dish_prices = {str(d["_id"]): d["price"] for d in all_dishes}
    
    # Simplified pipeline without expensive $lookup
    pipeline = [
        {
            "$match": {
                "action": "order",
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d", 
                            "date": "$timestamp",
                            "timezone": "Asia/Shanghai"
                        }
                    },
                    "dish_id": "$dish_id"
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.date": 1}}
    ]
    
    results = await database.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    # Calculate revenue in Python using pre-loaded prices
    revenue_by_date = {}
    for r in results:
        date = r["_id"]["date"]
        dish_id_str = str(r["_id"]["dish_id"])
        count = r["count"]
        price = dish_prices.get(dish_id_str, 0)
        revenue_by_date[date] = revenue_by_date.get(date, 0) + (price * count)
    
    # Sort by date
    sorted_dates = sorted(revenue_by_date.keys())
    dates = sorted_dates
    values = [revenue_by_date[d] for d in sorted_dates]
    
    return {"dates": dates, "values": values}

@router.get("/analytics/heatmap")
async def get_heatmap():
    # Last 30 days
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=30)
    
    database = await get_database()
    
    pipeline = [
        {
            "$match": {
                "action": "order",
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$project": {
                "dayOfWeek": {
                    "$dayOfWeek": {
                        "date": "$timestamp",
                        "timezone": "Asia/Shanghai"
                    }
                },
                "hour": {
                    "$hour": {
                        "date": "$timestamp",
                        "timezone": "Asia/Shanghai"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": {"day": "$dayOfWeek", "hour": "$hour"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = await database.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    # ECharts heatmap format: [x, y, value]
    # x: hour (0-23), y: day (0-6, Mon-Sun)
    # MongoDB $dayOfWeek: 1 (Sun) - 7 (Sat)
    # Map Mongo day to ECharts day: Sun(1)->6, Mon(2)->0, ..., Sat(7)->5
    
    data = []
    for r in results:
        mongo_day = r["_id"]["day"]
        hour = r["_id"]["hour"]
        count = r["count"]
        
        # Convert 1-7 (Sun-Sat) to 0-6 (Mon-Sun)
        # 1->6, 2->0, 3->1, 4->2, 5->3, 6->4, 7->5
        echarts_day = (mongo_day - 2) % 7
        
        data.append([hour, echarts_day, count])
        
    return data

@router.get("/analytics/category_share")
async def get_category_share():
    database = await get_database()
    
    # OPTIMIZATION: Pre-load all dish categories into memory to avoid $lookup
    all_dishes = await database.dishes.find({}, {"_id": 1, "category": 1}).to_list(length=1000)
    dish_categories = {str(d["_id"]): d["category"] for d in all_dishes}
    
    # Simplified pipeline without expensive $lookup
    pipeline = [
        {"$match": {"action": "order"}},
        {
            "$group": {
                "_id": "$dish_id",
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = await database.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    # Calculate category counts in Python using pre-loaded categories
    category_counts = {}
    for r in results:
        dish_id_str = str(r["_id"])
        category = dish_categories.get(dish_id_str, "未知")
        category_counts[category] = category_counts.get(category, 0) + r["count"]
    
    # Sort by count descending
    data = [{"name": cat, "value": count} for cat, count in category_counts.items()]
    data.sort(key=lambda x: x["value"], reverse=True)
    
    return data

@router.get("/analytics/user_radar")
async def get_user_radar():
    # Calculate average preference scores across all users
    # This is a simplification. Ideally we'd aggregate user.preferences
    
    database = await get_database()
    users = await database.users.find({}, {"preferences": 1}).to_list(length=1000)
    
    # Define standard dimensions
    dimensions = ["辣", "甜", "咸", "酸", "鲜", "油"]
    totals = {d: 0.0 for d in dimensions}
    counts = {d: 0 for d in dimensions}
    
    for u in users:
        prefs = u.get("preferences", {})
        for k, v in prefs.items():
            # Map some common tags to dimensions if needed, or just use exact matches
            # For now assuming preferences keys match dimensions or are close
            if k in totals:
                totals[k] += v
                counts[k] += 1
            elif "辣" in k: 
                totals["辣"] += v
                counts["辣"] += 1
            # ... add more mapping logic if needed
            
    # Default values if no data
    values = []
    for d in dimensions:
        if counts[d] > 0:
            values.append(round(totals[d] / counts[d], 1))
        else:
            values.append(3.0) # Default middle score
            
    indicators = [{"name": d, "max": 5} for d in dimensions]
    
    return {"indicators": indicators, "values": values}

@router.get("/analytics/calories_trend")
async def get_calories_trend():
    # Last 7 days
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=6)
    
    database = await get_database()
    
    pipeline = [
        {
            "$match": {
                "action": "order",
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$lookup": {
                "from": "dishes",
                "localField": "dish_id",
                "foreignField": "_id",
                "as": "dish"
            }
        },
        {"$unwind": "$dish"},
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d", 
                        "date": "$timestamp",
                        "timezone": "Asia/Shanghai"
                    }
                },
                "total_calories": {"$sum": "$dish.calories"},
                "order_count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "avg_calories": {"$divide": ["$total_calories", "$order_count"]}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    results = await database.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    dates = [r["_id"] for r in results]
    values = [round(r["avg_calories"], 0) for r in results]
    
    return {"dates": dates, "values": values}

@router.get("/analytics/traffic_prediction")
async def get_traffic_prediction():
    """
    Predict daily traffic flow based on historical data (last 30 days).
    Returns predicted traffic for each hour (0-23).
    """
    # Last 30 days
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=30)
    
    database = await get_database()
    
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
    
    results = await database.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    # Fill missing hours with 0
    hours_data = {r["_id"]: r["avg_count"] for r in results}
    
    hours = list(range(24))
    predicted_traffic = [int(hours_data.get(h, 0)) for h in hours]
    
    # Get current hour traffic for comparison
    current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
    
    return {
        "hours": [f"{h}点" for h in hours],
        "predicted_traffic": predicted_traffic,
        "current_hour": current_hour
    }

@router.get("/analytics/procurement_guidance")
async def get_procurement_guidance():
    """
    Generate procurement guidance based on sales forecast.
    Uses Linear Regression on last 14 days data to predict next day needs.
    """
    from ingredient_map import DISH_INGREDIENTS_MAP
    import numpy as np
    try:
        from sklearn.linear_model import LinearRegression
    except ImportError:
        print("Scikit-learn not found, falling back to simple average.")
        LinearRegression = None
    
    # Last 14 days for prediction base (more data for regression)
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=13)
    
    database = await get_database()
    
    # Get daily sales per dish
    pipeline = [
        {
            "$match": {
                "action": "order",
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "dish_id": "$dish_id",
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d", 
                            "date": "$timestamp",
                            "timezone": "Asia/Shanghai"
                        }
                    }
                },
                "daily_count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.date": 1}}
    ]
    
    sales_data = await database.logs_behavior.aggregate(pipeline).to_list(length=None)
    
    # Organize data by dish: {dish_id: {date_str: count}}
    dish_sales_history = {}
    all_dates = sorted(list(set([d["_id"]["date"] for d in sales_data])))
    
    # Create a date index map for regression (0, 1, 2...)
    date_to_idx = {date: i for i, date in enumerate(all_dates)}
    
    for record in sales_data:
        dish_id = str(record["_id"]["dish_id"])
        date = record["_id"]["date"]
        count = record["daily_count"]
        
        if dish_id not in dish_sales_history:
            dish_sales_history[dish_id] = {}
        dish_sales_history[dish_id][date] = count
        
    # Get dish names
    dish_ids = [ObjectId(did) for did in dish_sales_history.keys()]
    dishes = await database.dishes.find({"_id": {"$in": dish_ids}}, {"name": 1}).to_list(length=None)
    dish_map = {str(d["_id"]): d["name"] for d in dishes}
    
    # Calculate ingredient needs based on prediction
    ingredient_totals = {}
    
    # Next day index (if we have N days 0..N-1, next is N)
    next_day_idx = len(all_dates)
    
    for dish_id, history in dish_sales_history.items():
        dish_name = dish_map.get(dish_id, "")
        
        # Prepare X (days) and y (sales)
        # Fill missing days with 0
        X = []
        y = []
        for date in all_dates:
            X.append([date_to_idx[date]])
            y.append(history.get(date, 0))
            
        predicted_sales = 0
        
        if LinearRegression and len(y) > 1:
            try:
                model = LinearRegression()
                model.fit(X, y)
                # Predict next day
                prediction = model.predict([[next_day_idx]])
                predicted_sales = max(0, prediction[0]) # No negative sales
            except Exception as e:
                print(f"Prediction error for {dish_name}: {e}")
                predicted_sales = sum(y) / len(y) # Fallback to average
        else:
            # Fallback if not enough data or no sklearn
            predicted_sales = sum(y) / len(y) if y else 0
            
        # Get ingredients for this dish
        ingredients = DISH_INGREDIENTS_MAP.get(dish_name, DISH_INGREDIENTS_MAP["default"])
        
        for ing_name, amount_per_dish in ingredients.items():
            total_needed = predicted_sales * amount_per_dish
            ingredient_totals[ing_name] = ingredient_totals.get(ing_name, 0) + total_needed
            
    # Sort by quantity descending
    sorted_ingredients = sorted(ingredient_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Take top 10 for display
    top_ingredients = sorted_ingredients[:10]
    
    return {
        "ingredients": [i[0] for i in top_ingredients],
        "quantities": [round(i[1], 1) for i in top_ingredients],
        "units": ["kg"] * len(top_ingredients)
    }
