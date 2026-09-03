from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.validation import ValidationRequest, ValidationResponse
from app.services.validation_service import validate_relationship

router = APIRouter(tags=["validation"])

@router.post("/relationships", response_model=ValidationResponse)
def validate_relationships_api(request: ValidationRequest, db: Session = Depends(get_db)):
    return validate_relationship(db, request)
