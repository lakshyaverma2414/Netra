import pytest
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Entity, Relationship, RelationshipAssertion, ResolutionStatus, ValidationStatus
from app.schemas.validation import ValidationRequest, ValidationStatusEnum
from app.services.validation_service import validate_relationship

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(autouse=True)
def clean_db(db):
    yield
    from sqlalchemy import text
    db.execute(text("DELETE FROM relationship_assertion_links WHERE assertion_id IN (SELECT assertion_id FROM relationship_assertions WHERE source_record_id IN ('SR-101', 'SR-102', 'SR-103', 'SR-104', 'SR-201', ''))"))
    db.execute(text("DELETE FROM relationship_cases WHERE relationship_id IN (SELECT relationship_id FROM relationships WHERE relationship_id LIKE 'TEST-R-%')"))
    db.execute(text("DELETE FROM relationship_assertions WHERE source_record_id IN ('SR-101', 'SR-102', 'SR-103', 'SR-104', 'SR-201', '')"))
    db.execute(text("DELETE FROM relationships WHERE relationship_id LIKE 'TEST-R-%'"))
    db.commit()

def test_valid_relationship_confirmed(db):
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-002",
        relationship_type="TRANSFERRED_TO",
        target_entity_id="UPI-001",
        source_record_id="SR-101",
        extracted_text="V. Singh transferred to ghost@bank"
    )
    res = validate_relationship(db, req)
    assert res.status == ValidationStatusEnum.CONFIRMED
    assert "VALID_ENTITY_TYPE_PAIR" in res.reasons
    
def test_source_entity_missing(db):
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-999",
        relationship_type="TRANSFERRED_TO",
        target_entity_id="UPI-001",
        source_record_id="SR-101"
    )
    res = validate_relationship(db, req)
    assert res.status == ValidationStatusEnum.REJECTED
    assert "SOURCE_ENTITY_NOT_FOUND" in res.reasons

def test_target_entity_missing(db):
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-002",
        relationship_type="TRANSFERRED_TO",
        target_entity_id="UPI-999",
        source_record_id="SR-101"
    )
    res = validate_relationship(db, req)
    assert res.status == ValidationStatusEnum.REJECTED
    assert "TARGET_ENTITY_NOT_FOUND" in res.reasons

def test_unresolved_entities_blocked(db):
    # Temporarily make P-002 unresolved
    ent = db.query(Entity).filter(Entity.entity_id == "P-002").first()
    original_status = ent.resolution_status
    ent.resolution_status = ResolutionStatus.UNRESOLVED
    db.commit()
    
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-002",
        relationship_type="TRANSFERRED_TO",
        target_entity_id="UPI-001",
        source_record_id="SR-101"
    )
    res = validate_relationship(db, req)
    
    # Restore
    ent.resolution_status = original_status
    db.commit()
    
    assert res.status == ValidationStatusEnum.CANDIDATE
    assert "SOURCE_ENTITY_UNRESOLVED" in res.reasons

def test_invalid_relationship_ontology(db):
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-002",
        relationship_type="KNOWS",
        target_entity_id="P-003",
        source_record_id="SR-101"
    )
    res = validate_relationship(db, req)
    assert res.status == ValidationStatusEnum.REJECTED
    assert "INVALID_RELATIONSHIP_ONTOLOGY" in res.reasons

def test_invalid_source_target_type(db):
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="LOC-001",
        relationship_type="USES",
        target_entity_id="PH-001",
        source_record_id="SR-101"
    )
    res = validate_relationship(db, req)
    assert res.status == ValidationStatusEnum.REJECTED
    assert "INVALID_ENTITY_TYPE_PAIR" in res.reasons

def test_missing_provenance(db):
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-002",
        relationship_type="TRANSFERRED_TO",
        target_entity_id="UPI-001",
        source_record_id=""
    )
    res = validate_relationship(db, req)
    assert res.status == ValidationStatusEnum.CANDIDATE
    assert "MISSING_PROVENANCE" in res.reasons

def test_contradiction_detection(db):
    # P-003 owns VEH-001
    req1 = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-003",
        relationship_type="OWNS",
        target_entity_id="VEH-001",
        source_record_id="SR-101"
    )
    res1 = validate_relationship(db, req1)
    
    # Now someone else claims to own VEH-001
    req2 = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-002",
        relationship_type="OWNS",
        target_entity_id="VEH-001",
        source_record_id="SR-102"
    )
    res2 = validate_relationship(db, req2)
    
        
    assert res2.status == ValidationStatusEnum.CANDIDATE
    assert "CONTRADICTORY_RELATIONSHIP" in res2.reasons

def test_idempotent_duplicate_prevention(db):
    req = ValidationRequest(
        case_id="C-001",
        source_entity_id="P-001",
        relationship_type="USES",
        target_entity_id="PH-001",
        source_record_id="SR-103"
    )
    # First submission
    res1 = validate_relationship(db, req)
    assert res1.status == ValidationStatusEnum.CONFIRMED
    
    # Second submission
    req.source_record_id = "SR-104" # Different source, same fact
    res2 = validate_relationship(db, req)
    assert res2.status == ValidationStatusEnum.CONFIRMED
    assert "DUPLICATE_CANONICAL_RELATIONSHIP" in res2.reasons
    
    # Verify count is 1
    rel_count = db.query(Relationship).filter_by(
        source_entity_id="P-001", 
        target_entity_id="PH-001",
        relationship_type="USES"
    ).count()
    
    assert rel_count == 1
    
    # Check assertions count is 2
    assert_count = db.query(RelationshipAssertion).filter_by(
        source_entity_id="P-001", 
        target_entity_id="PH-001",
        relationship_type="USES"
    ).count()
    # Check assertions count is 2
    assert_count = db.query(RelationshipAssertion).filter_by(
        source_entity_id="P-001", 
        target_entity_id="PH-001",
        relationship_type="USES"
    ).count()
    assert assert_count >= 2
    
    
def test_cross_case_relationship(db):
    req = ValidationRequest(
        case_id="C-002", # different case
        source_entity_id="P-002",
        relationship_type="COMMUNICATES_WITH",
        target_entity_id="P-003",
        source_record_id="SR-201"
    )
    res = validate_relationship(db, req)
    assert res.status == ValidationStatusEnum.CONFIRMED

