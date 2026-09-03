import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.schemas.resolution import CanonicalEntity, ResolutionStatus, MentionProvenance
from app.services.relationship_service import extract_all_relationships

client = TestClient(app)

def test_structured_cdr_extraction():
    record = NormalizedRecord(metadata={"source_file": "test.txt"}, 
        record_id="R1", source_type="CDR", content_type="STRUCTURED",
        data={"caller": "+91-9876543210", "receiver": "+91-9123456789"}
    )
    m1 = EntityMention(record_id="R1", entity_type="PHONE", text="+91-9876543210", normalized_value="919876543210", extraction_method="RULE", confidence=1.0, mention_id="M1")
    m2 = EntityMention(record_id="R1", entity_type="PHONE", text="+91-9123456789", normalized_value="919123456789", extraction_method="RULE", confidence=1.0, mention_id="M2")
    c1 = CanonicalEntity(entity_id="PHONE1", entity_type="PHONE", canonical_name="919876543210", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[MentionProvenance(mention_id="M1", record_id="R1")])
    c2 = CanonicalEntity(entity_id="PHONE2", entity_type="PHONE", canonical_name="919123456789", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[MentionProvenance(mention_id="M2", record_id="R1")])
    
    rels = extract_all_relationships([record], [m1, m2], [c1, c2])
    assert len(rels) == 1
    assert rels[0].relationship_type == "COMMUNICATES_WITH"
    assert rels[0].source_entity_id == "PHONE1"
    assert rels[0].target_entity_id == "PHONE2"
    assert rels[0].status == "CANDIDATE"

def test_text_rule_extraction():
    record = NormalizedRecord(metadata={"source_file": "test.txt"}, 
        record_id="R2", source_type="FIR", content_type="TEXT",
        text="Rahul uses mobile number 9876543210."
    )
    m1 = EntityMention(record_id="R2", entity_type="PERSON", text="Rahul", normalized_value="Rahul", extraction_method="RULE", confidence=1.0, mention_id="M3")
    m2 = EntityMention(record_id="R2", entity_type="PHONE", text="9876543210", normalized_value="919876543210", extraction_method="RULE", confidence=1.0, mention_id="M4")
    c1 = CanonicalEntity(entity_id="PER1", entity_type="PERSON", canonical_name="Rahul", resolution_status="PROBABLE", resolution_score=0.8, source_mentions=[MentionProvenance(mention_id="M3", record_id="R2")])
    c2 = CanonicalEntity(entity_id="PHONE3", entity_type="PHONE", canonical_name="919876543210", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[MentionProvenance(mention_id="M4", record_id="R2")])

    rels = extract_all_relationships([record], [m1, m2], [c1, c2])
    assert len(rels) == 1
    assert rels[0].relationship_type == "USES"
    assert rels[0].source_entity_id == "PER1"
    assert rels[0].target_entity_id == "PHONE3"
    assert rels[0].extraction_method == "TEXT_RULE"

def test_negation_handling():
    record = NormalizedRecord(metadata={"source_file": "test.txt"}, 
        record_id="R3", source_type="FIR", content_type="TEXT",
        text="Rahul did not use phone 9876543210."
    )
    m1 = EntityMention(record_id="R3", entity_type="PERSON", text="Rahul", normalized_value="Rahul", extraction_method="RULE", confidence=1.0, mention_id="M3")
    m2 = EntityMention(record_id="R3", entity_type="PHONE", text="9876543210", normalized_value="919876543210", extraction_method="RULE", confidence=1.0, mention_id="M4")
    c1 = CanonicalEntity(entity_id="PER1", entity_type="PERSON", canonical_name="Rahul", resolution_status="PROBABLE", resolution_score=0.8, source_mentions=[MentionProvenance(mention_id="M3", record_id="R3")])
    c2 = CanonicalEntity(entity_id="PHONE3", entity_type="PHONE", canonical_name="919876543210", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[MentionProvenance(mention_id="M4", record_id="R3")])

    rels = extract_all_relationships([record], [m1, m2], [c1, c2])
    # The rule 'did not use' triggers the negated flag (the existing rule triggers USES but negated=True)
    assert len(rels) == 1
    assert rels[0].negated is True
    
def test_missing_entity():
    # Record has phone, but mention for person is missing, so no canonical mapping
    record = NormalizedRecord(metadata={"source_file": "test.txt"}, 
        record_id="R4", source_type="FIR", content_type="TEXT",
        text="He uses mobile number 9876543210."
    )
    m2 = EntityMention(record_id="R4", entity_type="PHONE", text="9876543210", normalized_value="919876543210", extraction_method="RULE", confidence=1.0, mention_id="M4")
    c2 = CanonicalEntity(entity_id="PHONE3", entity_type="PHONE", canonical_name="919876543210", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[MentionProvenance(mention_id="M4", record_id="R4")])

    rels = extract_all_relationships([record], [m2], [c2])
    # Should be 0 since PERSON canonical ID is not found
    assert len(rels) == 0

def test_api_endpoint():
    # Pass empty records for now
    req = {
        "records": [],
        "mentions": [],
        "canonical_entities": []
    }
    response = client.post("/api/v1/relationships/process", json=req)
    assert response.status_code == 200
    assert response.json()["total_candidates"] == 0
