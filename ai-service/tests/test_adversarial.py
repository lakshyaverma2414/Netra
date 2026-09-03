import pytest
from app.schemas.ingestion import NormalizedRecord
from app.schemas.resolution import CanonicalEntity, MentionProvenance
from app.schemas.relationship import RelationshipCandidate, RelationshipType
from app.validation.relationship_validator import RelationshipValidator
from app.schemas.validation import ValidationStatus, RelationshipValidationResult
from app.graph.graph_writer import MockGraphWriter as GraphWriter

def create_mock_data():
    r1 = NormalizedRecord(metadata={"source_file": "r1"}, record_id="R1", source_type="FIR", content_type="TEXT", text="Rahul uses phone X. He also was near Bhopal.")
    r2 = NormalizedRecord(metadata={"source_file": "r2"}, record_id="R2", source_type="FIR", content_type="TEXT", text="Rahul does not use phone X.")
    r3 = NormalizedRecord(metadata={"source_file": "r3"}, record_id="R3", source_type="FIR", content_type="TEXT", text="Rahul uses phone X again.")
    
    c1 = CanonicalEntity(entity_id="P001", entity_type="PERSON", canonical_name="Rahul", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[])
    c2 = CanonicalEntity(entity_id="PHONE001", entity_type="PHONE", canonical_name="phone X", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[])
    
    return [r1, r2, r3], [c1, c2]

def test_temporal_spatial_checks():
    recs, ents = create_mock_data()
    cand = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R1", evidence_id="E1", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X", negated=False,
        temporal_context={"date": "2026-08-12"}, location_context="Bhopal"
    )
    cand2 = RelationshipCandidate(
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_id="R3", evidence_id="E3", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X again", negated=False
    )
    validator = RelationshipValidator(recs, ents)
    res = validator.validate([cand])
    assert res[0].checks["temporal_check"] == "SUPPORTED"
    assert res[0].checks["spatial_check"] == "SUPPORTED"
    
    res2 = validator.validate([cand2])
    assert res2[0].checks["temporal_check"] == "UNKNOWN"
    assert res2[0].checks["spatial_check"] == "UNKNOWN"

def test_contradiction_provenance():
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
    assert res[0].status == ValidationStatus.NEEDS_REVIEW
    assert "R1" in res[0].source_record_ids
    assert "R2" in res[0].source_record_ids
    assert "E1" in res[0].evidence_ids
    assert "E2" in res[0].evidence_ids

def test_multiple_evidence():
    recs, ents = create_mock_data()
    cands = [
        RelationshipCandidate(source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001", source_record_id="R1", evidence_id="E1", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X.", negated=False),
        RelationshipCandidate(source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001", source_record_id="R3", evidence_id="E3", extraction_method="TEXT_RULE", evidence_text="Rahul uses phone X again.", negated=False)
    ]
    validator = RelationshipValidator(recs, ents)
    res = validator.validate(cands)
    assert len(res) == 1
    assert set(res[0].source_record_ids) == {"R1", "R3"}
    assert set(res[0].evidence_ids) == {"E1", "E3"}

def test_graph_writer_boundary():
    writer = GraphWriter()
    writer.connect()
    
    res_conf = RelationshipValidationResult(relationship_id="r1", status=ValidationStatus.CONFIRMED, source_entity_id="A", relationship_type="USES", target_entity_id="B")
    res_rev = RelationshipValidationResult(relationship_id="r2", status=ValidationStatus.NEEDS_REVIEW, source_entity_id="A", relationship_type="USES", target_entity_id="C")
    res_rej = RelationshipValidationResult(relationship_id="r3", status=ValidationStatus.REJECTED, source_entity_id="A", relationship_type="USES", target_entity_id="D")
    
    written = writer.write_relationships([res_conf, res_rev, res_rej])
    assert written == 1
