from fastapi import FastAPI
from app.routes import sensor_routes
from app.database import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn :
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title = "RobosenseAPI",
    description = "로봇 센서 데이터 수집 API",
    version = "1.0.0",
    lifespan = lifespan
)
app.include_router(sensor_routes.router)

@app.get("/")
def root() :
    return {"message" : "Hi"}

@app.get("/health_check")
def health() :
    return {"health" : "Ok"}