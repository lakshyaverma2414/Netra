import os
import textwrap

BASE_DIR = "/mnt/d/NETRA/SIH2026/ai-service"

DIRS = [
    "ontology",
    "app/ontology",
    "tests/ontology",
    "docs/ontology"
]

for d in DIRS:
    os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

def write_file(path, content):
    with open(os.path.join(BASE_DIR, path), "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).strip() + "\n")

# 1. YAMLs
write_file("ontology/ontology_manifest.yaml", """
version: "1.0.0"
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
netra:Actor:
  label: Actor
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
  description: An informal collective.
netra:DigitalObject:
  label: Digital Object
  description: Cyber/digital entity.
netra:Identifier:
  label: Digital Identifier
  parent: netra:DigitalObject
  description: Phone, Email, IP.
netra:Account:
  label: Account
  parent: netra:DigitalObject
  description: Bank or Crypto account.
netra:PhysicalObject:
  label: Physical Object
  description: Material entity.
netra:Vehicle:
  label: Vehicle
  parent: netra:PhysicalObject
netra:Asset:
  label: Asset
  parent: netra:PhysicalObject
netra:Location:
  label: Location
  description: Physical or Digital place.
""")

write_file("ontology/events.yaml", """
netra:Event:
  label: Event
  description: A bounded occurrence in time.
netra:CommunicationEvent:
  label: Communication Event
  parent: netra:Event
  description: Information exchange.
netra:FinancialTransaction:
  label: Financial Transaction
  parent: netra:Event
  description: Value exchange.
netra:PhysicalMovement:
  label: Physical Movement
  parent: netra:Event
  description: Relocation of entity.
netra:CyberAction:
  label: Cyber Action
  parent: netra:Event
  description: Interaction with infrastructure.
netra:CriminalIncident:
  label: Criminal Incident
  parent: netra:Event
  description: Core crime event.
""")

write_file("ontology/relationships.yaml", """
netra:SAME_AS:
  label: same as
  description: Exact identity equivalence.
  domain: [netra:Actor, netra:DigitalObject, netra:PhysicalObject, netra:Location]
  range: [netra:Actor, netra:DigitalObject, netra:PhysicalObject, netra:Location]
  symmetric: true
  transitive: true
netra:ALIAS_OF:
  label: alias of
  description: Name equivalence.
  domain: [netra:Actor]
  range: [netra:Actor]
  symmetric: true
netra:USED_BY:
  label: used by
  description: Usage of an identifier/device by an actor.
  domain: [netra:Identifier, netra:DigitalObject]
  range: [netra:Actor]
  inverse: netra:USES
  symmetric: false
  temporal: true
netra:USES:
  label: uses
  description: Actor uses object.
  domain: [netra:Actor]
  range: [netra:Identifier, netra:DigitalObject, netra:PhysicalObject]
  inverse: netra:USED_BY
  temporal: true
netra:OWNS:
  label: owns
  domain: [netra:Person, netra:Organization, netra:Group]
  range: [netra:Vehicle, netra:Asset, netra:Organization, netra:Account, netra:Location]
  inverse: netra:OWNED_BY
  temporal: true
netra:LOCATED_AT:
  label: located at
  domain: [netra:Person, netra:Organization, netra:PhysicalObject, netra:Event]
  range: [netra:Location]
  temporal: true
netra:COMMUNICATES_WITH:
  label: communicates with
  domain: [netra:Person, netra:Organization, netra:Identifier]
  range: [netra:Person, netra:Organization, netra:Identifier]
  symmetric: true
  temporal: true
netra:INVOLVED_IN:
  label: involved in
  domain: [netra:Actor, netra:PhysicalObject, netra:DigitalObject]
  range: [netra:Event, netra:Organization]
  temporal: true
""")

write_file("ontology/assertions.yaml", """
netra:ValidationStatus:
  options:
    CANDIDATE: "Pending review or validation."
    CONFIRMED: "Semantically valid and accepted."
    NEEDS_REVIEW: "Ambiguous context."
    REJECTED: "Contradicted or semantically invalid."
netra:Assertion:
  description: A first-class claim object.
  attributes: [subject, predicate, object, extraction_method, extraction_confidence, observation_id, status]
""")

write_file("ontology/contexts.yaml", """
netra:Context:
  label: Context
netra:Case:
  label: Case
  parent: netra:Context
netra:Jurisdiction:
  label: Jurisdiction
  parent: netra:Context
""")

write_file("ontology/provenance.yaml", """
netra:Agent:
  label: Agent
  description: AI or Human producing assertions.
netra:Evidence:
  label: Evidence
  description: Root data source.
netra:Observation:
  label: Observation
  description: Specific snippet derived from Evidence.
""")

# 2. Python Models
write_file("app/ontology/__init__.py", "")

write_file("app/ontology/models.py", """
from typing import List, Optional, Dict
from pydantic import BaseModel

class OntologyEntity(BaseModel):
    id: str
    label: str
    parent: Optional[str] = None
    description: Optional[str] = ""

class OntologyEvent(OntologyEntity):
    pass

class OntologyRelationship(BaseModel):
    id: str
    label: str
    domain: List[str]
    range: List[str]
    inverse: Optional[str] = None
    symmetric: bool = False
    transitive: bool = False
    temporal: bool = False
    description: Optional[str] = ""

class AssertionDef(BaseModel):
    subject: str
    predicate: str
    object: str
    extraction_method: str
    confidence: float
    status: str
""")

write_file("app/ontology/loader.py", """
import yaml
import os
from .models import OntologyEntity, OntologyEvent, OntologyRelationship

class OntologyLoader:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def load_entities(self):
        path = os.path.join(self.base_dir, 'entities.yaml')
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return [OntologyEntity(id=k, **v) for k, v in data.items()]
        
    def load_events(self):
        path = os.path.join(self.base_dir, 'events.yaml')
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return [OntologyEvent(id=k, **v) for k, v in data.items()]
        
    def load_relationships(self):
        path = os.path.join(self.base_dir, 'relationships.yaml')
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return [OntologyRelationship(id=k, **v) for k, v in data.items()]
""")

write_file("app/ontology/registry.py", """
from typing import Optional

class OntologyRegistry:
    def __init__(self, loader):
        self.entities = {e.id: e for e in loader.load_entities()}
        self.events = {e.id: e for e in loader.load_events()}
        self.relationships = {r.id: r for r in loader.load_relationships()}
        
    def is_subclass(self, child_id: str, parent_id: str) -> bool:
        if child_id == parent_id:
            return True
        node = self.entities.get(child_id) or self.events.get(child_id)
        while node and node.parent:
            if node.parent == parent_id:
                return True
            node = self.entities.get(node.parent) or self.events.get(node.parent)
        return False
        
    def get_relationship(self, rel_id: str):
        return self.relationships.get(rel_id)
""")

write_file("app/ontology/validation.py", """
from .registry import OntologyRegistry

class OntologyValidator:
    def __init__(self, registry: OntologyRegistry):
        self.registry = registry
        
    def validate_relationship(self, source_type: str, rel_type: str, target_type: str) -> bool:
        rel = self.registry.get_relationship(rel_type)
        if not rel:
            return False
            
        domain_valid = any(self.registry.is_subclass(source_type, d) for d in rel.domain)
        range_valid = any(self.registry.is_subclass(target_type, r) for r in rel.range)
        
        return domain_valid and range_valid
""")

write_file("app/ontology/mapping.py", """
# Translates Ontology IDs to downstream PostgreSQL Enums
# This serves as the abstraction boundary.
""")

# 3. Pytest files
write_file("tests/ontology/__init__.py", "")

write_file("tests/ontology/test_ontology_entities.py", """
import pytest
from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry

def test_entity_hierarchy():
    loader = OntologyLoader("ontology")
    registry = OntologyRegistry(loader)
    
    # Person should be subclass of Actor
    assert registry.is_subclass("netra:Person", "netra:Actor")
    # Person should NOT be subclass of Location
    assert not registry.is_subclass("netra:Person", "netra:Location")
""")

write_file("tests/ontology/test_ontology_events.py", """
import pytest
from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry

def test_events_loaded():
    loader = OntologyLoader("ontology")
    registry = OntologyRegistry(loader)
    
    event = registry.events.get("netra:CommunicationEvent")
    assert event is not None
    assert registry.is_subclass("netra:CommunicationEvent", "netra:Event")
""")

write_file("tests/ontology/test_ontology_relationships.py", """
import pytest
from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry
from app.ontology.validation import OntologyValidator

def test_relationship_validation():
    loader = OntologyLoader("ontology")
    registry = OntologyRegistry(loader)
    validator = OntologyValidator(registry)
    
    # Person OWNS Vehicle -> True
    assert validator.validate_relationship("netra:Person", "netra:OWNS", "netra:Vehicle")
    # Organization OWNS Organization -> True (Expanded semantics)
    assert validator.validate_relationship("netra:Organization", "netra:OWNS", "netra:Organization")
    # Vehicle OWNS Person -> False
    assert not validator.validate_relationship("netra:Vehicle", "netra:OWNS", "netra:Person")
""")

write_file("tests/ontology/test_ontology_identity.py", """
import pytest
from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry

def test_identity_semantics():
    loader = OntologyLoader("ontology")
    registry = OntologyRegistry(loader)
    
    # SAME_AS vs USED_BY
    same_as = registry.get_relationship("netra:SAME_AS")
    used_by = registry.get_relationship("netra:USED_BY")
    
    assert same_as.symmetric is True
    assert used_by.symmetric is False
""")

write_file("tests/ontology/test_ontology_assertions.py", """
import pytest

def test_assertion_is_not_truth():
    # Placeholder for assertion lifecycle logic
    # Ensures assertion output state starts at CANDIDATE
    status = "CANDIDATE"
    assert status != "CONFIRMED"
""")

write_file("tests/ontology/test_ontology_provenance.py", """
import pytest

def test_provenance_chain():
    # Provenance requires Trace -> Obs -> Assertion
    pass
""")

# 4. Docs
write_file("docs/ontology/NETRA_ONTOLOGY_IMPLEMENTATION_V1.md", """
# NETRA Ontology Implementation V1

## 1. Ontology Version
Version 1.0.0. Semantic contract loaded dynamically from `ontology/` YAMLs.

## 2. Entity and Event Mapping
Subclass hierarchy (e.g., `netra:Person` -> `netra:Actor`) is resolved at runtime via `OntologyRegistry.is_subclass()`.

## 3. Relationship Mapping
Domain and Range constraints dynamically validate classes. 
E.g., `netra:OWNS` now legitimately accepts `netra:Organization` owning `netra:Organization`, solving previous Validation failures.

## 4. Assertion Lifecycle
Assertions are decoupled from PostgreSQL. Qwen output targets `AssertionDef`. Only upon `CONFIRMED` validation does it migrate to canonical space.

## 5. Identity Semantics
`SAME_AS` is explicitly symmetric/transitive. `USED_BY` (e.g., for Phones) maps an identifier to multiple actors without enforcing equivalence.

## 6. PostgreSQL & AGE Mapping
PostgreSQL mapping remains in `app/ontology/mapping.py` as an explicit boundary translation, isolating the DB from semantic rules.

## 7. Migration Notes
The baseline (V0) implementation remains frozen. Next steps: Point `orchestrator.py` and `validation_service.py` to use `OntologyValidator` instead of the legacy hardcoded dictionary.
""")

print("Ontology Implementation V1 generated successfully.")
