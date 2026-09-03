import os
os.environ['POSTGRES_HOST']='127.0.0.1'
os.environ['POSTGRES_PORT']='5433'
os.environ['POSTGRES_USER']='postgres'
os.environ['POSTGRES_PASSWORD']='netra_admin'
os.environ['POSTGRES_DB']='postgres'
os.environ['AGE_GRAPH_NAME']='crime_network'

import json
from fastapi.testclient import TestClient
from app.main import app
from app.graph.age_writer import AgeGraphWriter
from app.schemas.validation import RelationshipValidationResult, ValidationStatus
from app.schemas.resolution import CanonicalEntity
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

def setup_graph():
    writer = AgeGraphWriter(dsn="dbname=postgres user=postgres password=netra_admin host=127.0.0.1 port=5433", graph_name="crime_network")
    writer.connect()
    
    # Write entities
    e1 = CanonicalEntity(entity_id="P001", entity_type="PERSON", canonical_name="Rahul", resolution_status="CONFIRMED", resolution_score=1.0, aliases=["R"])
    e2 = CanonicalEntity(entity_id="PHONE001", entity_type="PHONE", canonical_name="9876543210", resolution_status="CONFIRMED", resolution_score=1.0, aliases=[])
    e3 = CanonicalEntity(entity_id="P002", entity_type="PERSON", canonical_name="Amit", resolution_status="PROBABLE", resolution_score=0.87, aliases=[])
    e4 = CanonicalEntity(entity_id="UPI001", entity_type="UPI_ACCOUNT", canonical_name="amit@upi", resolution_status="CONFIRMED", resolution_score=1.0, aliases=[])
    
    writer.write_entities([e1, e2, e3, e4])
    
    # Write relationships
    # P001 -> PHONE001
    r1 = RelationshipValidationResult(
        relationship_id="REL001", status=ValidationStatus.CONFIRMED,
        source_entity_id="P001", relationship_type="USES", target_entity_id="PHONE001",
        source_record_ids=["REC1"], evidence_ids=["EVD1"],
        validated_at=datetime.utcnow(), validator_version="1.0"
    )
    # P001 -> P002
    r2 = RelationshipValidationResult(
        relationship_id="REL002", status=ValidationStatus.CONFIRMED,
        source_entity_id="P001", relationship_type="ASSOCIATED_WITH", target_entity_id="P002",
        source_record_ids=["REC2"], evidence_ids=["EVD2"],
        validated_at=datetime.utcnow(), validator_version="1.0"
    )
    # P002 -> UPI001
    r3 = RelationshipValidationResult(
        relationship_id="REL003", status=ValidationStatus.CONFIRMED,
        source_entity_id="P002", relationship_type="OWNS", target_entity_id="UPI001",
        source_record_ids=["REC3"], evidence_ids=["EVD3"],
        validated_at=datetime.utcnow(), validator_version="1.0"
    )
    # Rejected relation P001 -> UPI001 (should not write)
    r_reject = RelationshipValidationResult(
        relationship_id="REL004", status=ValidationStatus.REJECTED,
        source_entity_id="P001", relationship_type="TRANSFERRED_TO", target_entity_id="UPI001",
        source_record_ids=[], evidence_ids=[],
        validated_at=datetime.utcnow(), validator_version="1.0"
    )
    
    writer.write_relationships([r1, r2, r3, r_reject])
    writer.disconnect()

def test_depth_and_properties():
    setup_graph()
    
    # Depth 1
    res1 = client.get("/api/v1/graph/explore?entity_id=P001&depth=1")
    assert res1.status_code == 200
    d1 = res1.json()
    n_ids1 = [n["data"]["id"] for n in d1["nodes"]]
    assert "P001" in n_ids1 and "PHONE001" in n_ids1 and "P002" in n_ids1
    assert "UPI001" not in n_ids1 # Depth 1, so no UPI001
    
    # Check properties
    p001_node = next(n for n in d1["nodes"] if n["data"]["id"] == "P001")
    assert p001_node["data"]["resolution_status"] == "CONFIRMED"
    assert "R" in p001_node["data"]["aliases"]
    
    p002_node = next(n for n in d1["nodes"] if n["data"]["id"] == "P002")
    assert p002_node["data"]["resolution_status"] == "PROBABLE"
    assert p002_node["data"]["resolution_score"] == 0.87
    
    rel1 = next(e for e in d1["edges"] if e["data"]["id"] == "REL001")
    assert "REC1" in rel1["data"]["source_record_ids"]
    assert "EVD1" in rel1["data"]["evidence_ids"]
    assert rel1["data"]["status"] == "CONFIRMED"
    
    # Depth 2
    res2 = client.get("/api/v1/graph/explore?entity_id=P001&depth=2")
    assert res2.status_code == 200
    d2 = res2.json()
    n_ids2 = [n["data"]["id"] for n in d2["nodes"]]
    assert "UPI001" in n_ids2 # Depth 2, should be there!
    
    # Check injection protection
    res_inj = client.get("/api/v1/graph/explore?entity_id=P001' OR '1'='1")
    assert res_inj.status_code == 400
