from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.db.database import get_db
from app.services.findings_service import FindingsService

router = APIRouter(tags=["findings"])

class FeedbackRequest(BaseModel):
    decision: str
    reason: str

@router.get("/cases/{case_id}/findings")
def list_case_findings(case_id: str, db: Session = Depends(get_db)):
    svc = FindingsService(db)
    findings = svc.get_findings_for_case(case_id)
    return {"case_id": case_id, "findings": findings}

@router.get("/findings/{finding_id}")
def get_finding_detail(finding_id: str, db: Session = Depends(get_db)):
    svc = FindingsService(db)
    detail = svc.get_finding_detail(finding_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Finding not found")
    return detail

@router.post("/findings/{finding_id}/feedback")
def submit_feedback(finding_id: str, request: FeedbackRequest, db: Session = Depends(get_db)):
    svc = FindingsService(db)
    # Using a dummy investigator ID for now as per requirement: 
    # "For the standalone AI service, follow the current authentication/test convention rather than inventing fake identities."
    # We will just pass None or a static test UUID if required. We'll use None.
    try:
        result = svc.submit_feedback(finding_id, request.decision, request.reason, investigator_id=None)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
