# NETRA Ontology Architecture & Mapping

## How LLM Output Maps to the Ontology
1.  **LLM Phase**: Qwen outputs a loosely-typed JSON (e.g., `source: "John", target: "Phone X", rel: "USES"`).
2.  **Orchestrator Phase**: The system creates an `Observation` mapping to the text snippet, and a `RelationshipAssertion` marked as `CANDIDATE`.
3.  **Validation Phase**: `validation_service.py` checks `check_ontology("PERSON", "USES", "PHONE")`. 
4.  **Resolution Phase**: The ER engine maps "John" to `Canonical Person E-123` and "Phone X" to `Canonical Phone E-456`.
5.  **Graph Phase**: The canonical relationship is projected into Apache AGE.

**The Golden Rule**: Qwen must be allowed to hallucinate or guess. The Ontology dictates what the Graph will accept. If Qwen outputs `PHONE -> OWNS -> PERSON`, the Validation layer rejects it gracefully without crashing the pipeline.
