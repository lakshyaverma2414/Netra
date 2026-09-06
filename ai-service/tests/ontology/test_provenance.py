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

def test_provenance_chain_exists(registry):
    assert registry.get_node("netra:SourceRecord") is not None
    assert registry.get_node("netra:DerivedArtifact") is not None
    assert registry.get_node("netra:Observation") is not None
    assert registry.is_subclass("netra:SourceRecord", "netra:ProvenanceRecord")
