import pytest
from app.schemas.ingestion import NormalizedRecord
from app.schemas.resolution import CanonicalEntity, MentionProvenance
from app.schemas.relationship import RelationshipCandidate, RelationshipType
from app.validation.relationship_validator import RelationshipValidator
from app.schemas.validation import ValidationStatus

def create_mock_data():
    r1 = NormalizedRecord(metadata={"source_file": "r1"}, record_id="R1", source_type="FIR", content_type="TEXT", text="Rahul uses phone X.")
    r2 = NormalizedRecord(metadata={"source_file": "r2"}, record_id="R2", source_type="FIR", content_type="TEXT", text="Rahul does not use phone X.")
    
    c1 = CanonicalEntity(entity_id="P001", entity_type="PERSON", canonical_name="Rahul", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[])
    c2 = CanonicalEntity(entity_id="PHONE001", entity_type="PHONE", canonical_name="phone X", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[])
    
    return [r1, r2], [c1, c2]

def test_pass_valid_relationship():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E1", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert len(res) == 1
    assert res[0].status == ValidationStatus.CONFIRMED

def test_fail_missing_entity():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="P999", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E1", extraction_method="STRUCTURED_RULE", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert res[0].status == ValidationStatus.REJECTED
    assert "MISSING_ENTITY" in res[0].reasons

def test_fail_invalid_ontology():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="PHONE001", relationship_type="OWNS", target_entity_id="P001",
        source_record_id="R1", evidence_id="E1", extraction_method="STRUCTURED_RULE", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert res[0].status == ValidationStatus.REJECTED
    assert "INVALID_ONTOLOGY_TYPES" in res[0].reasons

def test_fail_missing_source_record():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="NONEXISTENT", evidence_id="E1", extraction_method="STRUCTURED_RULE", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert res[0].status == ValidationStatus.REJECTED
    assert any("SOURCE_RECORD_NOT_FOUND" in r for r in res[0].reasons)

def test_fail_missing_evidence():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E1", extraction_method="QWEN_SEMANTIC", evidence_text="", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert res[0].status == ValidationStatus.REJECTED
    assert "MISSING_EVIDENCE" in res[0].reasons
    
def test_fail_unsupported_evidence_text():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E1", extraction_method="QWEN_SEMANTIC", evidence_text="Hallucinated evidence", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert res[0].status == ValidationStatus.REJECTED
    assert "UNSUPPORTED_EVIDENCE_TEXT" in res[0].reasons

def test_fail_negation():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R2", evidence_id="E2", extraction_method="TEXT_RULE", evidence_text="Rahul does not use phone X.", negated=True
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert res[0].status == ValidationStatus.REJECTED
    assert "NEGATED_RELATIONSHIP" in res[0].reasons

def test_review_contradiction():
    recs, ents = create_mock_data()
    cand1 = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E1", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X.", negated=False
    )
    cand2 = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R2", evidence_id="E2", extraction_method="TEXT_RULE", evidence_text="Rahul does not use phone X.", negated=True
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand1, cand2])
    assert len(res) == 1
    assert res[0].status == ValidationStatus.NEEDS_REVIEW
    assert "CONTRADICTORY_EVIDENCE" in res[0].reasons

def test_duplicate():
    recs, ents = create_mock_data()
    cand1 = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E1", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X.", negated=False
    )
    cand2 = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E2", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X.", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand1, cand2])
    assert len(res) == 1
    assert res[0].status == ValidationStatus.CONFIRMED
    assert len(res[0].evidence_ids) == 2
    assert res[0].checks["duplicate_check"] == "MERGED"
