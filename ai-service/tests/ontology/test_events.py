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

def test_event_role_loading(registry):
    event = registry.events.get("netra:CommunicationEvent")
    assert event is not None
    assert "sender" in event.roles
    assert event.roles["sender"].required is True
    assert event.roles["infrastructure"].required is False

def test_event_role_validation_logic(validator):
    # Sender can be Person
    res = validator.validate_event_role("netra:CommunicationEvent", "sender", "netra:Person")
    assert res.is_valid
    # Sender cannot be Vehicle
    res = validator.validate_event_role("netra:CommunicationEvent", "sender", "netra:Vehicle")
    assert not res.is_valid
