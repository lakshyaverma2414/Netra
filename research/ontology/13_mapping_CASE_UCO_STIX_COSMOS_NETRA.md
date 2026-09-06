# Mapping to Existing Standards

## STIX 2.1
*   **Adopt**: SRO (STIX Relationship Object) pattern for assertions.
*   **Reject**: Cyber-only entity focus.

## CASE / UCO
*   **Adopt**: `Trace`, `Observation`, and `ProvenanceRecord` semantics.
*   **Reject**: Deep forensic file-system level granularity (e.g., NTFS sector mapping is overkill for NETRA's high-level intelligence graph).

## Project COSMOS
*   **Adopt**: Separation of conceptual framework from graph instance; multi-level event modelling.
*   **Reject**: Strict focus purely on cybercrime markets (NETRA needs physical crime like murder/theft too).
