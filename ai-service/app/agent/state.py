from typing import TypedDict, List, Dict, Any, Annotated, Optional
import operator

def merge_lists(a: list, b: list) -> list:
    if not a: return b
    if not b: return a
    return a + b

class InvestigationState(TypedDict):
    request_id: str
    investigator_id: Optional[str]
    case_id: str
    question: str

    # Message history for LangGraph (holds AIMessage, HumanMessage, ToolMessage)
    messages: Annotated[List[Any], merge_lists]
    
    # Internal agent memory to enforce isolation and prevent unbounded querying
    identified_entities: Annotated[List[Dict], merge_lists]
    identified_cases: Annotated[List[Dict], merge_lists]
    
    # Accumulated context for final answer
    relationships: Annotated[List[Dict], merge_lists]
    paths: Annotated[List[Dict], merge_lists]
    findings: Annotated[List[Dict], merge_lists]
    evidence: Annotated[List[Dict], merge_lists]
    analysis_results: Annotated[List[Dict], merge_lists]
    
    # Simple structured outputs
    reasoning_context: str
    final_answer: str
    errors: Annotated[List[str], merge_lists]
