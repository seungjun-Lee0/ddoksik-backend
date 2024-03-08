import sys
sys.path.append('/home/app/code')
sys.path.append('/home/app/code/user')
from fastapi import Depends, APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import services, schemas
from auth import verify_token
from database import get_db
from config import cognito_client, COGNITO_USERPOOL_ID

from opentracing.ext import tags
from opentracing.propagation import Format
from opentelemetry.propagate import inject
from jaeger_client import Config

app = FastAPI()
router = APIRouter()

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

tracer = init_jaeger_tracer('user')

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

# List of allowed origins (the front-end application URL)
origins = [
    "http://www.bangwol08.com",
    "http://user-svc:8000",
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

@app.get("/api/v1/user/protected-route")
async def protected_route(user=Depends(verify_token)):
    return {"message": "This is a protected route"}

@app.post("/api/v1/user/delete-user/")
async def delete_user(username: str):
    try:
        # Cognito 사용자 풀 ID와 사용자 이름(또는 사용자의 Cognito ID)을 사용하여 사용자 삭제
        response = cognito_client.admin_delete_user(
            UserPoolId=COGNITO_USERPOOL_ID,
            Username=username
        )
        return {"message": "User deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/user/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def read_user_profile(username: str, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    db_user_profile = await services.get_user_profile(db, username=username)
    if db_user_profile is None:
        raise HTTPException(status_code=404, detail="User Profile not found")
    return db_user_profile

@app.post("/api/v1/user/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def create_health_profile_for_user(health_profile: schemas.UserHealthProfileCreate, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    return await services.create_user_health_profile(db=db, health_profile=health_profile)

@app.put("/api/v1/user/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def update_health_profile(username: str, health_profile: schemas.UserHealthProfileCreate, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    return await services.update_user_health_profile(db=db, username=username, health_profile=health_profile)

@app.delete("/api/v1/user/users/{username}/health_profiles/", response_model=schemas.UserHealthProfileBase)
async def delete_health_profile(username: str, db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    return await services.delete_user_health_profile(db=db, username=username)


app.include_router(router)
