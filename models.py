from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

# MealPlan 모델 정의
class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, ForeignKey('user_health_profiles.username'), nullable=False)
    desc_kor = Column(String)
    meal_type = Column(String)
    nutrients = Column(JSON)
    current_date = Column(Date)
    quantity = Column(Integer)
    # Relationship to FoodItem through meal_plan_food_item association table
    user = relationship("UserHealthProfile", back_populates="meal_plans")

class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    diet_preference = Column(String)
    allergy_intolerance_type = Column(JSON)
    age = Column(Integer)
    gender = Column(String)
    height = Column(Float)
    weight = Column(Float)
    activity_level = Column(Float)
    meal_plans = relationship("MealPlan", back_populates="user")
