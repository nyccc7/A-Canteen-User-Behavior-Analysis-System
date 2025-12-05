from fastapi import APIRouter, HTTPException
from database import get_database
from models import Dish, LogBehavior
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

@router.get("/history/{user_id}")
async def get_order_history(user_id: str):
    """
    获取用户的历史订单记录。
    """
    db = await get_database()
    
    # 查找该用户的 order 记录，按时间倒序
    from bson import ObjectId
    try:
        oid = ObjectId(user_id)
    except:
        return []
        
    cursor = db.logs_behavior.find(
        {"user_id": oid, "action": "order"}
    ).sort("timestamp", -1).limit(50)
    
    logs = await cursor.to_list(length=50)
    
    history = []
    for log in logs:
        dish = await db.dishes.find_one({"_id": log["dish_id"]})
        if dish:
            history.append({
                "dish_name": dish["name"],
                "price": dish["price"],
                "timestamp": log["timestamp"],
                "category": dish["category"]
            })
            
    return history

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    user_id: str = None  # Optional user ID for personalization

@router.post("/chat")
async def chat_with_nutritionist(request: ChatRequest):
    """
    AI Nutritionist Chat Endpoint with Database Integration.
    Queries database for available dishes and user context to provide personalized recommendations.
    """
    user_msg = request.message
    
    # Real AI Logic using OpenAI
    try:
        import openai
        from bson import ObjectId
        
        # TODO: User must fill in their API Key here
        OPENAI_API_KEY = "sk-fedfpdbnswnrspxgwigpqjdiggfmfeuidyqbkgpbcyxvdwmf" 
        
        if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
             return {"reply": "请在后端代码 backend/routers/student.py 中配置您的 OpenAI API Key。"}

        # Query database for context
        db = await get_database()
        
        # Get all available dishes
        dishes = await db.dishes.find({}).to_list(length=100)
        dishes_info = []
        for dish in dishes:
            dishes_info.append(f"{dish['name']}（{dish['category']}，{dish['calories']}kcal，¥{dish['price']}，标签:{','.join(dish.get('tags', []))}）")
        
        dishes_context = "今日可选菜品：\n" + "\n".join(dishes_info[:30])  # Limit to 30 to avoid token limit
        
        # Get user preferences if user_id provided
        user_context = ""
        if request.user_id:
            try:
                user_oid = ObjectId(request.user_id)
                # Get user's recent orders
                recent_orders = await db.logs_behavior.find(
                    {"user_id": user_oid, "action": "order"}
                ).sort("timestamp", -1).limit(10).to_list(length=10)
                
                if recent_orders:
                    ordered_dishes = []
                    for order in recent_orders:
                        dish = await db.dishes.find_one({"_id": order["dish_id"]})
                        if dish:
                            ordered_dishes.append(dish["name"])
                    
                    user_context = f"\n\n用户最近点过的菜品：{', '.join(ordered_dishes[:5])}"
            except:
                pass
        
        # Disable proxy for this request to avoid SOCKS proxy errors
        import httpx
        import os
        
        # Temporarily disable proxy environment variables for OpenAI client
        old_http_proxy = os.environ.get('HTTP_PROXY')
        old_https_proxy = os.environ.get('HTTPS_PROXY')
        old_all_proxy = os.environ.get('ALL_PROXY')
        
        # Clear proxy settings
        for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']:
            os.environ.pop(key, None)
        
        try:
            client = openai.AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url="https://api.siliconflow.cn/v1"
            )
        
            # Construct messages with database context
            system_prompt = f"""你是一位专业的学校食堂AI营养师。你的任务是根据学生的口味偏好、健康需求推荐菜品，并解答营养相关问题。请用亲切、鼓励的语气回答。

{dishes_context}
{user_context}

请根据以上真实的菜品信息来回答用户问题和提供推荐。推荐时请考虑营养均衡、热量搭配和用户的历史偏好，回答简洁，尽量两句话回答。"""

            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add history (simplified mapping)
            for h in request.history:
                role = "user" if h.get("role") == "user" else "assistant"
                messages.append({"role": role, "content": h.get("content", "")})
                
            messages.append({"role": "user", "content": user_msg})
            
            completion = await client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3.2-Exp",
                messages=messages,
                max_tokens=200
            )
            
            response = completion.choices[0].message.content
        finally:
            # Restore proxy settings
            if old_http_proxy:
                os.environ['HTTP_PROXY'] = old_http_proxy
            if old_https_proxy:
                os.environ['HTTPS_PROXY'] = old_https_proxy
            if old_all_proxy:
                os.environ['ALL_PROXY'] = old_all_proxy
        
    except ImportError:
        response = "错误：未安装 openai 库。请运行 `pip install openai`。"
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        response = "抱歉，AI服务暂时不可用，请稍后再试。"
    
    return {"reply": response}

@router.get("/users")
async def get_demo_users():
    """
    获取演示用户列表，并根据历史订单动态计算用户标签。
    """
    db = await get_database()
    users = await db.users.find({"username": {"$regex": "^demo_"}}).to_list(length=10)
    
    result = []
    for u in users:
        # Calculate tags based on history
        pipeline = [
            {"$match": {"user_id": u["_id"], "action": "order"}},
            {"$lookup": {
                "from": "dishes",
                "localField": "dish_id",
                "foreignField": "_id",
                "as": "dish_info"
            }},
            {"$unwind": "$dish_info"},
            {"$unwind": "$dish_info.tags"},
            {"$group": {"_id": "$dish_info.tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 3}
        ]
        tags_agg = await db.logs_behavior.aggregate(pipeline).to_list(length=3)
        top_tags = [t["_id"] for t in tags_agg]
        
        # Fallback if no history
        if not top_tags:
            top_tags = ["新用户"]
            
        result.append({
            "username": u["username"], 
            "id": str(u["_id"]), 
            "preferences": u["preferences"],
            "dynamic_tags": top_tags
        })
        
    return result

@router.delete("/history/{user_id}")
async def clear_order_history(user_id: str):
    """
    清空用户历史订单（仅限演示用户）。
    用于 demo_interactive 用户重置体验。
    """
    db = await get_database()
    from bson import ObjectId
    
    try:
        oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # 安全检查：只允许演示用户清空历史
    user = await db.users.find_one({"_id": oid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user["username"].startswith("demo_"):
        raise HTTPException(status_code=403, detail="只有演示用户可以清空历史")
    
    # 删除该用户的所有订单日志
    result = await db.logs_behavior.delete_many({"user_id": oid})
    
    return {
        "deleted_count": result.deleted_count,
        "message": f"已清空 {result.deleted_count} 条历史记录"
    }
