import os
import textwrap

BASE_DIR = "/mnt/d/NETRA/SIH2026/ai-service"

def write_file(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).strip() + "\n")

# ---------------------------------------------------------
# 1. YAML Definitions
# ---------------------------------------------------------

write_file("ontology/ontology_manifest.yaml", """
version: "1.1.0"
name: "NETRA Generic Investigative Ontology"
description: "Semantic contract for heterogeneous criminal investigations."
modules:
  - entities.yaml
  - events.yaml
  - relationships.yaml
  - assertions.yaml
  - contexts.yaml
  - provenance.yaml
""")

write_file("ontology/entities.yaml", """
netra:Entity:
  label: Entity
  description: Base domain object.
  version: "1.0"
netra:Actor:
  label: Actor
  parent: netra:Entity
  description: An entity capable of action.
netra:Person:
  label: Person
  parent: netra:Actor
  description: A human being.
netra:Organization:
  label: Organization
  parent: netra:Actor
  description: A formal group or agency.
netra:Group:
  label: Group
  parent: netra:Actor
  description: An informal collective or syndicate.
netra:DigitalObject:
  label: Digital Object
  parent: netra:Entity
  description: Cyber/digital entity.
netra:Identifier:
  label: Digital Identifier
  parent: netra:DigitalObject
  description: Phone, Email, IP, MAC.
netra:DigitalIdentity:
  label: Digital Identity
  parent: netra:DigitalObject
  description: Persona or username.
netra:Account:
  label: Account
  parent: netra:DigitalObject
  description: Bank, Crypto, or Social Media account.
netra:Device:
  label: Device
  parent: netra:DigitalObject
  description: Mobile, Computer, IoT.
netra:PhysicalObject:
  label: Physical Object
  parent: netra:Entity
  description: Material entity.
netra:Vehicle:
  label: Vehicle
  parent: netra:PhysicalObject
netra:Weapon:
  label: Weapon
  parent: netra:PhysicalObject
netra:Document:
  label: Document
  parent: netra:PhysicalObject
netra:Asset:
  label: Asset
  parent: netra:PhysicalObject
  description: Real estate, valuables.
netra:Location:
  label: Location
  parent: netra:Entity
  description: Physical or Digital place.
""")

write_file("ontology/events.yaml", """
netra:Event:
  label: Event
  description: A bounded occurrence in time.
  version: "1.0"
netra:CommunicationEvent:
  label: Communication Event
  parent: netra:Event
  description: Exchange of information between entities.
  roles:
    sender: [netra:Actor, netra:Identifier]
    receiver: [netra:Actor, netra:Identifier]
    infrastructure: [netra:Device, netra:Identifier]
netra:FinancialTransaction:
  label: Financial Transaction
  parent: netra:Event
  description: Movement of financial value.
  roles:
    originator: [netra:Actor, netra:Account]
    beneficiary: [netra:Actor, netra:Account]
    facilitator: [netra:Organization]
netra:PhysicalMovement:
  label: Physical Movement
  parent: netra:Event
  description: Relocation of an entity.
  roles:
    mover: [netra:Actor, netra:PhysicalObject]
    origin: [netra:Location]
    destination: [netra:Location]
netra:CyberAction:
  label: Cyber Action
  parent: netra:Event
  description: Interaction with infrastructure.
  roles:
    actor: [netra:Actor, netra:DigitalIdentity]
    target: [netra:DigitalObject]
    vector: [netra:DigitalObject]
netra:CriminalIncident:
  label: Criminal Incident
  parent: netra:Event
  description: The core crime event.
  roles:
    perpetrator: [netra:Actor]
    victim: [netra:Actor, netra:Organization]
    target_object: [netra:Entity]
    location: [netra:Location]
""")

write_file("ontology/relationships.yaml", """
# Direct Relationships vs Event-Mediated is handled by context. 
# Event-Mediated rely on Events and Roles. Direct rely on these definitions.
netra:SAME_AS:
  label: same as
  description: Exact real-world identity equivalence. Not for shared identifiers.
  domain: [netra:Entity]
  range: [netra:Entity]
  symmetric: true
  transitive: true
  direct: true
netra:POSSIBLY_SAME_AS:
  label: possibly same as
  description: Algorithmic candidate for identity equivalence.
  domain: [netra:Entity]
  range: [netra:Entity]
  symmetric: true
  direct: true
netra:ALIAS_OF:
  label: alias of
  description: Nomenclature equivalence (A is known as B).
  domain: [netra:Actor, netra:DigitalIdentity]
  range: [netra:Actor, netra:DigitalIdentity]
  symmetric: true
  direct: true
netra:USED_BY:
  label: used by
  description: Usage of an identifier/device by an actor. Does not imply ownership or identity equivalence.
  domain: [netra:Identifier, netra:Device]
  range: [netra:Actor]
  inverse: netra:USES
  symmetric: false
  temporal: true
  direct: true
netra:USES:
  label: uses
  domain: [netra:Actor]
  range: [netra:Identifier, netra:Device]
  inverse: netra:USED_BY
  temporal: true
  direct: true
netra:OWNS:
  label: owns
  description: Legal or de-facto property rights over an object.
  domain: [netra:Person, netra:Organization, netra:Group]
  range: [netra:PhysicalObject, netra:DigitalObject, netra:Organization, netra:Location]
  inverse: netra:OWNED_BY
  temporal: true
  direct: true
netra:LOCATED_AT:
  label: located at
  description: Physical or spatial presence.
  domain: [netra:Person, netra:Organization, netra:PhysicalObject, netra:Event]
  range: [netra:Location]
  temporal: true
  direct: true
netra:COMMUNICATES_WITH:
  label: communicates with
  description: Static representation of a communication line. (Prefer CommunicationEvent for specific instances).
  domain: [netra:Person, netra:Organization, netra:Group, netra:Identifier]
  range: [netra:Person, netra:Organization, netra:Group, netra:Identifier]
  symmetric: true
  temporal: true
  direct: true
netra:INVOLVED_IN:
  label: involved in
  description: Generic participation. (Prefer strict roles if Event is known).
  domain: [netra:Entity]
  range: [netra:Event, netra:Organization, netra:Group]
  temporal: true
  direct: true
""")

write_file("ontology/assertions.yaml", """
netra:AssertionStatus:
  options:
    CANDIDATE: "Extracted, pending semantic and evidence validation."
    NEEDS_REVIEW: "Semantically valid but ambiguous or lacks sufficient evidence."
    CONFIRMED: "Semantically valid and fully supported by provenance."
    REJECTED: "Contradicted, disproven, or semantically invalid."
netra:Assertion:
  label: Assertion
  description: A first-class claim object combining semantics with provenance.
  required_fields:
    - subject_id
    - predicate_id
    - object_id
    - extraction_agent
    - extraction_confidence
    - observation_id
    - status
""")

write_file("ontology/contexts.yaml", """
netra:Context:
  label: Context
  description: Boundary or scope of a set of facts.
netra:Case:
  label: Case
  parent: netra:Context
  description: An investigative boundary (e.g., an FIR or Operation).
netra:Jurisdiction:
  label: Jurisdiction
  parent: netra:Context
  description: Legal or geographic authority boundary.
netra:SourceSystem:
  label: Source System
  parent: netra:Context
  description: The origin system providing the data.
""")

write_file("ontology/provenance.yaml", """
netra:ProvenanceRecord:
  label: Provenance Record
  description: Base class for tracing data origins.
netra:SourceRecord:
  label: Source Record
  parent: netra:ProvenanceRecord
  description: The root physical or digital artifact (e.g., FIR Document, HDD).
netra:DerivedArtifact:
  label: Derived Artifact
  parent: netra:ProvenanceRecord
  description: Processed artifact (e.g., OCR text, Forensic Image).
netra:Observation:
  label: Observation
  parent: netra:ProvenanceRecord
  description: The exact snippet, region, or data point extracted.
netra:ProcessingRun:
  label: Processing Run
  parent: netra:ProvenanceRecord
  description: A scheduled job or analysis execution.
netra:Agent:
  label: Agent
  parent: netra:ProvenanceRecord
  description: Human analyst or AI model (e.g., Qwen-72B, Analyst John).
netra:Activity:
  label: Activity
  parent: netra:ProvenanceRecord
  description: The action performed to generate the assertion (e.g., LLM Inference, Manual Entry).
netra:ChainOfCustody:
  label: Chain of Custody
  parent: netra:ProvenanceRecord
  description: Sequential trace of handling.
""")


# ---------------------------------------------------------
# 2. Python Models, Loader, Registry, Validator
# ---------------------------------------------------------

write_file("app/ontology/models.py", """
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class OntologyNode(BaseModel):
    id: str
    label: str
    description: Optional[str] = ""
    parent: Optional[str] = None
    version: Optional[str] = "1.0"
    deprecated: bool = False

class OntologyEntity(OntologyNode):
    pass

class OntologyEvent(OntologyNode):
    roles: Dict[str, List[str]] = Field(default_factory=dict)

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
    description: Optional[str] = ""
    required_fields: List[str] = Field(default_factory=list)
    options: Dict[str, str] = Field(default_factory=dict)

class ValidationResult(BaseModel):
    is_valid: bool
    reasons: List[str] = Field(default_factory=list)
""")

write_file("app/ontology/loader.py", """
import yaml
import os
from .models import (
    OntologyEntity, OntologyEvent, OntologyRelationship, 
    OntologyContext, OntologyProvenance, OntologyAssertionDef
)

class OntologyLoader:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.manifest = self._load_yaml('ontology_manifest.yaml')

    def _load_yaml(self, filename: str) -> dict:
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def load_entities(self):
        data = self._load_yaml('entities.yaml')
        return [OntologyEntity(id=k, **v) for k, v in data.items()]
        
    def load_events(self):
        data = self._load_yaml('events.yaml')
        return [OntologyEvent(id=k, **v) for k, v in data.items()]
        
    def load_relationships(self):
        data = self._load_yaml('relationships.yaml')
        return [OntologyRelationship(id=k, **v) for k, v in data.items()]

    def load_contexts(self):
        data = self._load_yaml('contexts.yaml')
        return [OntologyContext(id=k, **v) for k, v in data.items()]

    def load_provenance(self):
        data = self._load_yaml('provenance.yaml')
        return [OntologyProvenance(id=k, **v) for k, v in data.items()]
        
    def load_assertions(self):
        data = self._load_yaml('assertions.yaml')
        return [OntologyAssertionDef(id=k, **v) for k, v in data.items()]
""")

write_file("app/ontology/registry.py", """
from typing import Optional, Dict
from .models import OntologyNode

class OntologyRegistry:
    def __init__(self, loader):
        self.version = loader.manifest.get("version", "1.0.0")
        self.entities = {e.id: e for e in loader.load_entities()}
        self.events = {e.id: e for e in loader.load_events()}
        self.relationships = {r.id: r for r in loader.load_relationships()}
        self.contexts = {c.id: c for c in loader.load_contexts()}
        self.provenance = {p.id: p for p in loader.load_provenance()}
        self.assertions = {a.id: a for a in loader.load_assertions()}
        
    def get_node(self, node_id: str) -> Optional[OntologyNode]:
        for space in (self.entities, self.events, self.relationships, self.contexts, self.provenance):
            if node_id in space:
                return space[node_id]
        return None

    def is_subclass(self, child_id: str, parent_id: str) -> bool:
        if child_id == parent_id:
            return True
        node = self.get_node(child_id)
        while node and node.parent:
            if node.parent == parent_id:
                return True
            node = self.get_node(node.parent)
        return False
""")

write_file("app/ontology/validation.py", """
from .registry import OntologyRegistry
from .models import ValidationResult

class OntologyValidator:
    def __init__(self, registry: OntologyRegistry):
        self.registry = registry
        
    def validate_direct_relationship(self, source_type: str, rel_type: str, target_type: str) -> ValidationResult:
        rel = self.registry.relationships.get(rel_type)
        if not rel:
            return ValidationResult(is_valid=False, reasons=[f"Relationship '{rel_type}' is not defined in ontology."])
        
        if not rel.direct:
            return ValidationResult(is_valid=False, reasons=[f"Relationship '{rel_type}' is not a direct relationship. It must be event-mediated."])
            
        domain_valid = any(self.registry.is_subclass(source_type, d) for d in rel.domain)
        if not domain_valid:
            return ValidationResult(is_valid=False, reasons=[f"Source type '{source_type}' is not a valid domain for '{rel_type}'. Allowed: {rel.domain}"])

        range_valid = any(self.registry.is_subclass(target_type, r) for r in rel.range)
        if not range_valid:
            return ValidationResult(is_valid=False, reasons=[f"Target type '{target_type}' is not a valid range for '{rel_type}'. Allowed: {rel.range}"])
            
        return ValidationResult(is_valid=True, reasons=[])

    def validate_event_role(self, event_type: str, role_name: str, entity_type: str) -> ValidationResult:
        event = self.registry.events.get(event_type)
        if not event:
            return ValidationResult(is_valid=False, reasons=[f"Event '{event_type}' is not defined."])
            
        if role_name not in event.roles:
            return ValidationResult(is_valid=False, reasons=[f"Role '{role_name}' is not defined for event '{event_type}'."])
            
        allowed_types = event.roles[role_name]
        role_valid = any(self.registry.is_subclass(entity_type, t) for t in allowed_types)
        if not role_valid:
            return ValidationResult(is_valid=False, reasons=[f"Entity type '{entity_type}' cannot play role '{role_name}' in '{event_type}'. Allowed: {allowed_types}"])
            
        return ValidationResult(is_valid=True, reasons=[])
""")

# ---------------------------------------------------------
# 3. Tests
# ---------------------------------------------------------

write_file("tests/ontology/test_ontology_core.py", """
import pytest
from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry
from app.ontology.validation import OntologyValidator

@pytest.fixture
def registry():
    loader = OntologyLoader("ontology")
    return OntologyRegistry(loader)

@pytest.fixture
def validator(registry):
    return OntologyValidator(registry)

def test_manifest_and_all_modules_loaded(registry):
    assert registry.version == "1.1.0"
    assert len(registry.entities) > 5
    assert len(registry.events) > 3
    assert len(registry.relationships) > 5
    assert "netra:SourceRecord" in registry.provenance
    assert "netra:Case" in registry.contexts
    assert "netra:Assertion" in registry.assertions

def test_entity_subclassing(registry):
    # Person -> Actor -> Entity
    assert registry.is_subclass("netra:Person", "netra:Actor")
    assert registry.is_subclass("netra:Person", "netra:Entity")
    assert not registry.is_subclass("netra:Person", "netra:DigitalObject")
    
def test_direct_relationship_validation(validator):
    # Valid: Organization OWNS Vehicle
    res = validator.validate_direct_relationship("netra:Organization", "netra:OWNS", "netra:Vehicle")
    assert res.is_valid
    
    # Valid: Identifier USED_BY Person
    res = validator.validate_direct_relationship("netra:Identifier", "netra:USED_BY", "netra:Person")
    assert res.is_valid
    
    # Invalid: Vehicle COMMUNICATES_WITH Person
    res = validator.validate_direct_relationship("netra:Vehicle", "netra:COMMUNICATES_WITH", "netra:Person")
    assert not res.is_valid
    assert "Source type 'netra:Vehicle' is not a valid domain" in res.reasons[0]

def test_event_role_validation(validator):
    # Valid: Person is sender in CommunicationEvent
    res = validator.validate_event_role("netra:CommunicationEvent", "sender", "netra:Person")
    assert res.is_valid
    
    # Invalid: Vehicle is sender in CommunicationEvent
    res = validator.validate_event_role("netra:CommunicationEvent", "sender", "netra:Vehicle")
    assert not res.is_valid
    assert "cannot play role" in res.reasons[0]
    
    # Invalid: Non-existent role
    res = validator.validate_event_role("netra:CommunicationEvent", "driver", "netra:Person")
    assert not res.is_valid

def test_identity_vs_usage_semantics(registry):
    same_as = registry.relationships["netra:SAME_AS"]
    used_by = registry.relationships["netra:USED_BY"]
    
    assert same_as.symmetric is True
    assert used_by.symmetric is False
    assert "netra:Actor" in used_by.range
    assert "netra:Identifier" in used_by.domain
""")

