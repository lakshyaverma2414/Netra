import pytest
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import SessionLocal
from app.db.models import Relationship, ValidationStatus
from app.graph.projection_service import ProjectionService
from app.graph.age_graph_repository import AgeGraphRepository
from app.api.graph import explore_graph_api

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_idempotency(db):
    svc = ProjectionService(db)
    
    # Project 1
    stats1 = svc.project_all()
    # Project 2
    stats2 = svc.project_all()
    # Project 3
    stats3 = svc.project_all()
    
    repo = AgeGraphRepository(db)
    glob_graph = repo.get_global_subgraph()
    
    # Edges should not multiply
    edges_count = len(glob_graph["edges"])
    # In seeded DB, 11 edges (1 is NEEDS_REVIEW, so 10 CONFIRMED).
    assert edges_count == 10
    
    nodes_count = len(glob_graph["nodes"])
    # E.g. ~11 nodes
    assert nodes_count > 0

def test_negative_test_unconfirmed_relationship(db):
    svc = ProjectionService(db)
    svc.project_all()
    # P-001 ASSOCIATED_WITH P-003 is NEEDS_REVIEW (R-BAD-001)
    # Check if R-BAD-001 is in the graph
    repo = AgeGraphRepository(db)
    glob_graph = repo.get_global_subgraph()
    
    has_r009 = any(e["data"]["relationship_id"] == "R-BAD-001" for e in glob_graph["edges"])
    assert not has_r009, "NEEDS_REVIEW relationship was wrongly projected!"

def test_traceability_preserved(db):
    repo = AgeGraphRepository(db)
    glob_graph = repo.get_global_subgraph()
    
    for e in glob_graph["edges"]:
        rel_id = e["data"].get("relationship_id")
        assert rel_id is not None
        assert rel_id.startswith("R-")

def test_case_isolation_and_cross_case(db):
    repo = AgeGraphRepository(db)
    
    # C-001 should have P-001, PH-001, LOC-001, PH-002
    c1 = repo.get_case_subgraph("C-001")
    c1_nodes = [n["data"]["id"] for n in c1["nodes"]]
    assert "P-001" in c1_nodes
    assert "PH-001" in c1_nodes
    assert "P-002" not in c1_nodes # P-002 is C-002/C-003

    # C-002 should have P-002
    c2 = repo.get_case_subgraph("C-002")
    c2_nodes = [n["data"]["id"] for n in c2["nodes"]]
    assert "P-002" in c2_nodes
    assert "P-001" not in c2_nodes

    # Global cross case should have one P-002 vertex, not duplicates
    glob = repo.get_global_subgraph()
    p002_nodes = [n for n in glob["nodes"] if n["data"]["id"] == "P-002"]
    assert len(p002_nodes) == 1

def test_depth_traversal(db):
    repo = AgeGraphRepository(db)
    
    d1 = repo.get_global_subgraph(entity_id="P-001", depth=1)
    d2 = repo.get_global_subgraph(entity_id="P-001", depth=2)
    d3 = repo.get_global_subgraph(entity_id="P-001", depth=3)
    
    assert len(d1["nodes"]) < len(d2["nodes"])
    assert len(d2["nodes"]) < len(d3["nodes"])

def test_rejection_mutation_stale_removal(db):
    svc = ProjectionService(db)
    repo = AgeGraphRepository(db)
    
    # 1. Start with R-001 CONFIRMED (which it is)
    r001 = db.query(Relationship).filter_by(relationship_id="R-001").first()
    assert r001.status == ValidationStatus.CONFIRMED
    
    glob = repo.get_global_subgraph()
    assert any(e["data"]["relationship_id"] == "R-001" for e in glob["edges"])
    
    # 2. Reject it in Postgres
    r001.status = ValidationStatus.REJECTED
    db.commit()
    
    # 3. Project
    svc.project_all()
    
    # 4. Verify it's gone
    glob2 = repo.get_global_subgraph()
    assert not any(e["data"]["relationship_id"] == "R-001" for e in glob2["edges"])
    
    # 5. Restore it to CONFIRMED
    r001.status = ValidationStatus.CONFIRMED
    db.commit()
    svc.project_all()
    
    glob3 = repo.get_global_subgraph()
    assert any(e["data"]["relationship_id"] == "R-001" for e in glob3["edges"])

