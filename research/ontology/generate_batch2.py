import os

BASE_DIR = "/mnt/d/NETRA/SIH2026/research/ontology"

def write_md(name, content):
    with open(os.path.join(BASE_DIR, name), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 7. 07_evidence_provenance_model.md
write_md("07_evidence_provenance_model.md", """
# Evidence and Provenance Model

## Concept
Following NIST's CASE-Corpora and W3C PROV-O, NETRA must distinguish between a physical/digital artifact (Evidence) and the extraction of intelligence from it (Observation -> Assertion).

## The Provenance Chain
1.  **SourceRecord (Trace/Artifact)**: The physical phone, the hard drive, or the FIR document.
2.  **DerivedArtifact**: A forensic image, a PDF translation, or an OCR output.
3.  **Observation**: The LLM parsing a specific sentence.
4.  **Assertion**: The claim that "Person A OWNS Vehicle B".
5.  **Canonical Relationship**: The accepted fact in the KG.

## Attributes Required
Every Assertion must carry:
*   `extraction_method` (e.g., Qwen-72B, Manual Entry)
*   `confidence` (Extraction heuristic score)
*   `observation_id` (Link to the raw text snippet)
*   `source_record_id` (Link to the root Evidence)
""")

# 8. 08_temporal_model.md
write_md("08_temporal_model.md", """
# Temporal Model

## Investigative Time is Not One-Dimensional
NETRA must model different temporal semantics:
*   **occurred_at**: When the real-world event happened (e.g., the murder). Often an interval (`start_time`, `end_time`) or bounded (`before_date`, `after_date`).
*   **observed_at**: When a sensor or witness recorded it (e.g., CDR log timestamp).
*   **reported_at**: When it entered the official system (e.g., FIR filing date).
*   **valid_from / valid_to**: For relationships (e.g., Person A owned Vehicle B from 2020 to 2024).

## Dealing with Uncertainty
Temporal representation must allow partial dates ("May 2023"), ranges ("Between Monday and Wednesday"), and contradictions (Witness A says 10:00, Witness B says 11:00). Events should use Allen's Interval Algebra semantics rather than strict UNIX timestamps.
""")

# 9. 09_uncertainty_model.md
write_md("09_uncertainty_model.md", """
# Uncertainty Model

## The Danger of "Confidence"
A heuristic score from an LLM (e.g., 0.91) is NOT a probability (91% chance this is true). It is a similarity or confidence-of-extraction metric.

## Semantic Dimensions of Uncertainty
NETRA must track three distinct axes:
1.  **Extraction Confidence (Heuristic)**: How confident is the tool (Qwen/Spacy) that it correctly parsed the sentence?
2.  **Source Reliability (Belief)**: How trustworthy is the source? (e.g., verified CDR vs anonymous tip).
3.  **Validation Status (Workflow)**: 
    *   `CANDIDATE`: Extracted, pending review.
    *   `CONFIRMED`: Validated mathematically or manually.
    *   `CONTRADICTED`: Conflicting evidence exists.
    *   `REJECTED`: Proven false.
""")

# 10. 10_cross_case_model.md
write_md("10_cross_case_model.md", """
# Cross-Case Model

## Global Entities vs Local Context
*   **Canonical Entities** are GLOBAL. "Ravi Kumar (9876543210)" exists once in the graph.
*   **Cases** are CONTEXTS. Case A and Case B are investigative boundaries.
*   **Case-Entity Linkage**: A Canonical Entity participates in a Case via a `case_entities` mapping, which includes the `role` (Suspect, Victim, Witness) specific to that case.

## Identity Resolution
A Phone Number "9876543210" in Case A and Case B must resolve to the SAME Canonical Digital Identifier. The system must not assume isolation. Ambiguity (e.g., two people using the same phone) is handled by linking the single Phone entity to two Person entities via `USES`, rather than creating two Phone entities.
""")

# 11. 11_case_linkage_model.md
write_md("11_case_linkage_model.md", """
# Case Linkage Model

## How Cases Connect
1.  **Shared Entities**: The most common linkage. (e.g., The same bank account appears in Case A and Case B).
2.  **Shared MO (Modus Operandi)**: Similar Event Patterns. (e.g., Case A and Case B both feature a CyberAction of type 'Phishing' using infrastructure 'XYZ').
3.  **Hierarchical Cases**: An overarching investigation (Operation X) containing sub-cases (FIR 1, FIR 2).

## Ontology Representation
`CASE` is modeled as a specialized `INVESTIGATION` entity that can have relationships like `RELATED_TO`, `SUB_CASE_OF`, and `SHARES_MO_WITH`.
""")

# 12. 12_netra_ontology_architecture.md
write_md("12_netra_ontology_architecture.md", """
# NETRA Ontology Architecture & Mapping

## How LLM Output Maps to the Ontology
1.  **LLM Phase**: Qwen outputs a loosely-typed JSON (e.g., `source: "John", target: "Phone X", rel: "USES"`).
2.  **Orchestrator Phase**: The system creates an `Observation` mapping to the text snippet, and a `RelationshipAssertion` marked as `CANDIDATE`.
3.  **Validation Phase**: `validation_service.py` checks `check_ontology("PERSON", "USES", "PHONE")`. 
4.  **Resolution Phase**: The ER engine maps "John" to `Canonical Person E-123` and "Phone X" to `Canonical Phone E-456`.
5.  **Graph Phase**: The canonical relationship is projected into Apache AGE.

**The Golden Rule**: Qwen must be allowed to hallucinate or guess. The Ontology dictates what the Graph will accept. If Qwen outputs `PHONE -> OWNS -> PERSON`, the Validation layer rejects it gracefully without crashing the pipeline.
""")

# 13. 13_mapping_CASE_UCO_STIX_COSMOS_NETRA.md
write_md("13_mapping_CASE_UCO_STIX_COSMOS_NETRA.md", """
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
""")

print("Batch 2 completed.")
