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
from enum import Enum

class EntityTypeEnum(str, Enum):
    PERSON = "PERSON"
    PHONE = "PHONE"
    IMEI = "IMEI"
    VEHICLE = "VEHICLE"
    LOCATION = "LOCATION"
    ORGANIZATION = "ORGANIZATION"
    EVENT = "EVENT"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    UPI_ID = "UPI_ID"
    SOCIAL_ACCOUNT = "SOCIAL_ACCOUNT"
    CASE = "CASE"

class RelationshipTypeEnum(str, Enum):
    USES = "USES"
    OWNS = "OWNS"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    LOCATED_AT = "LOCATED_AT"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    LINKED_TO = "LINKED_TO"
    INVOLVED_IN = "INVOLVED_IN"

class ExtractedEntity(BaseModel):
    mention: str
    type: EntityTypeEnum

class EntityExtractionRequest(BaseModel):
    case_id: str
    text: str

class EntityExtractionResponse(BaseModel):
    case_id: str
    entities: List[ExtractedEntity]

class ExtractedRelationship(BaseModel):
    source_mention: str
    relationship_type: RelationshipTypeEnum
    target_mention: str
    evidence_text: str

class RelationshipExtractionRequest(BaseModel):
    case_id: str
    text: str

class RelationshipExtractionResponse(BaseModel):
    case_id: str
    relationships: List[ExtractedRelationship]
