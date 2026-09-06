from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class LLMRelationship(BaseModel):
    source_text: str = Field(..., description="Text span of the source entity")
    source_type: str = Field(..., description="Entity type of the source (e.g. PERSON, PHONE, VEHICLE)")
    relationship_type: str = Field(..., description="Semantic relationship type extracted by the LLM")
    target_text: str = Field(..., description="Text span of the target entity")
    target_type: str = Field(..., description="Entity type of the target (e.g. PERSON, PHONE, VEHICLE)")
    evidence_text: str = Field(..., description="The exact sentence/span from text proving this")
    negated: bool = Field(default=False, description="True if explicitly denied")
    temporal_context: Optional[Dict[str, str]] = Field(None, description="Time context, e.g. {'date': '2026-08-12'}")
    location_context: Optional[str] = Field(None, description="Location context of the relationship")


class LLMRelationshipResponse(BaseModel):
    relationships: List[LLMRelationship]
