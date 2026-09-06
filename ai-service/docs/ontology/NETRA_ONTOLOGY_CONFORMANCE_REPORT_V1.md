# NETRA Ontology Conformance Report V1

## 1. Ontology Coverage
*   **Version:** 1.1.0
*   **Entities:** 18
*   **Events:** 6
*   **Relationships:** 15
*   **Provenance Classes:** 8

## 2. Audit Findings & Upgrades
*   **INVOLVED_IN vs AFFILIATED_WITH:** `INVOLVED_IN` is retained for generic Event participation. `AFFILIATED_WITH`, `EMPLOYED_BY`, and `MEMBER_OF` handle Actor-Organization links distinctly.
*   **LOCATED_AT vs OCCURRED_AT:** Event locations are now `OCCURRED_AT`. Entity physical presence is `LOCATED_AT`.
*   **OWNS Constraint:** `OWNS` is constrained to Property, Asset, DigitalAsset, Vehicle, Account, Organization. (Location is removed).
*   **Identity Semantics:** `SAME_AS` is fully symmetric and transitive, but assertions of `SAME_AS` must be `CONFIRMED` to affect the Canonical KG. Identifiers (`USED_BY`) are strictly asymmetric.
*   **Provenance Chain:** Models cover the full lifecycle: `SourceRecord -> DerivedArtifact -> Observation -> Assertion -> Canonical Edge`.

## 3. Ontology Self-Validation Results
*   **Status:** PASS
*   **Errors Found:** 0

## 4. Final Recommendation
**Status: READY_FOR_INTEGRATION**
The ontology is semantically complete, internally coherent, and verified.
