from fastapi import Depends, APIRouter, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import services, schemas
from database import engine, get_db


app = FastAPI()
router = APIRouter()

# List of allowed origins (the front-end application URL)
origins = [
    "http://localhost:3000",  # Adjust the port if your React app runs on a different one
    # You can add more origins if needed
]

# Add CORSMiddleware to the application instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows the specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# async def create_tables():
#     async with engine.begin() as conn:
#         # Replace Base.metadata.create_all with your models' metadata
#         await conn.run_sync(models.Base.metadata.create_all)
#
# @app.on_event("startup")
# async def startup_event():
#     await create_tables()

# @router.get("/token/auth")
# async def login_for_access_token(current_user: dict = Depends(get_current_user)):
#     return current_user
#
# @router.post("/token")
# async def login_for_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
#     user = await services.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer"}
#
# @app.post("/users/", response_model=schemas.User)
# async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
#     # Check if the username is already taken
#     db_user_by_username = await services.get_user_by_username(db,
#                                                               username=user.username)
#     if db_user_by_username:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
#
#     # Check if the email is already registered
#     db_user_by_email = await services.get_user_by_email(db, email=user.email)
#     if db_user_by_email:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
#
#     try:
#         # Attempt to create the user
#         created_user = await services.create_user(db=db, user=user)
#         return created_user
#     except IntegrityError:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="A user with this username or email already exists."
#         )
#
# @app.get("/users/{username}", response_model=schemas.User)
# async def read_user(username: str, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     db_user = await services.get_user(db, username=username)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

@app.get("/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def read_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    db_user_profile = await services.get_user_profile(db, username=username)
    if db_user_profile is None:
        raise HTTPException(status_code=404, detail="User Profile not found")
    return db_user_profile

@app.post("/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def create_health_profile_for_user(health_profile: schemas.UserHealthProfileCreate, db: AsyncSession = Depends(get_db)):
    return await services.create_user_health_profile(db=db, health_profile=health_profile)

@app.put("/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def update_health_profile(username: str, health_profile: schemas.UserHealthProfileCreate, db: AsyncSession = Depends(get_db)):
    return await services.update_user_health_profile(db=db, username=username, health_profile=health_profile)

@app.delete("/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def delete_health_profile(username: str, db: AsyncSession = Depends(get_db)):
    return await services.delete_user_health_profile(db=db, username=username)

app.include_router(router)
