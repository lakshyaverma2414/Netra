from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ValidationStatusEnum(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANDIDATE = "CANDIDATE"
    REJECTED = "REJECTED"

class ValidationRequest(BaseModel):
    case_id: str
    assertion_id: Optional[str] = None
    source_entity_id: str
    relationship_type: str
    target_entity_id: str
    source_record_id: Optional[str] = None
    evidence_ids: Optional[List[str]] = []
    extraction_method: Optional[str] = "Qwen-4B"
    extracted_text: Optional[str] = None

class ValidationResponse(BaseModel):
    request_id: str
    status: ValidationStatusEnum
    relationship_id: Optional[str] = None
    reasons: List[str]
    validator_version: str = "relationship-validator-v1"
