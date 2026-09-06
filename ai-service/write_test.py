import os
content = """
import pytest
from unittest.mock import MagicMock
from app.db.models import Entity, ResolutionStatus, RelationshipAssertion
from app.schemas.validation import ValidationRequest, ValidationStatusEnum
from app.services.validation_service import validate_relationship
import enum

class DummyEnum(enum.Enum):
    PERSON = 'PERSON'
    PHONE = 'PHONE'
    BANK_ACCOUNT = 'BANK_ACCOUNT'
    LOCATION = 'LOCATION'

@pytest.fixture
def db_mock():
    mock = MagicMock()
    
    class GlobalEntityCounter:
        def __init__(self):
            self.cc = 0
            
    # Default counter for normal tests
    counter = GlobalEntityCounter()
    
    def qse(model):
        qm = MagicMock()
        def first_side_effect():
            if model != Entity:
                return None
            counter.cc += 1
            if counter.cc == 1:
                ent = MagicMock()
                ent.entity_type = DummyEnum.PERSON
                ent.resolution_status = ResolutionStatus.CONFIRMED
                return ent
            elif counter.cc == 2:
                ent = MagicMock()
                ent.entity_type = getattr(counter, "target_type", DummyEnum.PHONE)
                ent.resolution_status = ResolutionStatus.CONFIRMED
                return ent
            return None
            
        qm.filter.return_value.first.side_effect = first_side_effect
        qm.filter_by.return_value.first.side_effect = first_side_effect
        return qm
        
    mock.query.side_effect = qse
    mock.counter = counter
    return mock

def test_legacy_validation_pass(db_mock, monkeypatch):
    monkeypatch.setenv("NETRA_ONTOLOGY_V1_ENABLED", "false")
    req = ValidationRequest(
        source_entity_id="E1", target_entity_id="E2", relationship_type="COMMUNICATES_WITH",
        source_record_id="REC1", extracted_text="test", extraction_method="QWEN", case_id="C1"
    )
    res = validate_relationship(db_mock, req)
    assert res.status == ValidationStatusEnum.REJECTED
    assert "INVALID_ENTITY_TYPE_PAIR" in res.reasons

def test_v1_validation_pass_direct(db_mock, monkeypatch):
    monkeypatch.setenv("NETRA_ONTOLOGY_V1_ENABLED", "true")
    req = ValidationRequest(
        source_entity_id="E1", target_entity_id="E2", relationship_type="COMMUNICATES_WITH",
        source_record_id="REC1", extracted_text="test", extraction_method="QWEN", case_id="C1"
    )
    res = validate_relationship(db_mock, req)
    assert res.status == ValidationStatusEnum.CONFIRMED

def test_v1_validation_event_role(db_mock, monkeypatch):
    monkeypatch.setenv("NETRA_ONTOLOGY_V1_ENABLED", "true")
    db_mock.counter.target_type = DummyEnum.BANK_ACCOUNT
    
    req = ValidationRequest(
        source_entity_id="E1", target_entity_id="E3", relationship_type="TRANSFERRED_TO",
        source_record_id="REC1", extracted_text="test", extraction_method="QWEN", case_id="C1"
    )
    res = validate_relationship(db_mock, req)
    assert res.status == ValidationStatusEnum.CONFIRMED

def test_assertion_is_recorded(db_mock, monkeypatch):
    monkeypatch.setenv("NETRA_ONTOLOGY_V1_ENABLED", "true")
    db_mock.counter.target_type = DummyEnum.LOCATION
    
    req = ValidationRequest(
        source_entity_id="E1", target_entity_id="E2", relationship_type="OWNS",
        source_record_id="REC1", extracted_text="invalid rel", extraction_method="QWEN", case_id="C1"
    )
    res = validate_relationship(db_mock, req)
    assert res.status == ValidationStatusEnum.REJECTED
    
    assertions_added = [call[0][0] for call in db_mock.add.call_args_list if isinstance(call[0][0], RelationshipAssertion)]
    assert len(assertions_added) > 0
    assert assertions_added[-1].status == "REJECTED"
"""
with open("/mnt/d/NETRA/SIH2026/ai-service/tests/ontology/test_runtime_integration.py", "w", encoding="utf-8") as f:
    f.write(content)
