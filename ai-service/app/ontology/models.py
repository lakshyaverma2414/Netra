from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class OntologyNode(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    parent: Optional[str] = None
    version: Optional[str] = "1.0"
    deprecated: bool = False

class OntologyEntity(OntologyNode):
    pass

class RoleDef(BaseModel):
    allowed_types: List[str]
    required: bool = True
    cardinality: str = "1..*"

class OntologyEvent(OntologyNode):
    roles: Dict[str, RoleDef] = Field(default_factory=dict)

class OntologyRelationship(OntologyNode):
    domain: List[str] = Field(default_factory=list)
    range: List[str] = Field(default_factory=list)
    inverse: Optional[str] = None
    symmetric: bool = False
    transitive: bool = False
    temporal: bool = False
    direct: bool = True

class OntologyContext(OntologyNode):
    pass

class OntologyProvenance(OntologyNode):
    pass

class OntologyAssertionDef(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    required_fields: List[str] = Field(default_factory=list)
    options: Dict[str, str] = Field(default_factory=dict)

class ValidationResult(BaseModel):
    is_valid: bool
    reasons: List[str] = Field(default_factory=list)
