import pytest
import uuid
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Finding, FindingEntity, FindingRelationship, Relationship, InvestigatorFeedback
from app.services.findings_service import FindingsService

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_finding_creation_and_idempotency(db):
    svc = FindingsService(db)
    
    lead = {
        "lead_id": "TEST-LEAD-001",
        "lead_type": "FINANCIAL_CONVERGENCE",
        "priority": "HIGH",
        "title": "Test Lead",
        "description": "A test lead.",
        "case_ids": ["C-002"],
        "entity_ids": ["P-002", "UPI-001"],
        "relationship_ids": ["R-005"]
    }
    
    # Run once
    f1 = svc.generate_finding_from_lead(lead)
    assert f1 is not None
    assert f1.finding_type == "FINANCIAL_CONVERGENCE"
    
    # Run twice
    f2 = svc.generate_finding_from_lead(lead)
    assert f1.finding_id == f2.finding_id, "Finding generation is not idempotent!"
    
    # Check entities and relationships
    entities = db.query(FindingEntity).filter_by(finding_id=f1.finding_id).all()
    e_ids = [e.entity_id for e in entities]
    assert "P-002" in e_ids
    assert "UPI-001" in e_ids
    
    rels = db.query(FindingRelationship).filter_by(finding_id=f1.finding_id).all()
    r_ids = [r.relationship_id for r in rels]
    assert "R-005" in r_ids

def test_negative_relationship_excluded(db):
    svc = FindingsService(db)
    
    # Attempt to generate a finding involving R-BAD-001
    lead = {
        "lead_id": "TEST-LEAD-BAD",
        "lead_type": "SUSPICIOUS",
        "priority": "HIGH",
        "case_ids": ["C-001"],
        "entity_ids": ["P-001", "P-003"],
        "relationship_ids": ["R-BAD-001"] # This is NEEDS_REVIEW
    }
    
    f = svc.generate_finding_from_lead(lead)
    
    # The relationship should NOT be attached because it's not CONFIRMED
    rels = db.query(FindingRelationship).filter_by(finding_id=f.finding_id).all()
    r_ids = [r.relationship_id for r in rels]
    assert "R-BAD-001" not in r_ids, "Negative relationship was included in finding!"

def test_feedback_submission_and_immutability(db):
    svc = FindingsService(db)
    
    lead = {
        "lead_id": f"TEST-LEAD-FEEDBACK-{uuid.uuid4()}",
        "case_ids": ["C-001"]
    }
    f = svc.generate_finding_from_lead(lead)
    
    # Check default status
    assert f.status == "NEW"
    
    # Submit REJECT feedback
    result = svc.submit_feedback(str(f.finding_id), "REJECT", "Insufficient evidence")
    assert result["decision"] == "REJECT"
    
    db.refresh(f)
    assert f.status == "REJECT"
    
    # Verify graph truth is NOT mutated (Assuming R-005 was used in a finding)
    rel = db.query(Relationship).filter_by(relationship_id="R-005").first()
    # It should still be CONFIRMED, not REJECTED just because a finding was rejected.
    assert rel.status.value == "CONFIRMED"
    
    # Verify feedback record exists
    fb = db.query(InvestigatorFeedback).filter_by(feedback_id=result["feedback_id"]).first()
    assert fb is not None
    assert fb.decision == "REJECT"

def test_traceability_api(db):
    from app.db.models import RelationshipAssertion, RelationshipAssertionLink
    import uuid
    # Mock assertion link so we can test traceability
    assrt = RelationshipAssertion(
        assertion_id=uuid.uuid4(), 
        source_entity_id="P-003", 
        target_entity_id="UPI-001", 
        relationship_type="OWNS",
        source_record_id="SR-303",
        status="CONFIRMED"
    )
    db.add(assrt)
    db.flush()
    db.add(RelationshipAssertionLink(relationship_id="R-009", assertion_id=assrt.assertion_id))
    db.commit()

    svc = FindingsService(db)
    
    lead = {
        "lead_id": "TEST-LEAD-TRACE",
        "case_ids": ["C-003"],
        "relationship_ids": ["R-009"] # P-003 OWNS UPI-001
    }
    f = svc.generate_finding_from_lead(lead)
    
    detail = svc.get_finding_detail(str(f.finding_id))
    assert detail is not None
    assert "R-009" in detail["relationship_ids"]
    assert "SR-303" in detail["source_record_ids"], "Source record traceability failed!"
    assert detail["generated_by"] == "analytics_rule"
    assert detail["algorithm_version"] == "10.8.0"

