import httpx
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from . import services, schemas
from auth import verify_token

app = FastAPI()

# List of allowed origins (the front-end application URL)
origins = [
    "http://localhost:3000",
    "http://localhost:8000"
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

async def log_request_data(request: Request, call_next):
    body = await request.body()
    # 요청 본문 로그 출력
    print(body)
    response = await call_next(request)
    return response

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    return await log_request_data(request, call_next)

@app.get("/get-nutrition-info/")
async def get_nutrition_info(search_term: str, page_no: int = Query(default=1), num_of_rows: int = Query(default=10)):
    # API Gateway를 통해 Lambda 함수 호출, 쿼리 파라미터 추가
    url = f"https://vxv6fyabuyipaimfzpsgwlkdru0qfbdq.lambda-url.ap-northeast-2.on.aws/?search_term={search_term}&pageNo={page_no}&numOfRows={num_of_rows}"
    try:
        response = httpx.get(url)
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/diets/{username}/meal-plans", response_model= schemas.MealPlan)
async def create_meal_plan_endpoint(meal_plan: schemas.MealPlanCreate, db: AsyncSession = Depends(get_db)):
    return await services.create_or_update_meal_plan(db=db, meal_plan_create=meal_plan)

@app.get("/diets/{username}/meal-plans")
async def get_meal_plans(username: str, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    meal_plans = await services.get_meal_plans_by_username(db, username)
    return meal_plans

@app.get("/diets/{username}/meal-plans/grouped", response_model=schemas.MealPlanGrouped)
async def get_meal_plans_grouped(username: str, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    grouped_meal_plans = await services.get_grouped_meal_plans(db, username)
    return {"grouped_meal_plans": grouped_meal_plans}

@app.put("/meal-plans/{meal_plan_id}", response_model=schemas.MealPlan)
async def update_meal_plan_endpoint(meal_plan_id: int, meal_plan_data: schemas.MealPlanUpdate, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    updated_meal_plan = await services.update_meal_plan(db, meal_plan_id, meal_plan_data)
    if not updated_meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return updated_meal_plan

@app.delete("/meal-plans/{meal_plan_id}")
async def delete_meal_plan(meal_plan_id: int, db: AsyncSession = Depends(get_db)):
    success = await services.delete_meal_plan(db, meal_plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="MealPlan not found")
    return {"ok": True}