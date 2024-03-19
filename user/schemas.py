# schemas.py
from __future__ import annotations

from pydantic import BaseModel, EmailStr
from typing import List, Union
from datetime import date

class UserHealthProfileBase(BaseModel):
    username: str
    diet_preference: str
    allergy_intolerance_type: List[str]
    age: int
    gender: str
    height: float
    weight: float
    activity_level: float

class UserHealthProfileCreate(UserHealthProfileBase):
    pass

class RecommendedMealPlanBase(BaseModel):
    id: int
    diet_type: str
    meal_type: str
    allergy_intolerance_type: List[str]
    food_info: str

    class Config:
        from_attributes = True
