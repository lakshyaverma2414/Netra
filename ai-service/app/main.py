from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.ingestion import router as ingestion_router
from app.api.extraction import router as extraction_router

app = FastAPI(
    title="SIH26189 AI Service",
    description="Python Intelligence Layer for Criminal Network Analysis System",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(ingestion_router, prefix="/api/v1/ingestion")
app.include_router(extraction_router, prefix="/api/v1/extraction")
