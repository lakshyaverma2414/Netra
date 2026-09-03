from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import uuid
from app.agent.workflow import run_investigation

router = APIRouter(tags=["investigations"])

class InvestigationRequest(BaseModel):
    case_id: str
    question: str

@router.post("/query")
def query_investigation(request: InvestigationRequest):
    request_id = str(uuid.uuid4())
    result = run_investigation(request.case_id, request.question, request_id)
    return result
