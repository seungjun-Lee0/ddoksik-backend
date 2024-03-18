import sys
sys.path.append('/home/app/code')
sys.path.append('/home/app/code/diet')
from opentracing.ext import tags
from opentracing.propagation import Format
from opentelemetry.propagate import inject
from jaeger_client import Config

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
    "https://www.ddoksik2.site/"
]

# Add CORSMiddleware to the application instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows the specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def init_jaeger_tracer(service_name):
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service_name,
        validate=True,
    )
    return config.initialize_tracer()

tracer = init_jaeger_tracer('diet') #서비스 이름별로 수정해줘야 함

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

# FastAPI middleware로 Jaeger 트레이싱 설정
@app.middleware("http")
async def add_span(request: Request, call_next):
    if request.url.path == '/':
        # Skip tracing for the root path
        response = await call_next(request)
        return response

    #headers = dict(request.headers)
    headers = {}
    inject(headers)
    span_ctx = tracer.extract(Format.HTTP_HEADERS, headers)
    scope = tracer.start_active_span(
        request.url.path,
        child_of=span_ctx,
        tags={tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER},
    )

    request.scope["span"] = scope.span
    scope.close()
    response = await call_next(request)
    
    return response

@app.get("/api/v1/diet/get-nutrition-info/")
async def get_nutrition_info(search_term: str, page_no: int = Query(default=1), num_of_rows: int = Query(default=10)):
    # API Gateway를 통해 Lambda 함수 호출, 쿼리 파라미터 추가
    url = f"https://vxv6fyabuyipaimfzpsgwlkdru0qfbdq.lambda-url.ap-northeast-2.on.aws/?search_term={search_term}&pageNo={page_no}&numOfRows={num_of_rows}"
    try:
        response = httpx.get(url)
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/v1/diet/diets/{username}/meal-plans", response_model= schemas.MealPlan)
async def create_meal_plan_endpoint(meal_plan: schemas.MealPlanCreate, db: AsyncSession = Depends(get_db)):
    return await services.create_or_update_meal_plan(db=db, meal_plan_create=meal_plan)

@app.get("/api/v1/diet/diets/{username}/meal-plans")
async def get_meal_plans(username: str, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    meal_plans = await services.get_meal_plans_by_username(db, username)
    return meal_plans

@app.get("/api/v1/diet/diets/{username}/daily-nutrition-totals", response_model=dict)
async def get_daily_nutrition_totals(username: str, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    daily_nutrition_totals = await services.calculate_daily_nutrition_totals(db, username)
    return daily_nutrition_totals

@app.get("/api/v1/diet/diets/{username}/meal-plans/grouped", response_model=schemas.MealPlanGrouped)
async def get_meal_plans_grouped(username: str, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    grouped_meal_plans = await services.get_grouped_meal_plans(db, username)
    return {"grouped_meal_plans": grouped_meal_plans}

@app.get("/api/v1/diet/diets/{username}/weekly-calories")
async def get_weekly_calories(username: str, db: AsyncSession = Depends(get_db)):
    recent_calories, previous_calories = await services.calculate_recent_and_previous_week_calories(db, username)
    # 결과 반환
    return {
        "recent_week_calories": recent_calories,
        "previous_week_calories": previous_calories
    }

@app.put("/api/v1/diet/meal-plans/{meal_plan_id}", response_model=schemas.MealPlan)
async def update_meal_plan_endpoint(meal_plan_id: int, meal_plan_data: schemas.MealPlanUpdate, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    updated_meal_plan = await services.update_meal_plan(db, meal_plan_id, meal_plan_data)
    if not updated_meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return updated_meal_plan

@app.delete("/api/v1/diet/meal-plans/{meal_plan_id}")
async def delete_meal_plan(meal_plan_id: int, db: AsyncSession = Depends(get_db)):
    success = await services.delete_meal_plan(db, meal_plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="MealPlan not found")
    return {"ok": True}
