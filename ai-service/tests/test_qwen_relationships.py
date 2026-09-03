import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.schemas.resolution import CanonicalEntity, MentionProvenance
from app.services.qwen_relationship_service import extract_qwen_relationships_for_record
import json

client = TestClient(app)

def mock_qwen_response(json_data):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(json_data)
                }
            }
        ]
    }
    return mock_resp

@patch('app.llm.qwen_client.httpx.Client')
def test_qwen_basic_extraction(mock_client):
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.post.return_value = mock_qwen_response({
        "relationships": [
            {
                "source_text": "Rahul",
                "relationship_type": "USES",
                "target_text": "9876543210",
                "evidence_text": "Rahul was seen using phone 9876543210.",
                "negated": False,
                "temporal_context": {"date": "2026-08-12"},
                "location_context": "Bhopal railway station"
            }
        ]
    })
    
    record = NormalizedRecord(metadata={"source_file": "test"}, record_id="R1", source_type="FIR", content_type="TEXT", text="Rahul was seen using phone 9876543210.")
    m1 = EntityMention(record_id="R1", entity_type="PERSON", text="Rahul", normalized_value="Rahul", extraction_method="RULE", confidence=1.0, mention_id="M1")
    m2 = EntityMention(record_id="R1", entity_type="PHONE", text="9876543210", normalized_value="919876543210", extraction_method="RULE", confidence=1.0, mention_id="M2")
    c1 = CanonicalEntity(entity_id="PER1", entity_type="PERSON", canonical_name="Rahul", resolution_status="PROBABLE", resolution_score=0.8, source_mentions=[MentionProvenance(mention_id="M1", record_id="R1")])
    c2 = CanonicalEntity(entity_id="PHONE3", entity_type="PHONE", canonical_name="919876543210", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[MentionProvenance(mention_id="M2", record_id="R1")])
    
    rels = extract_qwen_relationships_for_record(record, [m1, m2], [c1, c2])
    assert len(rels) == 1
    assert rels[0].relationship_type == "USES"
    assert rels[0].source_entity_id == "PER1"
    assert rels[0].target_entity_id == "PHONE3"
    assert rels[0].temporal_context["date"] == "2026-08-12"
    assert rels[0].location_context == "Bhopal railway station"

@patch('app.llm.qwen_client.httpx.Client')
def test_qwen_negation(mock_client):
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.post.return_value = mock_qwen_response({
        "relationships": [
            {
                "source_text": "Rahul",
                "relationship_type": "OWNS",
                "target_text": "vehicle X",
                "evidence_text": "The report does not state that Rahul owns vehicle X.",
                "negated": True
            }
        ]
    })
    
    record = NormalizedRecord(metadata={"source_file": "test"}, record_id="R1", source_type="FIR", content_type="TEXT", text="The report does not state that Rahul owns vehicle X.")
    m1 = EntityMention(record_id="R1", entity_type="PERSON", text="Rahul", normalized_value="Rahul", extraction_method="RULE", confidence=1.0, mention_id="M1")
    m2 = EntityMention(record_id="R1", entity_type="VEHICLE", text="vehicle X", normalized_value="vehicle X", extraction_method="RULE", confidence=1.0, mention_id="M2")
    c1 = CanonicalEntity(entity_id="PER1", entity_type="PERSON", canonical_name="Rahul", resolution_status="PROBABLE", resolution_score=0.8, source_mentions=[MentionProvenance(mention_id="M1", record_id="R1")])
    c2 = CanonicalEntity(entity_id="VEH1", entity_type="VEHICLE", canonical_name="vehicle X", resolution_status="CONFIRMED", resolution_score=1.0, source_mentions=[MentionProvenance(mention_id="M2", record_id="R1")])
    
    rels = extract_qwen_relationships_for_record(record, [m1, m2], [c1, c2])
    assert len(rels) == 1
    assert rels[0].negated is True
    assert rels[0].relationship_type == "OWNS"

@patch('app.llm.qwen_client.httpx.Client')
def test_qwen_invalid_json(mock_client):
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "I am Qwen. Here is some invalid json: { relationships: [ ]"
                }
            }
        ]
    }
    mock_instance.post.return_value = mock_resp
    
    record = NormalizedRecord(metadata={"source_file": "test"}, record_id="R1", source_type="FIR", content_type="TEXT", text="Hello")
    rels = extract_qwen_relationships_for_record(record, [], [])
    assert len(rels) == 0 # Must fail safely

@patch('app.llm.qwen_client.httpx.Client')
def test_qwen_unsupported_relationship(mock_client):
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.post.return_value = mock_qwen_response({
        "relationships": [
            {
                "source_text": "Rahul",
                "relationship_type": "REGISTERED_IN",
                "target_text": "vehicle X",
                "evidence_text": "Registered in",
                "negated": False
            }
        ]
    })
    record = NormalizedRecord(metadata={"source_file": "test"}, record_id="R1", source_type="FIR", content_type="TEXT", text="Hello")
    rels = extract_qwen_relationships_for_record(record, [], [])
    assert len(rels) == 0 # Must fail Pydantic validation safely, caught in except block

@patch('app.llm.qwen_client.httpx.Client')
def test_qwen_missing_entity_mapping(mock_client):
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.post.return_value = mock_qwen_response({
        "relationships": [
            {
                "source_text": "Rahul",
                "relationship_type": "COMMUNICATES_WITH",
                "target_text": "Amit",
                "evidence_text": "Rahul spoke to Amit.",
                "negated": False
            }
        ]
    })
    
    record = NormalizedRecord(metadata={"source_file": "test"}, record_id="R1", source_type="FIR", content_type="TEXT", text="Rahul spoke to Amit.")
    m1 = EntityMention(record_id="R1", entity_type="PERSON", text="Rahul", normalized_value="Rahul", extraction_method="RULE", confidence=1.0, mention_id="M1")
    # Missing Amit
    c1 = CanonicalEntity(entity_id="PER1", entity_type="PERSON", canonical_name="Rahul", resolution_status="PROBABLE", resolution_score=0.8, source_mentions=[MentionProvenance(mention_id="M1", record_id="R1")])
    
    rels = extract_qwen_relationships_for_record(record, [m1], [c1])
    assert len(rels) == 0 # Should not invent a canonical ID for Amit

def test_qwen_api_integration():
    req = {
        "records": [],
        "mentions": [],
        "canonical_entities": [],
        "method": "QWEN"
    }
    response = client.post("/api/v1/relationships/process", json=req)
    assert response.status_code == 200
