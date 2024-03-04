from collections import defaultdict
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import MealPlan
from .schemas import MealPlanCreate, MealPlanUpdate

MEAL_TYPE_ORDER = {
    "breakfast": 1,
    "lunch": 2,
    "dinner": 3,
    "snack": 4
}

async def create_or_update_meal_plan(db: AsyncSession, meal_plan_create: MealPlanCreate):
    stmt = select(MealPlan).where(
        MealPlan.username == meal_plan_create.username,
        MealPlan.meal_type == meal_plan_create.meal_type,
        MealPlan.desc_kor == meal_plan_create.desc_kor,
        MealPlan.current_date == meal_plan_create.current_date if meal_plan_create.current_date else date.today()
    )
    result = await db.execute(stmt)
    existing_meal_plan = result.scalars().first()

    if existing_meal_plan:
        # 존재하면 수량만 업데이트
        existing_meal_plan.quantity += meal_plan_create.quantity
    else:
        # 존재하지 않으면 새로운 음식 추가
        new_meal_plan = MealPlan(**meal_plan_create.dict())
        db.add(new_meal_plan)

    await db.commit()

    if existing_meal_plan:
        await db.refresh(existing_meal_plan)
        return existing_meal_plan
    else:
        await db.refresh(new_meal_plan)
        return new_meal_plan

async def get_meal_plans_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(MealPlan).filter(MealPlan.username == username))
    return result.scalars().all()



async def get_grouped_meal_plans(db: AsyncSession, username: str):
    stmt = select(MealPlan).where(MealPlan.username == username)
    results = await db.execute(stmt)
    meal_plans = results.scalars().all()

    grouped_data = defaultdict(lambda: defaultdict(list))

    for meal_plan in meal_plans:
        meal_plan_data = {
            "id": meal_plan.id,
            "desc_kor": meal_plan.desc_kor,
            "quantity": meal_plan.quantity,
            "nutrients": meal_plan.nutrients,
        }
        grouped_data[meal_plan.current_date][meal_plan.meal_type].append(meal_plan_data)

    # 결과를 정렬된 순서로 재구성
    sorted_grouped_data = defaultdict(lambda: defaultdict(list))
    for date, meals in grouped_data.items():
        # Ensure all meal types are present for each date
        for meal_type in MEAL_TYPE_ORDER:
            if meal_type in meals:
                sorted_grouped_data[date][meal_type] = meals[meal_type]
            else:
                # Add empty list for missing meal types
                sorted_grouped_data[date][meal_type] = []
        # Optionally sort the meal types within each date based on predefined order
        sorted_grouped_data[date] = {k: sorted_grouped_data[date][k] for k in sorted(sorted_grouped_data[date], key=lambda x: MEAL_TYPE_ORDER.get(x, 5))}

    return sorted_grouped_data


async def update_meal_plan(db: AsyncSession, meal_plan_id: int, meal_plan_update: MealPlanUpdate):
    # 식단 항목 조회
    stmt = select(MealPlan).where(MealPlan.id == meal_plan_id)
    result = await db.execute(stmt)
    meal_plan = result.scalars().first()

    if not meal_plan:
        return None  # 식단 항목이 존재하지 않는 경우

    # 업데이트할 정보가 제공된 경우 해당 필드를 업데이트
    if meal_plan_update.meal_type is not None:
        meal_plan.meal_type = meal_plan_update.meal_type
    if meal_plan_update.desc_kor is not None:
        meal_plan.desc_kor = meal_plan_update.desc_kor
    if meal_plan_update.quantity is not None:
        meal_plan.quantity = meal_plan_update.quantity
    if meal_plan_update.nutrients is not None:
        meal_plan.nutrients = meal_plan_update.nutrients
    if meal_plan_update.current_date is not None:
        meal_plan.current_date = meal_plan_update.current_date

    # 변경사항을 데이터베이스에 반영
    await db.commit()
    await db.refresh(meal_plan)

    return meal_plan

async def delete_meal_plan(db: AsyncSession, meal_plan_id: int):
    stmt = select(MealPlan).where(MealPlan.id == meal_plan_id)
    result = await db.execute(stmt)
    meal_plan = result.scalars().first()

    if meal_plan:
        await db.delete(meal_plan)
        await db.commit()
        return True
    return False