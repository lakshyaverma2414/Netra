from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.resolution import ResolutionRequest, ResolutionResponse
from app.services.resolution_service import resolve_mentions

router = APIRouter(tags=["resolution"])

@router.post("/resolve", response_model=ResolutionResponse)
def resolve_entities_api(request: ResolutionRequest, db: Session = Depends(get_db)):
    return resolve_mentions(db, request)
