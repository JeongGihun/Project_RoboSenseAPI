from fastapi import FastAPI
from app.routes import sensor_routes

app = FastAPI(
    title = "RobosenseAPI",
    description = "로봇 센서 데이터 수집 API",
    version = "1.0.0"
)

app.include_router(sensor_routes.router)

@app.get("/")
def root() :
    return {"message" : "Hi"}

@app.get("/health_check")
def health() :
    return {"health" : "Ok"}