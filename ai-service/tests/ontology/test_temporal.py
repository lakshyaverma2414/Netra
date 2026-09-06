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

def test_temporal_relationship_flags(registry):
    owns = registry.relationships["netra:OWNS"]
    same_as = registry.relationships["netra:SAME_AS"]

    assert owns.temporal is True
    assert same_as.temporal is False  # Identity is generally timeless in this abstraction
