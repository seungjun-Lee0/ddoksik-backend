from __future__ import annotations

from pydantic import BaseModel, EmailStr
from typing import List, Union
from datetime import date

class UserHealthProfileBase(BaseModel):
    username: str
    diet_preference: str
    allergy_intolerance_type: List[str]
    birth_date: date
    age: int
    gender: str
    height: float
    weight: float
    target_weight: float

class UserHealthProfileCreate(UserHealthProfileBase):
    pass