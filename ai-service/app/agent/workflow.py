from app.config import config
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.agent.state import InvestigationState
from app.agent.tools import get_all_tools
from app.agent.prompts import SYSTEM_PROMPT
import json
import logging

from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres"
pool = ConnectionPool(conninfo=DB_URI, max_size=10, kwargs={"autocommit": True})
checkpointer = PostgresSaver(pool)
checkpointer.setup()


logger = logging.getLogger(__name__)

tools = get_all_tools()
tool_node = ToolNode(tools)

# Use Qwen compatible OpenAI endpoint, or fallback to a mock/mock-endpoint for tests
llm = ChatOpenAI(
    base_url=f"{config.QWEN_BASE_URL}/v1",
    api_key="sk-no-key",
    model="qwen"
)
llm_with_tools = llm.bind_tools(tools)

def interpret_query(state: InvestigationState) -> InvestigationState:
    messages = state.get("messages", [])
    new_message = HumanMessage(content=f"Case: {state.get('case_id')}\nQuestion: {state.get('question')}")
    
    if not messages:
        return {"messages": [SystemMessage(content=SYSTEM_PROMPT), new_message]}
    else:
        return {"messages": [new_message]}

def call_model(state: InvestigationState) -> dict:
    messages = state["messages"]
    try:
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"LLM Error: {e}", exc_info=True)
        # Return a safe message — do NOT expose the raw Python exception to the investigator
        from langchain_core.messages import AIMessage
        return {
            "messages": [AIMessage(content="[UNKNOWN] The reasoning engine is temporarily unavailable. I could not complete this investigation step.")],
            "errors": ["LLM engine error. Details have been logged."]
        }


def should_continue(state: InvestigationState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check for loop limits
    # LangGraph does this automatically if recursion_limit is set, but we can also manually check
    tool_calls = [m for m in messages if hasattr(m, 'tool_calls') and m.tool_calls]
    if len(tool_calls) > 12:
        return "__end__"
        
    # If the LLM makes a tool call, we transition to the "tools" node
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # Otherwise, it has produced a final response
    return "__end__"

workflow = StateGraph(InvestigationState)
workflow.add_node("interpret_query", interpret_query)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "interpret_query")
workflow.add_edge("interpret_query", "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app_workflow = workflow.compile(checkpointer=checkpointer)

def run_investigation(case_id: str, question: str, request_id: str, thread_id: str = None) -> dict:
    if not thread_id:
        import uuid
        thread_id = str(uuid.uuid4())
        
    initial_state = {
        "request_id": request_id,
        "case_id": case_id,
        "question": question,
        "errors": []
    }
    
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 15
    }
    
    # Run graph with recursion limit
    try:
        result = app_workflow.invoke(initial_state, config)
        final_message = result["messages"][-1].content
        
        # Extract trace metadata (the tool calls made)
        trace = []
        for msg in result["messages"]:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    trace.append({
                        "tool": tc['name'],
                        "arguments": tc['args']
                    })
            if hasattr(msg, 'name') and msg.type == 'tool':
                # this is a tool result message
                # we don't output the full result to trace to keep it clean, just that it succeeded
                pass
                
        return {
            "request_id": request_id,
            "thread_id": thread_id,
            "answer": final_message,
            "trace": trace,
            "errors": result.get("errors", [])
        }
    except Exception as e:
        logger.error("run_investigation fatal error (request_id=%s): %s", request_id, e, exc_info=True)
        return {
            "request_id": request_id,
            "thread_id": thread_id,
            "answer": "The investigation encountered a technical issue. Please try again or contact your system administrator.",
            "trace": [],
            "errors": ["A technical error occurred. Details have been logged."]
        }

