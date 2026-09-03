from langchain_core.tools import tool
from typing import List, Dict, Optional, Any
from app.db.database import SessionLocal
from app.graph.age_graph_repository import AgeGraphRepository
from app.analytics.analytics_service import AnalyticsService
from app.services.findings_service import FindingsService
from app.db.models import Case, Entity, Relationship, Finding, Evidence

# Utility to manage session inside tool
from contextlib import contextmanager
@contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@tool
def search_cases(query: str) -> List[Dict]:
    """Find cases matching an investigator's query."""
    with get_session() as db:
        cases = db.query(Case).filter(Case.title.ilike(f"%{query}%")).all()
        return [{"case_id": c.case_id, "title": c.title, "description": c.description} for c in cases]

@tool
def search_entities(query: str, case_id: Optional[str] = None) -> List[Dict]:
    """Resolve investigator-mentioned entities against canonical NETRA entities."""
    with get_session() as db:
        # Search aliases or entity names
        entities = db.query(Entity).filter(Entity.name.ilike(f"%{query}%")).all()
        # Not filtering by case for simplicity in the mock, but could check case_entities
        return [{"entity_id": e.entity_id, "entity_type": e.entity_type, "name": e.name} for e in entities]

@tool
def get_entity(entity_id: str) -> Dict:
    """Return canonical entity details and authorized relationships/case memberships."""
    with get_session() as db:
        e = db.query(Entity).filter(Entity.entity_id == entity_id).first()
        if not e:
            return {"error": "Entity not found"}
        return {"entity_id": e.entity_id, "entity_type": e.entity_type, "name": e.name}

@tool
def explore_graph(case_id: str, entity_id: str, depth: int) -> Dict:
    """Explore the network graph starting from an entity, limited to a max depth of 5."""
    if depth > 5:
        return {"error": "Maximum depth is 5."}
    with get_session() as db:
        repo = AgeGraphRepository(db, "crime_network")
        try:
            return repo.explore_graph(case_id, entity_id, depth)
        except Exception as e:
            return {"error": str(e)}

@tool
def get_relationship(relationship_id: str) -> Dict:
    """Return relationship details, ensuring only CONFIRMED relationships are exposed."""
    with get_session() as db:
        r = db.query(Relationship).filter(Relationship.relationship_id == relationship_id).first()
        if not r:
            return {"error": "Relationship not found"}
        if r.status.value != "CONFIRMED":
            return {"error": "Relationship is not authorized for investigation (unconfirmed or rejected)."}
        return {
            "relationship_id": r.relationship_id,
            "source_entity_id": r.source_entity_id,
            "target_entity_id": r.target_entity_id,
            "relationship_type": r.relationship_type,
            "status": r.status.value
        }

@tool
def get_findings(case_id: str) -> List[Dict]:
    """Return the Step 10.9 investigator-facing findings."""
    with get_session() as db:
        svc = FindingsService(db)
        return svc.get_findings_for_case(case_id)

@tool
def get_evidence(evidence_id: str) -> Dict:
    """Return evidence metadata and provenance."""
    with get_session() as db:
        ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
        if not ev:
            return {"error": "Evidence not found"}
        return {
            "evidence_id": ev.evidence_id,
            "type": ev.evidence_type,
            "title": ev.title,
            "source": ev.source
        }

@tool
def run_network_analysis(case_id: str) -> Dict:
    """Expose existing deterministic analytics for a case (degree, betweenness, etc)."""
    with get_session() as db:
        svc = AnalyticsService(db)
        try:
            return svc.analyze_case_network(case_id)
        except Exception as e:
            return {"error": str(e)}

def get_all_tools():
    return [
        search_cases,
        search_entities,
        get_entity,
        explore_graph,
        get_relationship,
        get_findings,
        get_evidence,
        run_network_analysis
    ]
