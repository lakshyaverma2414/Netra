import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.extraction import EntityMention
from app.resolution.resolver import resolve_entities

client = TestClient(app)

def test_person_resolution():
    mentions = [
        EntityMention(record_id="E1", entity_type="PERSON", text="Rahul Sharma", normalized_value="Rahul Sharma", extraction_method="DICT", confidence=1.0),
        EntityMention(record_id="E2", entity_type="PERSON", text="R Sharma", normalized_value="R Sharma", extraction_method="DICT", confidence=1.0),
    ]
    resolved = resolve_entities(mentions)
    assert len(resolved) == 1
    assert resolved[0].resolution_status == "CANDIDATE"
    assert len(resolved[0].source_mentions) == 2

def test_negative_cases():
    mentions = [
        EntityMention(record_id="E1", entity_type="PERSON", text="Rahul Sharma", normalized_value="Rahul Sharma", extraction_method="DICT", confidence=1.0),
        EntityMention(record_id="E5", entity_type="PERSON", text="John Doe", normalized_value="John Doe", extraction_method="DICT", confidence=1.0)
    ]
    resolved = resolve_entities(mentions)
    assert len(resolved) == 2
    assert resolved[0].resolution_status == "UNRESOLVED"
    
def test_adversarial_negative_cases():
    mentions = [
        EntityMention(record_id="E1", entity_type="PERSON", text="Rahul Sharma", normalized_value="Rahul Sharma", extraction_method="DICT", confidence=1.0),
        EntityMention(record_id="E5", entity_type="PERSON", text="Rahul Verma", normalized_value="Rahul Verma", extraction_method="DICT", confidence=1.0)
    ]
    resolved = resolve_entities(mentions)
    assert len(resolved) == 2

def test_bridge_overmerge():
    # A matches B, B matches C, but A doesn't match C
    m1 = EntityMention(record_id="T1", entity_type="PERSON", text="Rahul Sharma", normalized_value="Rahul Sharma", extraction_method="T", confidence=1.0)
    m2 = EntityMention(record_id="T2", entity_type="PERSON", text="R Sharma", normalized_value="R Sharma", extraction_method="T", confidence=1.0)
    m3 = EntityMention(record_id="T3", entity_type="PERSON", text="R Sharmaa", normalized_value="R Sharmaa", extraction_method="T", confidence=1.0)
    m4 = EntityMention(record_id="T4", entity_type="PERSON", text="R Sharmaaa", normalized_value="R Sharmaaa", extraction_method="T", confidence=1.0)
    
    mentions = [m1, m2, m3, m4]
    resolved = resolve_entities(mentions)
    
    # We must explicitly verify that m1 and m4 are NOT in the same canonical entity.
    m1_entity = next((e for e in resolved if any(sm.mention_id == m1.mention_id for sm in e.source_mentions)), None)
    m4_entity = next((e for e in resolved if any(sm.mention_id == m4.mention_id for sm in e.source_mentions)), None)
    
    assert m1_entity is not None
    assert m4_entity is not None
    assert m1_entity.entity_id != m4_entity.entity_id

def test_vehicle_resolution():
    mentions = [
        EntityMention(record_id="V1", entity_type="VEHICLE", text="MP-09-AB-1234", normalized_value="MP09AB1234", extraction_method="RULE", confidence=1.0),
        EntityMention(record_id="V2", entity_type="VEHICLE", text="MP09AB1234", normalized_value="MP09AB1234", extraction_method="RULE", confidence=1.0)
    ]
    resolved = resolve_entities(mentions)
    assert len(resolved) == 1
    assert resolved[0].resolution_status == "CONFIRMED"
    assert resolved[0].resolution_explanation.deterministic_match is True

def test_api_resolution_endpoint():
    mentions = [
        EntityMention(record_id="E1", entity_type="PERSON", text="Amit Kumar", normalized_value="Amit Kumar", extraction_method="DICT", confidence=1.0).model_dump()
    ]
    response = client.post("/api/v1/resolution/resolve", json={"mentions": mentions})
    assert response.status_code == 200
    data = response.json()
    assert data["resolved_count"] == 1
