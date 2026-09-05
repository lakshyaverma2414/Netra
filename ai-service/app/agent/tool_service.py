"""
tool_service.py — Service Adapter Layer for NETRA Investigation Tools (Phase A)

This module provides InvestigationService, a single facade that:
  - Wraps AgeGraphRepository, AnalyticsService, and FindingsService
  - Maps tool method names to the correct repository/service methods
  - Catches ALL exceptions internally and returns structured error dicts
  - Validates inputs and truncates outputs to prevent LLM context overflow
  - NEVER raises raw exceptions to callers (tools or otherwise)

Key fix: explore_graph calls repo.get_case_subgraph(), NOT repo.explore_graph()
"""

import logging
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Case, Entity, Relationship, Evidence
from app.graph.age_graph_repository import AgeGraphRepository
from app.analytics.analytics_service import AnalyticsService
from app.services.findings_service import FindingsService

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
MAX_LIST_ITEMS = 50
MAX_NODES = 30
MAX_EDGES = 50
MAX_DEPTH = 5


def _error(code: str, message: str, retryable: bool = False) -> dict:
    """Return a standardised, investigator-safe error payload."""
    return {
        "tool_error": True,
        "code": code,
        "message": message,
        "retryable": retryable,
    }


class InvestigationService:
    """
    Adapter that exposes all tool-facing operations for NETRA investigation.

    All public methods:
      * Validate their inputs before touching the database.
      * Catch every exception and return a structured error dict.
      * Truncate result lists so the LLM context stays bounded.
      * Log the full technical error with logging.error before returning.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Search ───────────────────────────────────────────────────────────────

    def search_cases(self, query: str) -> list:
        """Find cases whose title matches *query* (case-insensitive LIKE)."""
        if not query or not query.strip():
            return _error("INVALID_INPUT", "query must be a non-empty string", retryable=False)
        try:
            cases = (
                self.db.query(Case)
                .filter(Case.title.ilike(f"%{query}%"))
                .limit(MAX_LIST_ITEMS)
                .all()
            )
            return [
                {
                    "case_id": c.case_id,
                    "title": c.title,
                    "description": c.description,
                }
                for c in cases
            ]
        except Exception as exc:
            logger.error("search_cases failed: %s", exc, exc_info=True)
            return _error("DB_ERROR", "Could not search cases at this time.", retryable=True)

    def search_entities(self, query: str) -> list:
        """Resolve investigator-mentioned names to canonical NETRA entities."""
        if not query or not query.strip():
            return _error("INVALID_INPUT", "query must be a non-empty string", retryable=False)
        try:
            entities = (
                self.db.query(Entity)
                .filter(Entity.canonical_name.ilike(f"%{query}%"))
                .limit(MAX_LIST_ITEMS)
                .all()
            )
            return [
                {
                    "entity_id": e.entity_id,
                    "entity_type": e.entity_type,
                    "name": e.canonical_name,
                }
                for e in entities
            ]
        except Exception as exc:
            logger.error("search_entities failed: %s", exc, exc_info=True)
            return _error("DB_ERROR", "Could not search entities at this time.", retryable=True)

    # ── Entity ───────────────────────────────────────────────────────────────

    def get_entity(self, entity_id: str) -> dict:
        """Return canonical entity details for *entity_id*."""
        if not entity_id or not entity_id.strip():
            return _error("INVALID_INPUT", "entity_id must be a non-empty string", retryable=False)
        try:
            e = (
                self.db.query(Entity)
                .filter(Entity.entity_id == entity_id)
                .first()
            )
            if not e:
                return _error("NOT_FOUND", f"Entity '{entity_id}' not found.", retryable=False)
            return {
                "entity_id": e.entity_id,
                "entity_type": e.entity_type,
                "name": e.canonical_name,
            }
        except Exception as exc:
            logger.error("get_entity(%s) failed: %s", entity_id, exc, exc_info=True)
            return _error("DB_ERROR", "Could not retrieve entity at this time.", retryable=True)

    # ── Graph ────────────────────────────────────────────────────────────────

    def explore_graph(self, case_id: str, entity_id: str, depth: int) -> dict:
        """
        Explore the crime network graph centred on *entity_id* within *case_id*.

        Calls AgeGraphRepository.get_case_subgraph() — NOT the non-existent
        repo.explore_graph().  Truncates nodes to MAX_NODES and edges to
        MAX_EDGES to prevent LLM context overflow.
        """
        # Input validation
        if not case_id or not case_id.strip():
            return _error("INVALID_INPUT", "case_id must be a non-empty string", retryable=False)
        if not entity_id or not entity_id.strip():
            return _error("INVALID_INPUT", "entity_id must be a non-empty string", retryable=False)
        if depth is None:
            return _error("INVALID_INPUT", "depth must be provided", retryable=False)
        if not isinstance(depth, int) or depth < 1:
            return _error("INVALID_INPUT", "depth must be a positive integer", retryable=False)
        if depth > MAX_DEPTH:
            return _error(
                "INVALID_INPUT",
                f"depth {depth} exceeds the maximum allowed depth of {MAX_DEPTH}.",
                retryable=False,
            )
        try:
            repo = AgeGraphRepository(self.db, "crime_network")
            # KEY FIX: call get_case_subgraph, not the non-existent explore_graph
            result = repo.get_case_subgraph(case_id, entity_id, depth)

            nodes = result.get("nodes", [])[:MAX_NODES]
            edges = result.get("edges", [])[:MAX_EDGES]

            return {
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges),
            }
        except Exception as exc:
            logger.error(
                "explore_graph(case=%s, entity=%s, depth=%s) failed: %s",
                case_id, entity_id, depth, exc, exc_info=True,
            )
            return _error(
                "GRAPH_ERROR",
                "Could not explore the network graph at this time.",
                retryable=True,
            )

    # ── Relationship ─────────────────────────────────────────────────────────

    def get_relationship(self, relationship_id: str) -> dict:
        """Return details for a CONFIRMED relationship only."""
        if not relationship_id or not relationship_id.strip():
            return _error("INVALID_INPUT", "relationship_id must be a non-empty string", retryable=False)
        try:
            r = (
                self.db.query(Relationship)
                .filter(Relationship.relationship_id == relationship_id)
                .first()
            )
            if not r:
                return _error("NOT_FOUND", f"Relationship '{relationship_id}' not found.", retryable=False)
            status_val = r.status.value if hasattr(r.status, "value") else str(r.status)
            if status_val != "CONFIRMED":
                return _error(
                    "NOT_AUTHORIZED",
                    "Relationship is not authorized for investigation (unconfirmed or rejected).",
                    retryable=False,
                )
            return {
                "relationship_id": r.relationship_id,
                "source_entity_id": r.source_entity_id,
                "target_entity_id": r.target_entity_id,
                "relationship_type": r.relationship_type,
                "status": status_val,
            }
        except Exception as exc:
            logger.error("get_relationship(%s) failed: %s", relationship_id, exc, exc_info=True)
            return _error("DB_ERROR", "Could not retrieve relationship at this time.", retryable=True)

    # ── Findings ─────────────────────────────────────────────────────────────

    def get_findings(self, case_id: str) -> list:
        """Return investigator-facing findings for *case_id*."""
        if not case_id or not case_id.strip():
            return _error("INVALID_INPUT", "case_id must be a non-empty string", retryable=False)
        try:
            svc = FindingsService(self.db)
            findings = svc.get_findings_for_case(case_id)
            return findings[:MAX_LIST_ITEMS]
        except Exception as exc:
            logger.error("get_findings(case=%s) failed: %s", case_id, exc, exc_info=True)
            return _error("DB_ERROR", "Could not retrieve findings at this time.", retryable=True)

    # ── Evidence ─────────────────────────────────────────────────────────────

    def get_evidence(self, evidence_id: str) -> dict:
        """Return evidence metadata and provenance for *evidence_id*."""
        if not evidence_id or not evidence_id.strip():
            return _error("INVALID_INPUT", "evidence_id must be a non-empty string", retryable=False)
        try:
            ev = (
                self.db.query(Evidence)
                .filter(Evidence.evidence_id == evidence_id)
                .first()
            )
            if not ev:
                return _error("NOT_FOUND", f"Evidence '{evidence_id}' not found.", retryable=False)
            return {
                "evidence_id": ev.evidence_id,
                "type": ev.evidence_type,
                "title": ev.title,
                "source": ev.source,
            }
        except Exception as exc:
            logger.error("get_evidence(%s) failed: %s", evidence_id, exc, exc_info=True)
            return _error("DB_ERROR", "Could not retrieve evidence at this time.", retryable=True)

    # ── Analytics ────────────────────────────────────────────────────────────

    def run_network_analysis(self, case_id: str) -> dict:
        """
        Run deterministic network analytics for *case_id*.

        Delegates to AnalyticsService.generate_leads() which computes degree,
        betweenness, cross-case bridges, shared identifiers and financial
        convergence patterns, then persists findings.
        """
        if not case_id or not case_id.strip():
            return _error("INVALID_INPUT", "case_id must be a non-empty string", retryable=False)
        try:
            svc = AnalyticsService(self.db)
            result = svc.generate_leads(case_id=case_id)
            # Truncate lists within the result to keep LLM context bounded
            if isinstance(result, dict):
                for key in ("metrics", "patterns", "leads"):
                    if key in result and isinstance(result[key], list):
                        result[key] = result[key][:MAX_LIST_ITEMS]
            return result
        except Exception as exc:
            logger.error("run_network_analysis(case=%s) failed: %s", case_id, exc, exc_info=True)
            return _error(
                "ANALYTICS_ERROR",
                "Could not run network analysis at this time.",
                retryable=True,
            )


@contextmanager
def get_session():
    """Context manager that yields a SQLAlchemy session and closes it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
