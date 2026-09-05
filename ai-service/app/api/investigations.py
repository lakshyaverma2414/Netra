from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.agent.workflow import run_investigation

router = APIRouter(tags=["investigations"])

class InvestigationRequest(BaseModel):
    case_id: str
    question: str
    request_id: Optional[str] = None
    investigator_id: Optional[str] = None
    thread_id: Optional[str] = None

@router.post("/query")
def query_investigation(request: InvestigationRequest):
    request_id = request.request_id or str(uuid.uuid4())
    result = run_investigation(request.case_id, request.question, request_id, request.thread_id)
    return result
