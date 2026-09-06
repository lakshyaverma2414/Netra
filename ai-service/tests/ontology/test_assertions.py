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

def test_assertion_model_requirements(registry):
    assrt = registry.assertions["netra:Assertion"]
    req = assrt.required_fields
    assert "subject_id" in req
    assert "extraction_agent" in req
    assert "status" in req

def test_assertion_status_lifecycle(registry):
    status = registry.assertions["netra:AssertionStatus"]
    assert "CANDIDATE" in status.options
    assert "CONFIRMED" in status.options
