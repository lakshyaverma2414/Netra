import pytest
from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry
from app.ontology.validation import OntologyValidator, OntologySelfValidator

@pytest.fixture
def registry():
    loader = OntologyLoader("ai-service/ontology")
    return OntologyRegistry(loader)

@pytest.fixture
def validator(registry):
    return OntologyValidator(registry)

def test_entity_hierarchy_resolution(registry):
    assert registry.is_subclass("netra:Person", "netra:Actor")
    assert registry.is_subclass("netra:Person", "netra:Entity")
    assert registry.is_subclass("netra:Vehicle", "netra:PhysicalObject")
    assert not registry.is_subclass("netra:Person", "netra:DigitalObject")

def test_missing_entities_are_handled(registry):
    assert registry.get_node("netra:NonExistent") is None
