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

def test_located_at_vs_occurred_at(validator):
    # Person -> LOCATED_AT -> Location (Valid)
    assert validator.validate_direct_relationship("netra:Person", "netra:LOCATED_AT", "netra:Location").is_valid
    # Event -> LOCATED_AT -> Location (Valid for generic backward compatibility, but OCCURRED_AT is preferred)
    assert validator.validate_direct_relationship("netra:Event", "netra:OCCURRED_AT", "netra:Location").is_valid
    # Person -> OCCURRED_AT -> Location (Invalid)
    assert not validator.validate_direct_relationship("netra:Person", "netra:OCCURRED_AT", "netra:Location").is_valid

def test_owns_domain_range(validator):
    # Person OWNS Property
    assert validator.validate_direct_relationship("netra:Person", "netra:OWNS", "netra:Property").is_valid
    # Organization OWNS Vehicle
    assert validator.validate_direct_relationship("netra:Organization", "netra:OWNS", "netra:Vehicle").is_valid
    # Person OWNS Location (Invalid)
    assert not validator.validate_direct_relationship("netra:Person", "netra:OWNS", "netra:Location").is_valid
