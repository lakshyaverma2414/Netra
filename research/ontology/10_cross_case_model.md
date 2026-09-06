# Cross-Case Model

## Global Entities vs Local Context
*   **Canonical Entities** are GLOBAL. "Ravi Kumar (9876543210)" exists once in the graph.
*   **Cases** are CONTEXTS. Case A and Case B are investigative boundaries.
*   **Case-Entity Linkage**: A Canonical Entity participates in a Case via a `case_entities` mapping, which includes the `role` (Suspect, Victim, Witness) specific to that case.

## Identity Resolution
A Phone Number "9876543210" in Case A and Case B must resolve to the SAME Canonical Digital Identifier. The system must not assume isolation. Ambiguity (e.g., two people using the same phone) is handled by linking the single Phone entity to two Person entities via `USES`, rather than creating two Phone entities.
