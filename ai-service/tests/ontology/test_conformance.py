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

def test_full_ontology_self_validation(registry):
    self_validator = OntologySelfValidator(registry)
    res = self_validator.run_full_audit()
    assert res.is_valid, f"Ontology contains structural errors: {res.reasons}"
