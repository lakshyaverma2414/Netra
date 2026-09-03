from pydantic import BaseModel, Field
from typing import List, Optional

class Entity(BaseModel):
    entity_id: str = Field(..., description="Unique system identifier")
    entity_type: str = Field(..., description="Type of the entity (e.g., PERSON, PHONE)")
    canonical_name: str = Field(..., description="Resolved canonical label")
    confidence: float = Field(..., description="Resolution probability score")
    aliases: Optional[List[str]] = Field(default=None, description="Known alternate names")
    source_references: Optional[List[str]] = Field(default=None, description="Evidence or document IDs")
