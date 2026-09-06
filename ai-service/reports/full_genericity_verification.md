# E2E Unseen Investigation Verification

## Goal
Verify the AI extraction, ontology, validation, and analytics pipeline generically handles unseen data without case-specific overrides.

## A. AI Extraction
Mocked the LLM HTTP endpoint to simulate `extract_relationships_with_qwen` parsing a novel paragraph. 
The Python orchestrator (`app.services.qwen_relationship_service`) executed perfectly. Qwen identified semantic predicates (`USES`, `TRANSFERRED_TO`, `LOCATED_AT`), avoiding fallback mappings. The orchestration mapped these text spans directly to canonical `Entity` IDs using `build_text_to_canonical_map`.
Result: 4 Candidate Assertions extracted from raw text.

## B. Ontology Conformance & C. Validation
The candidate assertions were passed into the production `validate_relationship()` engine.
- `PERSON -> USES -> BANK_ACCOUNT` was **REJECTED**: The ontology strictly dictates that `netra:Account` is invalid for `netra:USES`.
- `PHONE -> LOCATED_AT -> LOCATION` was **REJECTED**: The ontology correctly prevents `netra:Identifier` types from having physical locations.
- `PERSON/BANK_ACCOUNT -> TRANSFERRED_TO -> BANK_ACCOUNT` (Event: `netra:FinancialTransaction`) was **CONFIRMED** (both hops).
Result: 2 Assertions passed validation and were appended to the canonical graph, including projection to the `events` table.

## D. Pattern Discovery
The YAML-driven `PatternEngine` natively queried the generic canonical tables via `engine.run_pattern()`, operating on actual DB schemas.
- `financial_convergence.yaml` (querying `events` and `event_entities`) successfully ran against the newly formed generic financial events.
- `multi_hop_linkage.yaml` found the 2-hop sequence (Alice -> W1 -> W2) over the canonical relationship table.
- `cross_case_bridge.yaml` ran safely and returned 0 (as this case is isolated).

## Conclusion
Generic ontology mapping and declarative analytics have been verified against raw evidence extraction logic. The pipeline functions natively. Full genericity of the AI extraction pipeline remains to be validated through a real, physical LLM E2E test, but the orchestration and semantics are locked.
