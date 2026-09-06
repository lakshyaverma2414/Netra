# Identity Semantics & Cross-Case Resolution

## Identity Links vs Usage Links
The ontology requires precise differentiation between identity equivalence and mere association:
*   `SAME_AS`: Entity A and Entity B refer to the exact same real-world entity.
*   `POSSIBLY_SAME_AS`: Algorithmic/heuristic similarity requiring human review.
*   `ALIAS_OF`: Alternate naming for an entity.
*   `USED_BY` / `REGISTERED_TO`: Association to an identifier or asset.

## Identifiers as Pivots, Not Conclusions
An exact identifier match (e.g., `PHONE-123`) is a **strong candidate linkage pivot**, not an automatic identity conclusion.
If Person A and Person B both connect to `PHONE-123` via `USED_BY`, it may indicate:
*   They are the same person at different times.
*   It is a shared/organizational phone.
*   It is a recycled number.
The ontology captures the `USED_BY` linkage, leaving the `SAME_AS` inference to analytic/validation logic.
