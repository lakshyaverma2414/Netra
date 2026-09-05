"""
tools.py — LangGraph tool definitions for NETRA Investigation Agent (Phase A)

All 8 tool names are preserved exactly so the LLM's existing knowledge remains
valid.  Each tool delegates entirely to InvestigationService, which handles
input validation, error catching, and output truncation.

If a tool result contains {"tool_error": True, ...}, it is returned as-is so
the LLM can read the structured error and respond appropriately without
inventing facts.

No raw Python exceptions ever escape a tool function.
"""

import logging
from typing import List, Dict, Optional

from langchain_core.tools import tool

from app.agent.tool_service import InvestigationService, get_session

logger = logging.getLogger(__name__)


@tool
def search_cases(query: str) -> List[Dict]:
    """Find cases matching an investigator's query."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.search_cases(query)


@tool
def search_entities(query: str, case_id: Optional[str] = None) -> List[Dict]:
    """Resolve investigator-mentioned entities against canonical NETRA entities."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.search_entities(query)


@tool
def get_entity(entity_id: str) -> Dict:
    """Return canonical entity details and authorized relationships/case memberships."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.get_entity(entity_id)


@tool
def explore_graph(case_id: str, entity_id: str, depth: int) -> Dict:
    """Explore the network graph starting from an entity, limited to a max depth of 5."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.explore_graph(case_id, entity_id, depth)


@tool
def get_relationship(relationship_id: str) -> Dict:
    """Return relationship details, ensuring only CONFIRMED relationships are exposed."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.get_relationship(relationship_id)


@tool
def get_findings(case_id: str) -> List[Dict]:
    """Return the Step 10.9 investigator-facing findings."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.get_findings(case_id)


@tool
def get_evidence(evidence_id: str) -> Dict:
    """Return evidence metadata and provenance."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.get_evidence(evidence_id)


@tool
def run_network_analysis(case_id: str) -> Dict:
    """Expose existing deterministic analytics for a case (degree, betweenness, etc)."""
    with get_session() as db:
        svc = InvestigationService(db)
        return svc.run_network_analysis(case_id)


def get_all_tools():
    return [
        search_cases,
        search_entities,
        get_entity,
        explore_graph,
        get_relationship,
        get_findings,
        get_evidence,
        run_network_analysis,
    ]
