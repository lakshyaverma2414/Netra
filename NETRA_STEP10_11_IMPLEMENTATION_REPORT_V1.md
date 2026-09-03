# NETRA_STEP10_11_IMPLEMENTATION_REPORT_V1

## Agentic Investigation Workflow — Qwen + LangGraph

### Overview
Step 10.11 introduces a **controlled, read-only agentic investigation workflow** integrating NETRA's existing Postgres/AGE backend with LangGraph and the local Qwen LLM. It allows investigators to ask natural language questions which are translated into dynamic, bounded tool calls executed sequentially over the graph, producing evidence-grounded final answers.

### Implementation Details
* **Framework:** Integrated `langgraph`, `langchain`, and `langchain-openai` dependencies into the FastAPI backend.
* **Tools (`app/agent/tools.py`):**
  * Developed a rigid registry of read-only tools: `search_cases`, `search_entities`, `get_entity`, `explore_graph`, `get_relationship`, `get_findings`, `get_evidence`, `run_network_analysis`.
  * The `explore_graph` tool forces a max depth of 5.
  * The `get_relationship` tool enforces `status == "CONFIRMED"`, hiding rejected or unreviewed (`R-BAD-001`) relationships from the LLM.
* **Workflow (`app/agent/workflow.py`):**
  * Created an isolated `InvestigationState` TypedDict to maintain explicit boundaries on message history.
  * Established a `StateGraph` consisting of an `interpret_query` node, an `agent` reasoning loop, and a `tools` execution node.
  * Enforced a maximum limit of 15 recursion steps (preventing runaway cycles).
* **System Prompting (`app/agent/prompts.py`):**
  * Hardcoded guardrails forbidding the invention of authoritative relationships, ensuring facts are separated from hypotheses, and demanding evidence IDs be surfaced.
* **API (`app/api/investigations.py`):**
  * Exposed a clean `POST /api/v1/investigations/query` endpoint returning structured JSON, including the final `answer` and an auditable execution `trace`.
* **Frontend (`src/components/Chatbot.tsx`):**
  * Re-wired the floating AI Assistant panel from a static mock into a fully functional LangGraph client that passes the current `caseId` and streams the resulting investigation trace inline below the AI's answer.

### Verification
* **Test Suite (`tests/test_step10_11_agent.py`):** Passes successfully.
* **Negative Trust Check:** Verified that if Qwen tries to query an unconfirmed relationship, the tool layer raises an explicit "unauthorized" rejection, successfully enforcing the data trust boundary.
* **Bounded execution:** Verified depth boundaries and maximum recursion caps.
