from fastapi import APIRouter, HTTPException
from database import get_database
from models import Dish
from typing import List, Dict, Set
from bson import ObjectId
import random
from collections import defaultdict, Counter
import math
from datetime import datetime, timedelta
import pytz

router = APIRouter()

# --- Helper Functions ---

def calculate_jaccard_similarity(set1: Set, set2: Set) -> float:
    """Calculate Jaccard similarity between two sets."""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def calculate_temporal_weight(timestamp: datetime) -> float:
    """
    Calculate temporal weight using exponential decay.
    Recent orders have higher weight.
    Formula: weight = exp(-days_ago / 14)
    """
    if not timestamp:
        return 0.0
        
    # Ensure timestamp is timezone-aware for comparison
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=pytz.UTC)
        
    now = datetime.now(pytz.UTC)
    diff = now - timestamp
    days_ago = max(0, diff.days)
    
    # Decay factor: 14 days half-life roughly
    return math.exp(-days_ago / 14.0)

async def get_user_preferences(user_id: ObjectId, db) -> Dict:
    """
    Analyze user history to build preference profile (tags, categories).
    Returns dict with 'tags' and 'categories' counters weighted by recency.
    """
    pipeline = [
        {"$match": {"user_id": user_id, "action": "order"}},
        {"$lookup": {
            "from": "dishes",
            "localField": "dish_id",
            "foreignField": "_id",
            "as": "dish"
        }},
        {"$unwind": "$dish"},
        {"$sort": {"timestamp": -1}},
        {"$limit": 50} # Analyze last 50 orders
    ]
    
    history = await db.logs_behavior.aggregate(pipeline).to_list(length=50)
    
    tag_prefs = Counter()
    cat_prefs = Counter()
    
    for log in history:
        weight = calculate_temporal_weight(log.get("timestamp"))
        dish = log["dish"]
        
        # Weighted category preference
        cat_prefs[dish.get("category", "unknown")] += weight
        
        # Weighted tag preference
        for tag in dish.get("tags", []):
            tag_prefs[tag] += weight
            
    return {"tags": tag_prefs, "categories": cat_prefs}

async def calculate_collaborative_score(user_id: str, db) -> Dict[str, float]:
    """
    Calculate collaborative filtering scores.
    Returns dict: {dish_id: score}
    """
    try:
        target_oid = ObjectId(user_id)
    except:
        return {}

    # Get target user's ordered dishes to exclude or weight
    target_orders = await db.logs_behavior.find(
        {"user_id": target_oid, "action": "order"}
    ).to_list(length=1000)
    
    target_dish_ids = set(str(order["dish_id"]) for order in target_orders)
    
    # 1. Find similar users (using optimized aggregation from previous step)
    pipeline = [
        {
            "$match": {
                "action": "order",
                "user_id": {"$ne": target_oid}
            }
        },
        {
            "$group": {
                "_id": {"user_id": "$user_id", "dish_id": "$dish_id"},
                "count": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": "$_id.user_id",
                "dishes": {
                    "$push": {"dish_id": "$_id.dish_id", "count": "$count"}
                }
            }
        },
        {"$limit": 100} # Top 100 users
    ]
    
    user_summaries = await db.logs_behavior.aggregate(pipeline).to_list(length=100)
    
    # Calculate similarity
    similarities = []
    target_vector = Counter([str(order["dish_id"]) for order in target_orders])
    target_mag = math.sqrt(sum(1 for _ in target_orders)) # Simplified magnitude
    
    for summary in user_summaries:
        other_dishes = {str(d["dish_id"]): d["count"] for d in summary["dishes"]}
        
        # Jaccard-like similarity on dish sets for speed
        intersection = len(target_dish_ids.intersection(other_dishes.keys()))
        if intersection == 0:
            continue
            
        union = len(target_dish_ids.union(other_dishes.keys()))
        similarity = intersection / union
        
        similarities.append((similarity, other_dishes))
        
    # Top 20 similar users
    similarities.sort(key=lambda x: x[0], reverse=True)
    top_similar = similarities[:20]
    
    # Aggregate scores
    scores = defaultdict(float)
    for sim, dishes in top_similar:
        for dish_id, count in dishes.items():
            if dish_id not in target_dish_ids:
                scores[dish_id] += sim * count
                
    # Normalize scores to 0-1 range
    if not scores:
        return {}
        
    max_score = max(scores.values())
    return {k: v / max_score for k, v in scores.items()}

async def calculate_content_score(user_prefs: Dict, all_dishes: List[Dict]) -> Dict[str, float]:
    """
    Calculate content-based scores based on tag/category matching.
    """
    scores = {}
    tag_prefs = user_prefs["tags"]
    cat_prefs = user_prefs["categories"]
    
    # Normalize preferences
    total_tag_weight = sum(tag_prefs.values()) or 1
    total_cat_weight = sum(cat_prefs.values()) or 1
    
    for dish in all_dishes:
        dish_id = str(dish["_id"])
        score = 0.0
        
        # Category match
        cat = dish.get("category")
        if cat:
            score += (cat_prefs[cat] / total_cat_weight) * 0.4
            
        # Tag match
        dish_tags = set(dish.get("tags", []))
        if dish_tags:
            tag_score = sum(tag_prefs[t] for t in dish_tags)
            score += (tag_score / total_tag_weight) * 0.6
            
        scores[dish_id] = score
        
    # Normalize
    if not scores:
        return {}
    max_score = max(scores.values()) or 1
    return {k: v / max_score for k, v in scores.items()}

async def get_popularity_scores(db) -> Dict[str, float]:
    """Get global popularity scores (0-1)."""
    pipeline = [
        {"$match": {"action": "order"}},
        {"$group": {"_id": "$dish_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 50}
    ]
    popular = await db.logs_behavior.aggregate(pipeline).to_list(length=50)
    
    scores = {}
    if not popular:
        return scores
        
    max_count = popular[0]["count"]
    for p in popular:
        scores[str(p["_id"])] = p["count"] / max_count
        
    return scores

def calculate_diversity_penalty(selected_dishes: List[Dict], candidate_dish: Dict) -> float:
    """
    Calculate penalty if candidate dish category is already represented.
    Returns 0.0 (no penalty) to 0.8 (high penalty).
    """
    if not selected_dishes:
        return 0.0
        
    category = candidate_dish.get("category")
    same_cat_count = sum(1 for d in selected_dishes if d.get("category") == category)
    
    # Penalty increases with count: 0 -> 0, 1 -> 0.3, 2 -> 0.6, 3+ -> 0.8
    if same_cat_count == 0:
        return 0.0
    elif same_cat_count == 1:
        return 0.3
    elif same_cat_count == 2:
        return 0.6
    else:
        return 0.8

# --- Main Endpoints ---

@router.get("/recommend/{user_id}")
async def get_hybrid_recommendations(user_id: str):
    """
    Professional Vector Space Model Recommendation System
    Uses VectorEngine for feature-based matching and MMR for diversity.
    """
    db = await get_database()
    try:
        user_oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # 1. Fetch Data
    # Get all dishes
    all_dishes = await db.dishes.find().to_list(length=1000)
    
    # Get user history
    history = await db.logs_behavior.find(
        {"user_id": user_oid, "action": "order"}
    ).sort("timestamp", -1).limit(50).to_list(length=50)
    
    # Cooldown: Don't recommend dishes ordered in last 3 days
    cooldown_ids = set()
    now = datetime.now(pytz.UTC)
    for order in history:
        ts = order["timestamp"]
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=pytz.UTC)
        if (now - ts).days < 3:
            cooldown_ids.add(str(order["dish_id"]))

    # 2. Initialize Vector Engine
    from vector_engine import VectorEngine
    engine = VectorEngine(all_dishes)
    
    # 3. Build User Profile
    user_vector = engine.calculate_user_vector(history)
    
    # 4. Generate Recommendations
    if user_vector:
        # Context Awareness: Adjust user vector based on time of day
        # This is a "Query Expansion" technique in VSM
        current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
        
        # Modify the vector temporarily for this request
        # Indices: 0:spicy, 1:sweet, 2:salty, 3:sour, 4:oily, 5:fresh, 6:price, 7:cal, 8:pop
        
        if 6 <= current_hour < 10: # Breakfast
            # Reduce preference for spicy/oily, increase fresh/sweet(porridge)
            user_vector[0] *= 0.5 # Spicy
            user_vector[4] *= 0.3 # Oily
            user_vector[1] *= 1.2 # Sweet
        elif 17 <= current_hour < 21: # Dinner
            # Slight preference for lighter food (lower calories)
            # In our vector, index 7 is "High Calories". So we want to lower it?
            # Actually index 7 is normalized calories. If user likes high cal, this is high.
            # To recommend low cal, we should lower this component in the user vector
            user_vector[7] *= 0.8
            
        recommendations = engine.recommend(
            user_vector, 
            top_k=8, 
            diversity_alpha=0.75, # High precision, but some diversity
            exclude_ids=cooldown_ids
        )
    else:
        # Cold Start: Fallback to Popularity + Random
        # We can use the engine's internal dishes to pick popular ones
        # For simplicity, just pick random popular ones from all_dishes
        # Assuming all_dishes are already sorted or we sort them by some metric
        # Let's just pick random 8 to ensure something shows up
        available = [d for d in all_dishes if str(d["_id"]) not in cooldown_ids]
        random.shuffle(available)
        recommendations = available[:8]

    # Format IDs
    for r in recommendations:
        r["_id"] = str(r["_id"])
        
    return recommendations

@router.get("/top10/{user_id}")
async def get_top10(user_id: str):
    """
    Get user's yearly favorite dishes (Top 10 most ordered).
    """
    db = await get_database()
    
    try:
        user_oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Aggregate user's order history to find most ordered dishes
    pipeline = [
        {"$match": {"user_id": user_oid, "action": "order"}},
        {"$group": {"_id": "$dish_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    top_dishes = await db.logs_behavior.aggregate(pipeline).to_list(length=10)
    
    results = []
    for item in top_dishes:
        dish = await db.dishes.find_one({"_id": item["_id"]})
        if dish:
            dish["_id"] = str(dish["_id"])
            dish["order_count"] = item["count"]
            results.append(dish)
    
    return results
