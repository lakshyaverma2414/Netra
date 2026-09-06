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

def test_same_as_properties(registry):
    rel = registry.relationships["netra:SAME_AS"]
    assert rel.symmetric is True
    assert rel.transitive is True

def test_used_by_not_identity(registry):
    rel = registry.relationships["netra:USED_BY"]
    assert rel.symmetric is False
    assert rel.transitive is False
    assert "netra:Actor" in rel.range
    assert "netra:Identifier" in rel.domain
