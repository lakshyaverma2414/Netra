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

def test_context_case_hierarchy(registry):
    assert registry.is_subclass("netra:Case", "netra:Context")
    assert registry.is_subclass("netra:Jurisdiction", "netra:Context")
