from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum
import uuid

class RelationshipType(str, Enum):
    USES = "USES"
    OWNS = "OWNS"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    LOCATED_AT = "LOCATED_AT"
    LINKED_TO = "LINKED_TO"
    INVOLVED_IN = "INVOLVED_IN"

class RelationshipCandidate(BaseModel):
    relationship_id: str = Field(default_factory=lambda: f"REL-{uuid.uuid4().hex[:8]}")
    source_entity_id: str = Field(..., description="Canonical ID of the source entity")
    relationship_type: RelationshipType = Field(..., description="Ontology relationship type")
    target_entity_id: str = Field(..., description="Canonical ID of the target entity")
    
    source_record_id: str = Field(..., description="Record ID containing the relationship")
    evidence_id: Optional[str] = Field(None, description="Optional specific evidence reference")
    extraction_method: str = Field(..., description="E.g., STRUCTURED_RULE, TEXT_RULE")
    evidence_text: Optional[str] = Field(None, description="Text snippet justifying the relationship")
    
    negated: bool = Field(default=False, description="True if the relationship is explicitly denied")
    
    temporal_context: Optional[Dict[str, str]] = Field(None, description="Time context, e.g. {'date': '2026-08-12'}")
    location_context: Optional[str] = Field(None, description="Location context of the relationship")
    
    status: str = Field(default="CANDIDATE", description="Must start as CANDIDATE")
