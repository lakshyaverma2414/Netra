from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from app.schemas.ingestion import NormalizedRecord

class EntityMention(BaseModel):
    mention_id: str = Field(default_factory=lambda: f"M-{uuid.uuid4().hex[:8]}")
    record_id: str
    entity_type: str
    text: str
    normalized_value: str
    extraction_method: str
    confidence: float
    start: Optional[int] = None
    end: Optional[int] = None

class ExtractionRequest(BaseModel):
    records: List[NormalizedRecord]

class ExtractionResponse(BaseModel):
    record_count: int
    entity_count: int
    entities: List[EntityMention]
