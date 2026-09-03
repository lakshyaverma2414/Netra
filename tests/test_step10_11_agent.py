import pytest
from unittest.mock import patch, MagicMock
from app.agent.workflow import run_investigation
from langchain_core.messages import AIMessage, ToolMessage

def test_agent_initialization():
    # Test just initialization/compilation success
    from app.agent.workflow import app_workflow
    assert app_workflow is not None

@patch('langchain_core.language_models.chat_models.BaseChatModel.invoke')
def test_tool_selection_and_execution(mock_invoke):
    # Mock LLM choosing explore_graph, then giving final answer
    call_count = 0
    def mock_llm_behavior(messages, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Return a tool call
            return AIMessage(
                content="",
                tool_calls=[{
                    "name": "explore_graph",
                    "args": {"case_id": "C-001", "entity_id": "P-001", "depth": 2},
                    "id": "call_1"
                }]
            )
        else:
            return AIMessage(content="P-001 is connected to the network.")
            
    mock_invoke.side_effect = mock_llm_behavior
    
    result = run_investigation("C-001", "Who is P-001 connected to?", "req-123")
    
    assert "P-001 is connected to the network." in result["answer"]
    assert len(result["trace"]) == 1
    assert result["trace"][0]["tool"] == "explore_graph"

@patch('langchain_core.language_models.chat_models.BaseChatModel.invoke')
def test_negative_relationship_ignored(mock_invoke):
    # Verify that get_relationship returns an error if NEEDS_REVIEW is accessed
    # We will invoke the tool directly to test the tool isolation logic
    from app.agent.tools import get_relationship
    from app.db.database import SessionLocal
    from app.db.models import Relationship
    
    db = SessionLocal()
    rel = db.query(Relationship).filter_by(relationship_id="R-BAD-001").first()
    if rel:
        res = get_relationship.invoke({"relationship_id": "R-BAD-001"})
        assert "error" in res
        assert "not authorized" in res["error"]
    db.close()

@patch('langchain_core.language_models.chat_models.BaseChatModel.invoke')
def test_max_depth_enforced(mock_invoke):
    from app.agent.tools import explore_graph
    # Depth 6 should be blocked
    res = explore_graph.invoke({"case_id": "C-001", "entity_id": "P-001", "depth": 6})
    assert "error" in res
    assert "Maximum depth is 5" in res["error"]

@patch('langchain_core.language_models.chat_models.BaseChatModel.invoke')
def test_loop_limit_protection(mock_invoke):
    # If the LLM keeps returning tool calls endlessly
    def mock_infinite_loop(messages, *args, **kwargs):
        return AIMessage(
            content="",
            tool_calls=[{
                "name": "get_entity",
                "args": {"entity_id": "P-001"},
                "id": "call_inf"
            }]
        )
    mock_invoke.side_effect = mock_infinite_loop
    
    result = run_investigation("C-001", "Infinite loop test", "req-loop")
    # LangGraph's recursion_limit is set to 15 in workflow.py
    # So it should throw GraphRecursionError and be caught
    assert "errors" in result
    assert "Investigation stopped due to an error: Recursion limit of 15 reached" in result["answer"] or "error" in result["answer"].lower()
