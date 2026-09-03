import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai-service')))
from app.main import app

client = TestClient(app)

@patch('app.clients.llama_client.LlamaClient.check_health')
def test_health_check_qwen_connected(mock_check_health):
    mock_check_health.return_value = True
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["qwen"] == "connected"
    assert data["database"] == "connected"
    assert data["graph"] == "connected"

@patch('app.clients.llama_client.LlamaClient.check_health')
def test_health_check_qwen_disconnected(mock_check_health):
    mock_check_health.return_value = False
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
    assert data["qwen"] == "disconnected"

@patch('app.clients.llama_client.LlamaClient.generate_json')
def test_extract_entities_endpoint(mock_generate_json):
    mock_generate_json.return_value = {
        "entities": [
            {"mention": "Aryan", "type": "PERSON"},
            {"mention": "+91-9876543210", "type": "PHONE"}
        ]
    }
    
    response = client.post("/api/v1/extraction/entities", json={
        "case_id": "C-001",
        "text": "Aryan was observed using mobile number +91-9876543210."
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "C-001"
    assert len(data["entities"]) == 2
    assert data["entities"][0]["mention"] == "Aryan"
    assert data["entities"][0]["type"] == "PERSON"
    assert data["entities"][1]["mention"] == "+91-9876543210"
    assert data["entities"][1]["type"] == "PHONE"

@patch('app.clients.llama_client.LlamaClient.generate_json')
def test_extract_relationships_endpoint(mock_generate_json):
    mock_generate_json.return_value = {
        "relationships": [
            {
                "source_mention": "Aryan",
                "relationship_type": "USES",
                "target_mention": "+91-9876543210",
                "evidence_text": "Aryan was observed using mobile number +91-9876543210."
            }
        ]
    }
    
    response = client.post("/api/v1/extraction/relationships", json={
        "case_id": "C-001",
        "text": "Aryan was observed using mobile number +91-9876543210."
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "C-001"
    assert len(data["relationships"]) == 1
    assert data["relationships"][0]["source_mention"] == "Aryan"
    assert data["relationships"][0]["relationship_type"] == "USES"
    assert data["relationships"][0]["target_mention"] == "+91-9876543210"

