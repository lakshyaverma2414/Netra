import pytest
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.analytics.analytics_service import AnalyticsService

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_p002_cross_case_bridge(db):
    svc = AnalyticsService(db)
    result = svc.generate_leads(case_id=None)
    
    # Check for P-002 cross case bridge
    p002_bridge = next((p for p in result["patterns"] if p["type"] == "CROSS_CASE_BRIDGE" and p["entity_id"] == "P-002"), None)
    assert p002_bridge is not None, "P-002 not identified as a cross-case bridge"
    assert "C-002" in p002_bridge["cases"]
    assert "C-003" in p002_bridge["cases"]

def test_ph002_cross_case_bridge(db):
    svc = AnalyticsService(db)
    result = svc.generate_leads(case_id=None)
    
    ph002_bridge = next((p for p in result["patterns"] if p["type"] == "CROSS_CASE_BRIDGE" and p["entity_id"] == "PH-002"), None)
    assert ph002_bridge is not None, "PH-002 not identified as a cross-case bridge"
    assert "C-001" in ph002_bridge["cases"]
    assert "C-002" in ph002_bridge["cases"]

def test_financial_convergence(db):
    svc = AnalyticsService(db)
    result = svc.generate_leads(case_id=None)
    
    fc = next((p for p in result["patterns"] if p["type"] == "FINANCIAL_CONVERGENCE" and p["identifier"] == "UPI-001"), None)
    assert fc is not None, "UPI-001 not identified as financial convergence"
    assert "P-002" in fc["sources"]
    assert "P-003" in fc["sources"]

def test_multi_hop_path(db):
    svc = AnalyticsService(db)
    result = svc.find_multi_hop_path("P-001", "VEH-001", max_depth=5)
    
    assert "error" not in result
    path = result["path"]
    assert path[0] == "P-001"
    assert path[-1] == "VEH-001"
    assert len(path) > 1

def test_negative_relationship_ignored(db):
    svc = AnalyticsService(db)
    result = svc.generate_leads(case_id=None)
    
    # P-001 and P-003 should NOT have a direct relationship in the graph
    # If they did, they would be connected. We can test this by checking path length between them
    path_result = svc.find_multi_hop_path("P-001", "P-003", max_depth=2) # if directly connected, depth is 1
    
    # Actually P-001 -> PH-001 -> PH-002 -> P-002 -> P-003. Shortest path is 4 edges!
    # So if they are connected by R-009 (direct), path length would be 2 nodes (1 edge).
    assert "error" in path_result or len(path_result.get("path", [])) > 2, "P-001 and P-003 are directly connected! Negative test failed!"

