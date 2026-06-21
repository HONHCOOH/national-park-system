from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import dashboard, ecology, fire, risk, resource, chat
from app.utils.data_generator import generate_all_mock_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    generate_all_mock_data()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="国家公园模拟系统智能决策支持研究平台",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(ecology.router)
app.include_router(fire.router)
app.include_router(risk.router)
app.include_router(resource.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
