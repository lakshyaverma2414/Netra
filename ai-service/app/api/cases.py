from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.db.database import get_db
from app.db.repositories.case_repository import CaseRepository
from app.db.models import CaseStatus
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

class CaseCreate(BaseModel):
    case_id: str
    case_number: str
    title: str
    description: str = None

@router.post("")
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    repo = CaseRepository(db)
    existing = repo.get_by_id(case_in.case_id)
    if existing:
        raise HTTPException(status_code=400, detail="Case already exists")
    case = repo.create(case_in.case_id, case_in.case_number, case_in.title, case_in.description)
    db.commit()
    return {"case_id": case.case_id, "status": case.status}

@router.get("")
def list_cases(db: Session = Depends(get_db)):
    repo = CaseRepository(db)
    cases = repo.list_accessible_cases()
    return [{"case_id": c.case_id, "title": c.title, "status": c.status} for c in cases]

@router.get("/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    repo = CaseRepository(db)
    c = repo.get_by_id(case_id)
    if not c:
        raise HTTPException(status_code=404)
    return {"case_id": c.case_id, "title": c.title, "status": c.status}
