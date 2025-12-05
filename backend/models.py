from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

from typing import Annotated, Any
from pydantic import BaseModel, Field, BeforeValidator

# Pydantic V2 compatible ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class Dish(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    name: str
    category: str # Added category field
    price: float
    calories: int = 0
    tags: List[str] = []
    description: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class User(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    username: str
    preferences: Dict[str, float] = {} # e.g., {"spicy": 0.8, "sweet": 0.2}

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class LogBehavior(BaseModel):
    user_id: PyObjectId
    dish_id: PyObjectId
    action: str # view, order, like
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {
        "json_encoders": {datetime: lambda v: v.isoformat()}
    }
