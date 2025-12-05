import math
from datetime import datetime
from typing import List, Dict, Tuple
import pytz

class VectorEngine:
    """
    A pure Python implementation of a Vector Space Model recommendation engine.
    Features:
    - 9-dimensional feature space for dishes
    - Time-decayed user profiling
    - Cosine similarity
    - MMR (Maximal Marginal Relevance) for diversity
    """

    # Feature Dimensions
    DIMENSIONS = [
        'spicy', 'sweet', 'salty', 'sour', 'oily', 'fresh',
        'price_sensitivity', 'health_conscious', 'popularity'
    ]
    
    def __init__(self, all_dishes: List[Dict]):
        """
        Initialize the engine with all available dishes.
        Pre-computes feature vectors for all dishes.
        """
        self.dishes = {str(d['_id']): d for d in all_dishes}
        self.dish_vectors = {}
        
        # Pre-compute global stats for normalization
        prices = [d.get('price', 0) for d in all_dishes]
        calories = [d.get('calories', 0) for d in all_dishes]
        
        self.max_price = max(prices) if prices else 1
        self.min_price = min(prices) if prices else 0
        self.max_cal = max(calories) if calories else 1
        self.min_cal = min(calories) if calories else 0
        
        # Build vectors
        for dish in all_dishes:
            self.dish_vectors[str(dish['_id'])] = self._extract_features(dish)

    def _extract_features(self, dish: Dict) -> List[float]:
        """
        Convert a dish dictionary into a normalized feature vector.
        """
        vector = [0.0] * len(self.DIMENSIONS)
        tags = set(dish.get('tags', []))
        category = dish.get('category', '')
        
        # 1. Taste Features (0-5 mapped to 0-1, or binary presence)
        # Assuming tags might contain "微辣", "重辣" etc, or just "辣"
        # For simplicity in this demo, we check substring presence
        
        # Spicy
        if '重辣' in tags or '辣' in tags: vector[0] = 0.8
        elif '微辣' in tags: vector[0] = 0.3
        
        # Sweet
        if '甜' in tags or '糖' in dish.get('name', ''): vector[1] = 0.7
        
        # Salty (Default assumption for most main dishes)
        if category in ['热菜', '荤菜']: vector[2] = 0.5
        if '咸' in tags: vector[2] = 0.8
        
        # Sour
        if '酸' in tags or '醋' in dish.get('name', ''): vector[3] = 0.8
        
        # Oily
        if '油炸' in tags or category == '荤菜': vector[4] = 0.8
        elif category == '轻食': vector[4] = 0.1
        else: vector[4] = 0.4
        
        # Fresh (鲜)
        if '海鲜' in tags or '汤' in category: vector[5] = 0.7
        
        # 2. Price Sensitivity (Normalized)
        # Lower price = Higher sensitivity score (preference for cheap)
        # But here this is a DISH attribute. 
        # Let's define this dimension as "Price Level" (0=Cheap, 1=Expensive)
        # When building user profile, if user buys expensive, they get high score here.
        price = dish.get('price', 0)
        if self.max_price > self.min_price:
            vector[6] = (price - self.min_price) / (self.max_price - self.min_price)
            
        # 3. Health Conscious (Calories)
        # Higher calories = Higher score in this dimension
        # User who likes high cal will match high cal dishes
        cal = dish.get('calories', 0)
        if self.max_cal > self.min_cal:
            vector[7] = (cal - self.min_cal) / (self.max_cal - self.min_cal)
            
        # 4. Popularity (Placeholder, updated dynamically usually, but static here for vector)
        # We can pass popularity in dish dict if available, else 0.5
        vector[8] = dish.get('popularity_score', 0.5)
        
        return vector

    def calculate_user_vector(self, history: List[Dict]) -> List[float]:
        """
        Build user profile vector based on order history with time decay.
        """
        if not history:
            return None
            
        user_vector = [0.0] * len(self.DIMENSIONS)
        total_weight = 0.0
        
        now = datetime.now(pytz.UTC)
        
        for order in history:
            dish_id = str(order['dish_id'])
            if dish_id not in self.dish_vectors:
                continue
                
            # Time Decay Weight
            ts = order['timestamp']
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=pytz.UTC)
                
            days_ago = (now - ts).days
            # Decay: Recent orders matter much more. Half-life approx 7 days.
            weight = math.exp(-days_ago / 7.0)
            
            dish_vec = self.dish_vectors[dish_id]
            
            for i in range(len(self.DIMENSIONS)):
                user_vector[i] += dish_vec[i] * weight
                
            total_weight += weight
            
        if total_weight == 0:
            return None
            
        # Normalize
        return [x / total_weight for x in user_vector]

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        """
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    def recommend(self, user_vector: List[float], top_k: int = 8, diversity_alpha: float = 0.7, exclude_ids: set = None) -> List[Dict]:
        """
        Get recommendations using MMR (Maximal Marginal Relevance).
        
        Args:
            user_vector: The user's profile vector.
            top_k: Number of recommendations to return.
            diversity_alpha: 0-1. Higher = More relevance, Lower = More diversity.
            exclude_ids: Set of dish IDs to exclude (e.g. recently ordered).
        """
        if not user_vector:
            # Cold start: Return random popular dishes (simplified here)
            # In real app, caller handles cold start or we return top popularity
            return []
            
        candidates = []
        for did, vec in self.dish_vectors.items():
            if exclude_ids and did in exclude_ids:
                continue
                
            sim = self.cosine_similarity(user_vector, vec)
            candidates.append({
                'id': did,
                'dish': self.dishes[did],
                'vector': vec,
                'relevance': sim
            })
            
        # Filter candidates with very low relevance to speed up MMR
        candidates.sort(key=lambda x: x['relevance'], reverse=True)
        candidates = candidates[:50] # Top 50 relevant candidates
        
        # MMR Selection
        selected = []
        
        while len(selected) < top_k and candidates:
            best_mmr_score = -float('inf')
            best_idx = -1
            
            for i, cand in enumerate(candidates):
                # Relevance part
                relevance = cand['relevance']
                
                # Diversity part (Max similarity to already selected)
                max_sim_to_selected = 0.0
                for sel in selected:
                    sim = self.cosine_similarity(cand['vector'], sel['vector'])
                    if sim > max_sim_to_selected:
                        max_sim_to_selected = sim
                        
                # MMR Formula
                mmr = diversity_alpha * relevance - (1 - diversity_alpha) * max_sim_to_selected
                
                if mmr > best_mmr_score:
                    best_mmr_score = mmr
                    best_idx = i
            
            if best_idx != -1:
                selected.append(candidates.pop(best_idx))
            else:
                break
                
        return [s['dish'] for s in selected]
