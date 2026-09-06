# NETRA AI LAYER — FORENSIC AUDIT V2

## 1. Executive Summary
This second forensic audit delves deeper into the exact root causes of missing relationships across the 10-case corpus. By explicitly differentiating between LLM extraction candidates and canonical relationships, we have diagnosed the specific constraints blocking Intelligence formation. 

**Key Conclusion:** The AI layer (Qwen) is successfully extracting many valid relationships, but a rigid `validation_service.py` ontology combined with entity-type mapping mismatches is rejecting them. Additionally, cross-case entity resolution is entirely inactive, resulting in zero global graph connectedness.

---

## 2. 10-Case Data Inventory & Relationship Funnel
The transition from LLM Candidate to Canonical Edge demonstrates significant drop-off:

| Case_ID | LLM Assertions Created | Validation Pass (Canonical) | Validation Failed | AGE Edges |
|---|---|---|---|---|
| C-001 | 0 | 0 | 0 | 0 |
| C-002 | 4 | 2 | 2 | 2 |
| C-003 | 0 | 0 | 0 | 0 |
| C-004 | 0 | 0 | 0 | 0 |
| C-005 | 3 | 1 | 2 | 1 |
| C-006 | 5 | 3 | 2 | 3 |
| C-007 | 0 | 0 | 0 | 0 |
| C-008 | 5 | 2 | 3 | 2 |
| C-009 | 8 | 4 | 4 | 4 |
| C-010 | 4 | 3 | 1 | 3 |

*(See `relationship_funnel.csv` for complete metrics)*

---

## 3. Zero-Relationship Case Diagnosis (C-001, C-003, C-004, C-007)
These 4 cases failed entirely at the first step.
*   **Evidence Exists?** YES
*   **Processing Run:** YES (Failed)
*   **Qwen Invoked?** YES
*   **Exception:** LLM Context Window Overflow. 
*   **Root Cause:** The raw document text is passed to Qwen in a single prompt. For these specific files, the text length exceeded the configured context limit, causing Qwen to stream an incomplete JSON string (`Unterminated string`). The orchestrator crashed on `json.loads()`, creating 0 mentions and 0 assertions.

*(See `zero_case_diagnosis.csv` for full diagnosis)*

---

## 4. Validation Failure Analysis & Ontology Coverage
For cases where Qwen successfully extracted assertions, many were rejected. The current `ONTOLOGY` dictionary strictly enforces rules like:
*   `OWNS`: `PERSON` -> `[VEHICLE, BANK_ACCOUNT, UPI_ID, ORGANIZATION, PHONE, LOCATION]`
*   `COMMUNICATES_WITH`: `PERSON` -> `PERSON` or `PHONE` -> `PHONE`
*   `INVOLVED_IN`: `PERSON` -> `[EVENT, ORGANIZATION, LOCATION]`

### Why did candidates fail?
An analysis of `validation_failure_reasons.csv` reveals the rejects are largely due to **Target/Source Type Mismatches** (a combination of rigid ontology and loose Entity Resolution):
*   **C-008 (OWNS):** `ORGANIZATION -> ORGANIZATION` was rejected because the ontology only allows `PERSON` to own an `ORGANIZATION`. In reality, parent companies own subsidiaries.
*   **C-008 (COMMUNICATES_WITH):** `ORGANIZATION -> ORGANIZATION` was rejected because the ontology only allows `PERSON -> PERSON`.
*   **C-005 (INVOLVED_IN):** `PERSON -> PERSON` rejected (Ontology expects Person -> Event).
*   **C-006 (LOCATED_AT):** `ORGANIZATION -> LOCATION` rejected (Ontology only allows Person/Vehicle/Phone -> Location).

**Diagnosis:** The LLM is correctly identifying real-world facts (e.g., Company A owns Company B, Company C is located at City D), but the validation service is killing them because the ontology is too narrow.

*(See `ontology_coverage.csv` and `validation_failure_reasons.csv`)*

---

## 5. Provenance Audit
Provenance mapping is currently broken:
*   **Linkage Issue:** `orchestrator.py` instantiates `RelationshipAssertion` and `Observation` objects but fails to properly link `source_record_id` to the underlying `evidence_id`. 
*   **State Issue:** When a relationship successfully passes validation, `orchestrator.py` creates a `Relationship` record, but **forgets to update the `RelationshipAssertion` status**. Thus, all assertions remain permanently marked as `CANDIDATE`.

*(See `provenance_completeness.csv`)*

---

## 6. PostgreSQL → AGE Consistency
**Status: Perfect.** 
The data that survives validation successfully persists to PostgreSQL (47 entities, 15 relationships) and perfectly synchronizes to the Apache AGE graph (47 vertices, 15 edges). This boundary is entirely stable.

---

## 7. Cross-Case Resolution Audit
**Score:** 0 cross-case entities. 0 multi-hop paths across cases.
*   **Diagnosis:** `resolution_service.py` currently executes entity resolution strictly within the context of the active `case_id`. 
*   **Impact:** If "Vikram Singh" (Phone: 9876543210) appears in Case A and Case B, the system mints two completely distinct canonical entities (`E-111` and `E-222`). This entirely defeats the purpose of the network graph layer.

*(See `cross_case_resolution.csv`)*

---

## 8. Mathematical Layer Audit
The mathematical layer (NetworkX algorithms) relies on graph structure.
*   **Degree / Betweenness Centrality:** Operates correctly on individual case subgraphs.
*   **Cross-Case Bridge Scores:** Fails completely because the graph is fully disconnected. The highest possible score is currently 0.
*   **Recommendation:** Do not tune or trust mathematical anomalies until Cross-Case Entity Resolution is enabled. Graph mathematics are useless on fragmented data.

*(See `math_analytics_audit.csv`)*

---

## 9. AI Failure Taxonomy
| Failure Type | Count / Impact | Responsibility Area |
|---|---|---|
| **JSON Truncation** | 4 entire cases | `Qwen Context Management` |
| **Ontology Rejection** | ~14 valid assertions | `validation_service.py` |
| **Provenance Breakage** | 100% of assertions | `orchestrator.py` |
| **Graph Fragmentation** | 100% of cross-case links | `resolution_service.py` |

---

## 10. Root Causes & Recommended Fixes

1.  **DATA/PARSING:** Chunk the unstructured document text inside `unstructured_pipeline.py` before passing it to Qwen, or vastly increase the local Llama server `--c` context limit.
2.  **ONTOLOGY:** Expand the `ONTOLOGY` dictionary. At minimum, add:
    *   `OWNS`: `ORGANIZATION -> ORGANIZATION`
    *   `LOCATED_AT`: `ORGANIZATION -> LOCATION`
    *   `COMMUNICATES_WITH`: `ORGANIZATION -> ORGANIZATION`
3.  **PROVENANCE:** Fix `orchestrator.py` to correctly map `source_record_id` and explicitly execute `assertion.status = CONFIRMED` after validation.
4.  **ENTITY RESOLUTION:** Modify the resolution logic to run a global similarity search against *all* canonical entities, not just `WHERE case_id = current_case`. Use strict identifiers (phones, UPIs, emails) for automatic cross-case merging. 
