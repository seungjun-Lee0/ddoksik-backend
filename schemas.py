# schemas.py
from __future__ import annotations

from pydantic import BaseModel, EmailStr
from typing import List, Union
from datetime import date

# class UserBase(BaseModel):
#     username: str
#     email: EmailStr
#
# class UserGet(BaseModel):
#     id: int
#     username: str
#     email: EmailStr
#
# class UserCreate(UserBase):
#     password: str

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

# class User(UserBase):
#     id: int
#     health_profiles: List[UserHealthProfileBase] = []
#
#     class Config:
#         from_attributes = True

# from pydantic import BaseModel
#
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str
#
# class TokenData(BaseModel):
#     username: Union[str, None] = None

# class ChangePassword(BaseModel):
#     current_password: str
#     new_password: str
#
# class ChangeEmail(BaseModel):
#     new_email: EmailStr
#     verification_code: str
#
# class EmailVerification(BaseModel):
#     email: EmailStr