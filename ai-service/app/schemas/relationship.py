from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RelationshipStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANDIDATE = "CANDIDATE"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class Relationship(BaseModel):
    relationship_id: str = Field(..., description="Unique edge identifier")
    source_entity: str = Field(..., description="Source entity ID")
    target_entity: str = Field(..., description="Target entity ID")
    relation_type: str = Field(..., description="Relationship type (e.g., USES, ASSOCIATED_WITH)")
    status: RelationshipStatus = Field(..., description="Current validation status of the relationship")
    confidence: Optional[float] = Field(default=None, description="Validation score")
    evidence_ids: Optional[List[str]] = Field(default=None, description="Supporting documents")
