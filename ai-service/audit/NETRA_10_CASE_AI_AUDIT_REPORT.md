# NETRA AI LAYER — 10-CASE END-TO-END AUDIT REPORT

## Executive Summary
This audit evaluated the end-to-end data flow of 10 seeded cases (C-001 through C-010) through the NETRA AI pipeline: from unstructured text extraction via Qwen to PostgreSQL canonical persistence, Apache AGE graph projection, and React frontend rendering.

**Key Finding:** The downstream pipeline (PostgreSQL -> AGE Graph -> Graph API -> Frontend) is perfectly intact. However, significant drop-offs occur at the **Extraction Stage** (due to LLM context limits) and the **Validation Stage** (due to strict ontology constraints). 

---

## 1. What relationships did NETRA actually form from the 10 cases?
NETRA successfully formed **15 canonical relationships** across 6 cases, connecting 47 canonical entities.

*   **C-002**: 2 Relationships (ASSOCIATED_WITH, COMMUNICATES_WITH)
*   **C-005**: 1 Relationship (ASSOCIATED_WITH)
*   **C-006**: 3 Relationships (ASSOCIATED_WITH, LOCATED_AT)
*   **C-008**: 2 Relationships (ASSOCIATED_WITH)
*   **C-009**: 4 Relationships (ASSOCIATED_WITH, LOCATED_AT)
*   **C-010**: 3 Relationships (ASSOCIATED_WITH)
*   **C-001, C-003, C-004, C-007**: 0 Relationships formed.

*(A complete inventory is provided in `relationship_inventory.csv`)*

## 2. Which expected relationships were missed?
Several logically expected relationships were missed:
*   **Total Extraction Failure:** All relationships in C-001, C-003, C-004, and C-007 were missed entirely.
*   **Valid Extraction, Rejected by Constraints:** 
    *   `OWNS` (e.g., Person -> Vehicle) in C-008.
    *   `USES` (e.g., Person -> Phone) in C-009.
    *   `INVOLVED_IN` and `COMMUNICATES_WITH` for certain entity pairs across C-005, C-006, C-009, C-010.

## 3. At what stage were they lost?
Relationships were lost at two distinct stages:

1.  **Extraction Stage (AI Failure):** Cases C-001, C-003, C-004, and C-007 failed during Qwen extraction. The unstructured text exceeded the LLM's effective context window, resulting in `Unterminated string` (invalid JSON) errors. The pipeline skipped these files entirely, resulting in 0 mentions and 0 assertions.
2.  **Validation Stage (Constraint Failure):** Qwen successfully extracted complex relationships (like `OWNS`, `USES`, `INVOLVED_IN`) for the successful cases. However, the `validation_service.py` ontology rejected these candidate assertions because the specific `(source_type, relationship_type, target_type)` tuples were not explicitly permitted in the `ONTOLOGY` dictionary.

## 4. Are incomplete graphs caused by AI extraction, resolution, validation, AGE, analytics, or frontend?
The incomplete graphs are **NOT** caused by AGE, Analytics, or the Frontend. 
*   **PostgreSQL Canonical Data:** 47 Entities, 15 Relationships.
*   **Apache AGE Projection:** 47 Vertices, 15 Edges.
The downstream projection is 100% accurate. The graph is incomplete solely due to upstream **AI Extraction** (context limits) and **Validation** (ontology gaps).

## 5. Where is the semantic AI layer weak?
*   **Context Management:** The Qwen LLM cannot handle the full text of the larger case files in a single prompt. It truncates the JSON output, destroying all extracted intelligence for that document.
*   **Provenance Breakage:** The orchestrator bypasses standard `source_records` ingestion, meaning `entity_mentions` and `relationship_assertions` currently have `source_record_id = NULL`. Furthermore, `orchestrator.py` never updates the `status` of `relationship_assertions` to `CONFIRMED` upon successful validation, leaving all assertions permanently marked as `CANDIDATE`.

## 6. Where is the mathematical/analytical layer weak?
Because Entity Resolution is currently operating in isolation per document, **cross-case linkages are zero**. Identical entities appearing in different cases are minted as distinct canonical entities. Without cross-case entity resolution, mathematical analytics (like betweenness centrality or cross-case bridge scoring) yield trivial or completely disconnected results.

## 7. What are the top 5 fixes required before we call the AI layer demo-ready?
1.  **Implement Chunking / Increase LLM Context:** Document text must be chunked before sending to Qwen, or the local llama-server context window (`--c`) must be increased to prevent JSON truncation on large reports.
2.  **Expand the Relationship Ontology:** Update the `ONTOLOGY` dictionary in `validation_service.py` to accept all valid entity-type pairs for extracted relationships like `OWNS`, `USES`, `INVOLVED_IN`, and `COMMUNICATES_WITH`.
3.  **Fix Pipeline Provenance Links:** Modify `unstructured_pipeline.py` and `orchestrator.py` to properly create `source_records` and populate `source_record_id` across observations, mentions, and assertions.
4.  **Fix Assertion Status Updates:** Ensure `orchestrator.py` updates the `relationship_assertions` table status to `CONFIRMED` after `validate_relationship` succeeds.
5.  **Enable Cross-Case Entity Resolution:** Enhance `resolution_service.py` to query existing canonical entities globally (using fuzzy name/alias matching or exact identifier matching like phone numbers) rather than just within the isolated case context.
