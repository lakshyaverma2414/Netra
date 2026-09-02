from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(
    title="SIH26189 AI Service",
    description="Python Intelligence Layer for Criminal Network Analysis System",
    version="0.1.0",
)

app.include_router(health_router)
