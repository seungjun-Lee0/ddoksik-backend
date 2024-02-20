from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import schemas
from models import UserHealthProfile

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# async def get_user(db: AsyncSession, username: str):
#     result = await db.execute(
#         select(models.User).filter(models.User.username == username)
#     )
#     return result.scalars().first()
#
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
        birth_date=health_profile.birth_date,
        age=health_profile.age,
        gender=health_profile.gender,
        height=health_profile.height,
        weight=health_profile.weight,
        target_weight=health_profile.target_weight,
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

# async def authenticate_user(db: AsyncSession, username: str, password: str):
#     user = await get_user_by_username(db, username)
#     if not user:
#         return False
#     if not pwd_context.verify(password, user.hashed_password):
#         return False
#     return user

# async def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
# async def change_user_password(db: AsyncSession, user: models.User, new_password: str):
#     user.hashed_password = pwd_context.hash(new_password)
#     await db.commit()
#
# async def change_user_email(db: AsyncSession, user: models.User, new_email: str):
#     user.email = new_email
#     await db.commit()
#
# async def send_verification_email(email: EmailStr):
#     verification_code = secrets.token_hex(3) # 간단한 인증 코드 생성
#     message = MessageSchema(
#         subject="Your Verification Code",
#         recipients=[email],
#         body=f"Your verification code is: {verification_code}",
#         subtype="html"
#     )
#
#     fm = FastMail(conf)
#     await fm.send_message(message)
#     return verification_code
