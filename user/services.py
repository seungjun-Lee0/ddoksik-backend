from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import schemas
from models import UserHealthProfile

async def get_user_profile(db: AsyncSession, username: str):
    result = await db.execute(
        select(UserHealthProfile).filter(UserHealthProfile.username == username)
    )
    return result.scalars().first()

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
