"""
test_tool_contracts.py — Tool Contract Tests for NETRA Investigation Agent (Phase A5)

Tests that:
  1. Every tool is callable with valid minimal arguments.
  2. Every tool returns a dict or list (never raises an exception).
  3. Every tool handles invalid/empty arguments gracefully (returns error dict, not exception).
  4. explore_graph with a nonexistent entity_id returns empty nodes, not a crash.

These tests use unittest.mock to patch the database so no live DB is required.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_mock_db():
    """Return a MagicMock that satisfies the SQLAlchemy Session interface."""
    db = MagicMock()
    # Default: queries return empty lists
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
    db.query.return_value.filter.return_value.all.return_value = []
    return db


def make_service(db=None):
    """Return an InvestigationService with a mock db."""
    from app.agent.tool_service import InvestigationService
    return InvestigationService(db or make_mock_db())


# ── search_cases ──────────────────────────────────────────────────────────────

class TestSearchCases:
    def test_valid_query_returns_list(self):
        svc = make_service()
        result = svc.search_cases("robbery")
        assert isinstance(result, list)

    def test_empty_query_returns_error_dict(self):
        svc = make_service()
        result = svc.search_cases("")
        assert isinstance(result, dict)
        assert result.get("tool_error") is True

    def test_whitespace_query_returns_error_dict(self):
        svc = make_service()
        result = svc.search_cases("   ")
        assert isinstance(result, dict)
        assert result.get("tool_error") is True

    def test_db_exception_returns_error_dict(self):
        db = make_mock_db()
        db.query.side_effect = Exception("DB connection lost")
        svc = make_service(db)
        result = svc.search_cases("test")
        assert isinstance(result, dict)
        assert result.get("tool_error") is True
        assert result.get("retryable") is True


# ── search_entities ───────────────────────────────────────────────────────────

class TestSearchEntities:
    def test_valid_query_returns_list(self):
        svc = make_service()
        result = svc.search_entities("Ahmed")
        assert isinstance(result, list)

    def test_empty_query_returns_error_dict(self):
        svc = make_service()
        result = svc.search_entities("")
        assert isinstance(result, dict)
        assert result.get("tool_error") is True


# ── get_entity ────────────────────────────────────────────────────────────────

class TestGetEntity:
    def test_nonexistent_entity_returns_not_found_error(self):
        svc = make_service()  # db returns None for first()
        result = svc.get_entity("nonexistent_id")
        assert isinstance(result, dict)
        assert result.get("tool_error") is True
        assert result.get("code") == "NOT_FOUND"

    def test_empty_entity_id_returns_error_dict(self):
        svc = make_service()
        result = svc.get_entity("")
        assert isinstance(result, dict)
        assert result.get("tool_error") is True

    def test_found_entity_returns_expected_keys(self):
        mock_entity = MagicMock()
        mock_entity.entity_id = "ent_001"
        mock_entity.entity_type = "PERSON"
        mock_entity.canonical_name = "John Doe"
        db = make_mock_db()
        db.query.return_value.filter.return_value.first.return_value = mock_entity
        svc = make_service(db)
        result = svc.get_entity("ent_001")
        assert isinstance(result, dict)
        assert result["entity_id"] == "ent_001"
        assert "tool_error" not in result


# ── explore_graph ─────────────────────────────────────────────────────────────

class TestExploreGraph:
    def _make_repo_mock(self, nodes=None, edges=None):
        """Patch AgeGraphRepository so no DB connection is needed."""
        mock_repo = MagicMock()
        mock_repo.get_case_subgraph.return_value = {
            "nodes": nodes or [],
            "edges": edges or [],
        }
        return mock_repo

    def test_nonexistent_entity_returns_empty_nodes_not_crash(self):
        """explore_graph with a nonexistent entity should return empty nodes, not crash."""
        with patch("app.agent.tool_service.AgeGraphRepository") as MockRepo:
            MockRepo.return_value = self._make_repo_mock(nodes=[], edges=[])
            svc = make_service()
            result = svc.explore_graph("C-001", "nonexistent_ent", 1)
        assert isinstance(result, dict)
        assert "tool_error" not in result
        assert result["nodes"] == []
        assert result["edges"] == []
        assert result["node_count"] == 0

    def test_valid_call_uses_get_case_subgraph_not_explore_graph(self):
        """Verify the fix: get_case_subgraph is called, not explore_graph."""
        with patch("app.agent.tool_service.AgeGraphRepository") as MockRepo:
            mock_repo_inst = self._make_repo_mock()
            MockRepo.return_value = mock_repo_inst
            svc = make_service()
            svc.explore_graph("C-001", "ent_001", 2)
        mock_repo_inst.get_case_subgraph.assert_called_once_with("C-001", "ent_001", 2)
        # Verify the old broken method was never called
        mock_repo_inst.explore_graph.assert_not_called()

    def test_depth_exceeds_max_returns_error(self):
        svc = make_service()
        result = svc.explore_graph("C-001", "ent_001", 10)
        assert isinstance(result, dict)
        assert result.get("tool_error") is True
        assert result.get("code") == "INVALID_INPUT"

    def test_empty_case_id_returns_error(self):
        svc = make_service()
        result = svc.explore_graph("", "ent_001", 1)
        assert isinstance(result, dict)
        assert result.get("tool_error") is True

    def test_empty_entity_id_returns_error(self):
        svc = make_service()
        result = svc.explore_graph("C-001", "", 1)
        assert isinstance(result, dict)
        assert result.get("tool_error") is True

    def test_null_depth_returns_error(self):
        svc = make_service()
        result = svc.explore_graph("C-001", "ent_001", None)
        assert isinstance(result, dict)
        assert result.get("tool_error") is True

    def test_repo_exception_returns_error_dict_not_crash(self):
        with patch("app.agent.tool_service.AgeGraphRepository") as MockRepo:
            MockRepo.return_value.get_case_subgraph.side_effect = Exception("AGE graph unreachable")
            svc = make_service()
            result = svc.explore_graph("C-001", "ent_001", 1)
        assert isinstance(result, dict)
        assert result.get("tool_error") is True
        assert result.get("retryable") is True

    def test_result_truncated_to_limits(self):
        """Nodes truncated to 30, edges to 50."""
        big_nodes = [{"data": {"id": f"n{i}"}} for i in range(100)]
        big_edges = [{"data": {"id": f"e{i}", "relationship_id": f"e{i}"}} for i in range(200)]
        with patch("app.agent.tool_service.AgeGraphRepository") as MockRepo:
            MockRepo.return_value = self._make_repo_mock(nodes=big_nodes, edges=big_edges)
            svc = make_service()
            result = svc.explore_graph("C-001", "ent_001", 1)
        assert result["node_count"] <= 30
        assert result["edge_count"] <= 50


# ── get_relationship ──────────────────────────────────────────────────────────

class TestGetRelationship:
    def test_nonexistent_returns_error(self):
        svc = make_service()
        result = svc.get_relationship("rel_nonexistent")
        assert isinstance(result, dict)
        assert result.get("tool_error") is True

    def test_unconfirmed_relationship_is_blocked(self):
        mock_rel = MagicMock()
        mock_rel.relationship_id = "rel_001"
        mock_rel.status.value = "NEEDS_REVIEW"
        db = make_mock_db()
        db.query.return_value.filter.return_value.first.return_value = mock_rel
        svc = make_service(db)
        result = svc.get_relationship("rel_001")
        assert result.get("tool_error") is True
        assert result.get("code") == "NOT_AUTHORIZED"

    def test_confirmed_relationship_returns_data(self):
        mock_rel = MagicMock()
        mock_rel.relationship_id = "rel_001"
        mock_rel.source_entity_id = "ent_001"
        mock_rel.target_entity_id = "ent_002"
        mock_rel.relationship_type = "CALLS"
        mock_rel.status.value = "CONFIRMED"
        db = make_mock_db()
        db.query.return_value.filter.return_value.first.return_value = mock_rel
        svc = make_service(db)
        result = svc.get_relationship("rel_001")
        assert isinstance(result, dict)
        assert "tool_error" not in result
        assert result["status"] == "CONFIRMED"

    def test_empty_id_returns_error(self):
        svc = make_service()
        result = svc.get_relationship("")
        assert result.get("tool_error") is True


# ── get_findings ──────────────────────────────────────────────────────────────

class TestGetFindings:
    def test_valid_case_returns_list(self):
        with patch("app.agent.tool_service.FindingsService") as MockSvc:
            MockSvc.return_value.get_findings_for_case.return_value = []
            svc = make_service()
            result = svc.get_findings("C-001")
        assert isinstance(result, list)

    def test_empty_case_id_returns_error(self):
        svc = make_service()
        result = svc.get_findings("")
        assert result.get("tool_error") is True

    def test_service_exception_returns_error_dict(self):
        with patch("app.agent.tool_service.FindingsService") as MockSvc:
            MockSvc.return_value.get_findings_for_case.side_effect = Exception("DB error")
            svc = make_service()
            result = svc.get_findings("C-001")
        assert result.get("tool_error") is True
        assert result.get("retryable") is True


# ── get_evidence ──────────────────────────────────────────────────────────────

class TestGetEvidence:
    def test_nonexistent_returns_error(self):
        svc = make_service()
        result = svc.get_evidence("ev_nonexistent")
        assert result.get("tool_error") is True
        assert result.get("code") == "NOT_FOUND"

    def test_empty_id_returns_error(self):
        svc = make_service()
        result = svc.get_evidence("")
        assert result.get("tool_error") is True


# ── run_network_analysis ──────────────────────────────────────────────────────

class TestRunNetworkAnalysis:
    def test_valid_case_returns_dict(self):
        with patch("app.agent.tool_service.AnalyticsService") as MockSvc:
            MockSvc.return_value.generate_leads.return_value = {
                "case_id": "C-001",
                "entities_analyzed": 0,
                "metrics": [],
                "patterns": [],
                "leads": [],
            }
            svc = make_service()
            result = svc.run_network_analysis("C-001")
        assert isinstance(result, dict)
        assert "tool_error" not in result

    def test_empty_case_id_returns_error(self):
        svc = make_service()
        result = svc.run_network_analysis("")
        assert result.get("tool_error") is True

    def test_analytics_exception_returns_error_dict(self):
        with patch("app.agent.tool_service.AnalyticsService") as MockSvc:
            MockSvc.return_value.generate_leads.side_effect = Exception("NetworkX error")
            svc = make_service()
            result = svc.run_network_analysis("C-001")
        assert result.get("tool_error") is True
        assert result.get("retryable") is True


# ── Tool callable contracts (LangChain @tool wrappers) ────────────────────────

class TestToolCallable:
    """Verify that each @tool decorated function exists and is callable."""

    def test_all_tools_are_callable(self):
        from app.agent.tools import get_all_tools
        tools = get_all_tools()
        assert len(tools) == 8
        for t in tools:
            # LangChain StructuredTool uses .invoke() rather than Python's callable()
            assert hasattr(t, "invoke"), f"Tool {t} does not have an invoke method"

    def test_tool_names_unchanged(self):
        from app.agent.tools import get_all_tools
        expected_names = {
            "search_cases", "search_entities", "get_entity", "explore_graph",
            "get_relationship", "get_findings", "get_evidence", "run_network_analysis",
        }
        tools = get_all_tools()
        actual_names = {t.name for t in tools}
        assert actual_names == expected_names
