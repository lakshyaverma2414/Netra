from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from app.schemas.extraction import EntityTypeEnum

class ResolutionStatusEnum(str, Enum):
    CONFIRMED = "CONFIRMED"
    PROBABLE = "PROBABLE"
    CANDIDATE = "CANDIDATE"
    REJECTED = "REJECTED"

class MentionInput(BaseModel):
    text: str
    entity_type: EntityTypeEnum
    source_record_id: Optional[str] = None
    observation_id: Optional[str] = None

class ResolutionRequest(BaseModel):
    case_id: str
    mentions: List[MentionInput]

class ResolutionResultItem(BaseModel):
    mention: str
    entity_type: EntityTypeEnum
    status: ResolutionStatusEnum
    entity_id: Optional[str] = None
    canonical_name: Optional[str] = None
    score: float
    matching_methods: List[str]

class ResolutionResponse(BaseModel):
    request_id: str
    results: List[ResolutionResultItem]


class ProvenanceLink(BaseModel):
    record_id: str
    mention_id: str
    confidence: float

class CanonicalEntity(BaseModel):
    entity_id: str
    entity_type: str
    canonical_name: str
    source_mentions: List[ProvenanceLink]
