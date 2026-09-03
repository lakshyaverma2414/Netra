from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.ingestion import router as ingestion_router
from app.api.extraction import router as extraction_router
from app.api.resolution import router as resolution_router
from app.api.validation import router as validation_router
# from app.api.relationships import router as relationships_router
from app.api.graph import router as graph_router
from app.api.analytics import router as analytics_router
from app.api.findings import router as findings_router
from app.api.investigations import router as investigations_router
from app.api.cases import router as cases_router
from app.api.entities import router as entities_router

app = FastAPI(
    title="SIH26189 AI Service",
    description="Python Intelligence Layer for Criminal Network Analysis System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(cases_router)
app.include_router(entities_router)
app.include_router(ingestion_router, prefix="/api/v1/ingestion")
app.include_router(extraction_router, prefix="/api/v1/extraction")
app.include_router(resolution_router, prefix="/api/v1/resolution")
app.include_router(validation_router, prefix="/api/v1/validation")
# app.include_router(relationships_router, prefix="/api/v1/relationships")
app.include_router(graph_router, prefix="/api/v1/graph")
app.include_router(analytics_router, prefix="/api/v1/analytics")
app.include_router(findings_router, prefix="/api/v1")
app.include_router(investigations_router, prefix="/api/v1/investigations")
