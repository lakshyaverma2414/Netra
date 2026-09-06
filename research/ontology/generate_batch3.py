import os

BASE_DIR = "/mnt/d/NETRA/SIH2026/research/ontology"

def write_md(name, content):
    with open(os.path.join(BASE_DIR, name), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 14. 14_ontology_design_decisions.md
write_md("14_ontology_design_decisions.md", """
# Ontology Design Decisions

## 1. Event-Centric over Binary Relations for Complex Interactions
*Decision*: `PERSON -> COMMUNICATES_WITH -> PERSON` is insufficient.
*Justification*: Communications have timestamps, durations, and channels. Binary relations in Apache AGE only have edge properties, which makes querying "who communicated via WhatsApp on Tuesday" highly inefficient if modeled purely as edge properties on a single static `COMMUNICATES_WITH` edge. Using an `Event` node (e.g., `CommunicationEvent`) linked to both Persons allows robust temporal indexing and n-ary participation.

## 2. Strong Provenance Requirement
*Decision*: Every Canonical Edge must map back to an `Assertion`, which maps to an `Observation`, which maps to a `SourceRecord`.
*Justification*: In criminal investigations, facts are challenged in court. A KG without trace-back is an intelligence toy, not an investigative tool. 

## 3. Ambiguity Tolerance
*Decision*: Allow `Entity -> ALIAS_OF -> Entity` and delayed resolution.
*Justification*: We often don't know if "John Doe" in Case A is "John Doe" in Case B. The ontology must allow them to exist as separate Canonical Entities until evidence justifies an `SAME_AS` edge, which the Graph DB can traverse seamlessly.
""")

# 15. 15_NETRA_GENERIC_ONTOLOGY_V1_PROPOSAL.md
write_md("15_NETRA_GENERIC_ONTOLOGY_V1_PROPOSAL.md", """
# NETRA Generic Investigative Ontology Framework V1 Proposal

## 1. Scope
The scope of NETRA V1 is to provide a generic, extensible, and semantically coherent conceptual framework for heterogeneous criminal investigations, covering physical crime, cyber crime, and financial crime.

## 2. Design Principles
*   **Ontology ≠ Truth**: It defines the bounds of the possible.
*   **Separation of Concerns**: Divide the real-world (Entities/Events) from the investigative process (Evidence/Provenance).
*   **Event-Centricity**: Use Events for temporal, n-ary interactions.
*   **Interoperability**: Map to STIX, CASE/UCO, and COSMOS where appropriate.

## 3. Upper-Level Concepts
*   `Entity`
*   `Event`
*   `Relationship`
*   `ProvenanceRecord`
*   `Context` (Case)

## 4. Entity Hierarchy
Refer to `04_entity_taxonomy_proposal.yaml`. Core branches: `Actor`, `DigitalObject`, `PhysicalObject`, `Location`.

## 5. Event/Action Hierarchy
Refer to `05_event_action_taxonomy_proposal.yaml`. Core branches: `CommunicationEvent`, `FinancialTransaction`, `PhysicalMovement`, `CyberAction`, `CriminalIncident`.

## 6. Relationship Hierarchy
Refer to `06_relationship_taxonomy_proposal.yaml`. Core branches: `Identity`, `Association`, `OwnershipControl`, `Spatial`, `Temporal`.

## 7. Attributes
Entities have intrinsic attributes (e.g., `name`, `dob`, `mac_address`). Events have temporal and operational attributes (e.g., `timestamp`, `amount`, `channel`).

## 8. Temporal Semantics
Events utilize `start_time` and `end_time` (Interval Algebra). Relationships utilize `valid_from` and `valid_to`. Observations utilize `observed_at`.

## 9. Evidence/Provenance Semantics
Aligns with W3C PROV-O and CASE: `SourceRecord` -> `Observation` -> `Assertion` -> `Canonical Relationship`.

## 10. Uncertainty Semantics
Distinguish AI `extraction_confidence` from analytical `validation_status` (`CANDIDATE`, `CONFIRMED`, `CONTRADICTED`, `REJECTED`).

## 11. Entity-Resolution Semantics
Global identity is managed through `SAME_AS` linkages rather than destructive merging, preserving historical investigative states.

## 12. Case Semantics
A `Case` is a contextual boundary. Entities are globally unique but linked to cases via `case_entities` mapping roles.

## 13. Cross-Case Semantics
Enabled by default. A canonical identifier (e.g., a Phone Number) acts as an automatic pivot bridging Case A and Case B.

## 14. Ontology Constraints
Constraints validate types but must be broad enough to capture reality (e.g., `ORGANIZATION` can `OWN` an `ORGANIZATION`).

## 15. Inverse/Symmetric Relationships
Defined in the relationship taxonomy (e.g., `KNOWS` is symmetric, `OWNS` is directed).

## 16. Extensibility Mechanism
Subclassing. A new crime type (e.g., "Drone Interception") creates a new `Event` subclass without altering the upper ontology.

## 17. Versioning/Governance
Ontology updates are versioned (V1.0, V1.1) to ensure backwards compatibility with existing AGE graph projections.

## 18. Mapping to CASE/UCO/STIX/COSMOS
*   **CASE**: Trace/Observation mapping.
*   **STIX**: Threat Actor and Infrastructure mapping.
*   **COSMOS**: Ecosystem phase and role mapping.

## 19. Mapping to Current NETRA Architecture
Qwen (Extraction) -> Postgres (Provenance/Candidate) -> AGE (Canonical Graph).

## 20. Examples
*   *Financial*: `Person A` -> `PARTICIPATES_IN (Sender)` -> `Transaction Event` -> `PARTICIPATES_IN (Receiver)` -> `Person B`.
*   *Physical*: `Vehicle X` -> `LOCATED_AT` -> `Location Y`.

## 21. Known Limitations
Extremely granular digital forensics (e.g., specific NTFS registry keys) are out of scope and should be linked as external raw evidence artifacts rather than graphed nodes.

## 22. Proposed V1
The files generated in this research phase constitute the formal V1 Proposal. Upon approval, the `ONTOLOGY` dictionary in `validation_service.py` and the PostgreSQL schema will be refactored to support this model.
""")

print("Batch 3 completed.")
