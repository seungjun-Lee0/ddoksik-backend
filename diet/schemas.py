from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class MealPlanBase(BaseModel):
    username: str
    meal_type: str
    desc_kor: str
    quantity: int
    nutrients: Dict[str, str]
    current_date: Optional[date] = Field(default_factory=date.today)  # 기본값으로 오늘 날짜 설정

class MealPlanCreate(BaseModel):
    meal_type: str
    username: str
    desc_kor: str
    quantity: int
    nutrients: Dict[str, str]
    current_date: Optional[date] = Field(default_factory=date.today)  # 기본값으로 오늘 날짜 설정

    class Config:
        from_attributes = True


class MealPlan(MealPlanBase):
    id: int

    class Config:
        from_attributes = True

class MealPlanUpdate(BaseModel):  # 식단 업데이트를 위한 스키마, 선택적 필드를 포함
    meal_type: Optional[str] = None
    desc_kor: Optional[str] = None  # 선택적 업데이트를 위해 추가
    quantity: Optional[int] = None
    nutrients: Optional[dict] = None
    current_date: Optional[date] = None


# class GroupedMealPlanItem(BaseModel):
#     id: int
#     desc_kor: str
#     quantity: int
#     nutrients: Dict[str, str]
#
# class MealTypeGroup(BaseModel):
#     items: List[GroupedMealPlanItem]
#
# class MealPlanGroupedByDateAndType(BaseModel):
#     date: date
#     meal_type: str
#     meal_plans: List[GroupedMealPlanItem]

class MealPlanGrouped(BaseModel):
    grouped_meal_plans: Dict[date, Dict[str, Any]]
