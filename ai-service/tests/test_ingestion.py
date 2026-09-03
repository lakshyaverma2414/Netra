import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app
from app.ingestion.normalizer import normalize_phone, normalize_vehicle, normalize_text
from app.services.ingestion_service import process_file

client = TestClient(app)

DATA_DIR = Path("d:/NETRA/SIH2026/ai-service/data/synthetic/sources")

def test_normalize_phone():
    assert normalize_phone("+91-9876543210") == "+919876543210"
    assert normalize_phone("98765 43210") == "9876543210"

def test_normalize_vehicle():
    assert normalize_vehicle("MP-09-AB-1234") == "MP09AB1234"
    assert normalize_vehicle("mp 09 ab 1234") == "MP09AB1234"
    assert normalize_vehicle("MP09AB1234") == "MP09AB1234"

def test_normalize_text():
    assert normalize_text("  This   is  a test  ") == "This is a test"
    assert normalize_text("Hello\tWorld") == "Hello World"

def test_ingest_fir():
    filepath = str(DATA_DIR / "fir_001.json")
    records = process_file(filepath, "FIR")
    assert len(records) > 0
    assert records[0].source_type == "FIR"
    assert records[0].content_type == "TEXT"
    assert records[0].metadata.source_file == "fir_001.json"
    assert records[0].record_id != ""
    assert records[0].text is not None

def test_ingest_cdr():
    filepath = str(DATA_DIR / "cdr_001.csv")
    records = process_file(filepath, "CDR")
    assert len(records) > 0
    assert records[0].source_type == "CDR"
    assert records[0].content_type == "STRUCTURED"
    assert records[0].metadata.source_file == "cdr_001.csv"
    assert records[0].data["caller"] is not None

def test_ingest_transaction():
    filepath = str(DATA_DIR / "transactions_001.csv")
    records = process_file(filepath, "TRANSACTION")
    assert len(records) > 0
    assert records[0].source_type == "TRANSACTION"
    assert records[0].content_type == "STRUCTURED"
    assert records[0].metadata.source_file == "transactions_001.csv"
    assert records[0].data["amount"] is not None

def test_ingest_surveillance():
    filepath = str(DATA_DIR / "surveillance_001.json")
    records = process_file(filepath, "SURVEILLANCE")
    assert len(records) > 0
    assert records[0].source_type == "SURVEILLANCE"
    assert records[0].content_type == "SEMI_STRUCTURED"
    assert records[0].metadata.source_file == "surveillance_001.json"
    # test vehicle normalization inside surveillance
    for r in records:
        if "vehicle_number" in r.data:
            assert " " not in r.data["vehicle_number"]
            assert "-" not in r.data["vehicle_number"]

def test_missing_file_handling():
    with pytest.raises(FileNotFoundError):
        process_file("missing_file.json", "FIR")

def test_api_process_endpoint():
    filepath = str(DATA_DIR / "fir_001.json")
    response = client.post("/api/v1/ingestion/process", json={
        "source_file_path": filepath,
        "source_type": "FIR"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "FIR"
    assert data["record_count"] > 0
    assert len(data["records"]) == data["record_count"]

def test_health_check_still_passes():
    response = client.get("/health")
    assert response.status_code == 200
