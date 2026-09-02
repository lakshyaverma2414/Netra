import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from app.main import app
from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities

client = TestClient(app)
DATA_DIR = Path("d:/NETRA/SIH2026/ai-service/data/synthetic/sources")

def test_extraction_fir():
    records = process_file(str(DATA_DIR / "fir_001.json"), "FIR")
    mentions = extract_entities(records)
    
    types = {m.entity_type for m in mentions}
    texts = {m.text for m in mentions}
    
    assert "PERSON" in types
    assert "PHONE" in types
    assert "CASE" in types
    assert "Rahul Sharma" in texts
    assert "Rocky" in texts
    assert "Central Market" in texts
    assert "FIR-2026-001" in texts
    
    # test character offsets
    person_m = next(m for m in mentions if m.text == "Rahul Sharma")
    assert person_m.start is not None
    assert person_m.end is not None

def test_extraction_cdr():
    records = process_file(str(DATA_DIR / "cdr_001.csv"), "CDR")
    mentions = extract_entities(records)
    assert all(m.entity_type == "PHONE" for m in mentions)
    texts = {m.text for m in mentions}
    assert "+919876543210" in texts

def test_extraction_transaction():
    records = process_file(str(DATA_DIR / "transactions_001.csv"), "TRANSACTION")
    mentions = extract_entities(records)
    assert all(m.entity_type == "UPI_ACCOUNT" for m in mentions)
    texts = {m.text for m in mentions}
    assert "amit@ybl" in texts

def test_extraction_surveillance():
    records = process_file(str(DATA_DIR / "surveillance_001.json"), "SURVEILLANCE")
    mentions = extract_entities(records)
    types = {m.entity_type for m in mentions}
    assert "PERSON" in types
    assert "VEHICLE" in types
    assert "LOCATION" in types
    
def test_api_extraction_endpoint():
    records = process_file(str(DATA_DIR / "fir_001.json"), "FIR")
    payload = {"records": [r.model_dump() for r in records]}
    response = client.post("/api/v1/extraction/entities", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["record_count"] == len(records)
    assert data["entity_count"] > 0
    assert len(data["entities"]) > 0
