from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import schemas
from models import UserHealthProfile, RecommendedMealPlan


def calculate_bmr(user: UserHealthProfile) -> float:
    if user.gender == "male":
        bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
    else:
        bmr = 447.593 + (9.247 * user.weight) + (3.098 * user.height) - (4.330 * user.age)
    return bmr

def calculate_bmi(height: float, weight: float) -> float:
    return weight / (height / 100) ** 2

def recommend_diet(user: UserHealthProfile) -> str:
    bmi = calculate_bmi(user.height, user.weight)
    diet_recommendation = ""

    if user.diet_preference == "lose_weight":
        if bmi >= 30:
            diet_recommendation = "low-c, high-f"
        elif bmi >= 25 and bmi < 30:
            diet_recommendation = "low-c, high-p"
        else:
            diet_recommendation = "medium-c"
    elif user.diet_preference == "maintain_weight":
        if bmi < 18.5:
            diet_recommendation = "고칼로리, 영양소가 풍부한 식단을 추천합니다."
        elif bmi >= 18.5 and bmi < 24.9:
            diet_recommendation = "medium-c"
        elif bmi >= 25 and bmi < 30:
            diet_recommendation = "medium-c, high-p"
        else:
            diet_recommendation = "medium-c"
    elif user.diet_preference == "gain_weight":
        if bmi < 18.5:
            diet_recommendation = "high-c, high-p"
        elif bmi >= 18.5 and bmi < 24.9:
            diet_recommendation = "high-c, high-n"
        else:
            diet_recommendation = "medium-c"

    return diet_recommendation

def calculate_nutrients(daily_calories: float, diet_preference: str) -> dict:
    # 체중 관리 목표에 따른 영양소 비율 설정
    if diet_preference == "lose_weight":
        # 체중 감량: 단백질 비율 증가, 탄수화물 및 지방 비율 감소
        carb_ratio = 0.40
        protein_ratio = 0.40
        fat_ratio = 0.20
    elif diet_preference == "gain_weight":
        # 체중 증량: 탄수화물 및 지방 비율 증가, 단백질 비율 적당히
        carb_ratio = 0.50
        protein_ratio = 0.25
        fat_ratio = 0.25
    else:  # "maintain_weight"
        # 체중 유지: 균형 잡힌 비율
        carb_ratio = 0.50
        protein_ratio = 0.25
        fat_ratio = 0.25

    daily_calories = round(daily_calories)

    # 각 영양소의 칼로리 계산
    carb_calories = daily_calories * carb_ratio
    protein_calories = daily_calories * protein_ratio
    fat_calories = daily_calories * fat_ratio

    # 그램으로 변환
    carb_grams = carb_calories / 4
    protein_grams = protein_calories / 4
    fat_grams = fat_calories / 9

    return {
        "carbohydrates": round(carb_grams),
        "proteins": round(protein_grams),
        "fats": round(fat_grams)
    }

def calculate_daily_calories(user: UserHealthProfile) -> dict:
    # 기존 로직으로 일일 칼로리 계산
    bmr = calculate_bmr(user)
    daily_calories = bmr * user.activity_level

    # 다이어트 목표에 따른 칼로리 조정
    if user.diet_preference == "lose_weight":
        daily_calories -= 500
    elif user.diet_preference == "gain_weight":
        daily_calories += 500

    # 수정된 일일 칼로리에 따른 영양소 분배 계산
    nutrients = calculate_nutrients(daily_calories, user.diet_preference)

    return {
        "daily_calories": round(daily_calories),
        "nutrients": nutrients
    }

async def get_user_profile(db: AsyncSession, username: str):
    result = await db.execute(
        select(UserHealthProfile).filter(UserHealthProfile.username == username)
    )
    return result.scalars().first()


async def get_recommended_meal_plans(db: AsyncSession, username: str) -> dict:
    # 사용자 프로필 정보 가져오기
    user_profile = await get_user_profile(db, username)
    if not user_profile:
        return {"error": "User not found"}

    # 사용자 식단 선호도 계산
    diet_recommendation = recommend_diet(user_profile)

    # 사용자 알레르기 정보 가져오기
    user_allergies = user_profile.allergy_intolerance_type

    # 식단 추천 조회
    meal_types = ["breakfast", "lunch", "dinner", "snack"]
    recommended_meals = {}
    for meal_type in meal_types:
        query = select(RecommendedMealPlan).filter(
            RecommendedMealPlan.meal_type == meal_type,
            RecommendedMealPlan.diet_type.contains(diet_recommendation)
        )
        result = await db.execute(query)
        meals = result.scalars().all()

        # 알레르기 정보에 따라 음식 제외하고 Pydantic 모델로 변환
        suitable_meals = [
            schemas.RecommendedMealPlanBase.from_orm(meal) for meal in meals
            if not any(allergy in user_allergies for allergy in meal.allergy_intolerance_type)
        ]

        if suitable_meals:
            recommended_meals[meal_type] = suitable_meals
        else:
            recommended_meals[meal_type] = "No suitable meals found"

    return recommended_meals


async def create_user_health_profile(db: AsyncSession, health_profile: schemas.UserHealthProfileCreate):
    db_health_profile = UserHealthProfile(
        username=health_profile.username,
        allergy_intolerance_type=health_profile.allergy_intolerance_type,
        diet_preference=health_profile.diet_preference,
        age=health_profile.age,
        gender=health_profile.gender,
        height=health_profile.height,
        weight=health_profile.weight,
        activity_level=health_profile.activity_level,
    )
    db.add(db_health_profile)
    await db.commit()
    await db.refresh(db_health_profile)
    return db_health_profile

async def update_user_health_profile(db: AsyncSession, username: str, health_profile: schemas.UserHealthProfileCreate):
    result = await db.execute(
        select(UserHealthProfile).filter(UserHealthProfile.username == username)
    )
    db_health_profile = result.scalars().first()
    if db_health_profile:
        update_data = health_profile.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_health_profile, key, value)
        await db.commit()
        await db.refresh(db_health_profile)
    return db_health_profile


async def delete_user_health_profile(db: AsyncSession, username: str):
    async with db as session:
        result = await session.execute(select(UserHealthProfile).filter(
            UserHealthProfile.user_id == username))
        db_health_profile = result.scalars().first()
        if db_health_profile:
            await session.delete(db_health_profile)
            await session.commit()
            return db_health_profile
