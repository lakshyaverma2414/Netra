# Case Linkage Model

## How Cases Connect
1.  **Shared Entities**: The most common linkage. (e.g., The same bank account appears in Case A and Case B).
2.  **Shared MO (Modus Operandi)**: Similar Event Patterns. (e.g., Case A and Case B both feature a CyberAction of type 'Phishing' using infrastructure 'XYZ').
3.  **Hierarchical Cases**: An overarching investigation (Operation X) containing sub-cases (FIR 1, FIR 2).

## Ontology Representation
`CASE` is modeled as a specialized `INVESTIGATION` entity that can have relationships like `RELATED_TO`, `SUB_CASE_OF`, and `SHARES_MO_WITH`.
