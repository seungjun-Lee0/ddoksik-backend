from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

# FoodItem 모델 정의
class FoodItem(Base):
    __tablename__ = "food_items"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    calories = Column(Float, nullable=True)  # Optional은 여기서 제거
    protein = Column(Float, nullable=True)  # SQLAlchemy 컬럼으로 정의
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    serve_size = Column(String, nullable=True)

# MealPlan 모델 정의
class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, ForeignKey('user_health_profiles.username'), nullable=False)
    current_date = Column(Date)
    meal_type = Column(String)
    food_items = Column(ARRAY(Integer), nullable=True)  # PostgreSQL ARRAY type 사용

    # Relationship to FoodItem through meal_plan_food_item association table
    user = relationship("UserHealthProfile", back_populates="meal_plans")
    foods = relationship("FoodItem", secondary="meal_plan_food_item")

# Association table for the many-to-many relationship between MealPlan and FoodItem
meal_plan_food_item = Table(
    'meal_plan_food_item', Base.metadata,
    Column('meal_plan_id', ForeignKey('meal_plans.id'), primary_key=True),
    Column('food_item_id', ForeignKey('food_items.id'), primary_key=True)
)

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
