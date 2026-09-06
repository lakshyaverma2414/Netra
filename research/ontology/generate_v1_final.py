import os

BASE_DIR = "/mnt/d/NETRA/SIH2026/research/ontology"

def write_md(name, content):
    with open(os.path.join(BASE_DIR, name), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. Update Domain Concept Model
write_md("03_netra_domain_concept_model.md", """
# NETRA Domain Concept Model

## Core Principle
**Ontology defines the concepts, semantics, and valid forms of representation within the investigative domain; it does not determine whether a particular assertion is true.**

## The Final NETRA Reasoning Model
```text
REAL WORLD
    │
    ↓
Entities / Events / Actions
    │
    ↓
Observed through sources
    │
    ↓
Evidence / Observations
    │
    ↓
AI / Rules / Analysts
    │
    ↓
Assertions / Claims
    │
    ↓
Entity Resolution + Semantic Validation
    │
    ├── REJECTED
    ├── NEEDS_REVIEW
    └── CONFIRMED
             │
             ↓
       Canonical Knowledge
             │
        ┌────┴─────┐
        ↓          ↓
      AGE      Analytics
                   ↓
             Investigation
```

## Abstract Layers
1.  **DOMAIN OBJECTS**: Entities (Actor, Object, Location) and Events/Actions.
2.  **SEMANTIC ASSERTIONS**: Relationships and Claims.
3.  **INVESTIGATION**: Case, Finding, Hypothesis.
4.  **EVIDENCE & OBSERVATION**: SourceRecord, Observation, DerivedArtifact.
5.  **PROVENANCE**: Agent, Activity, Chain of Custody.
6.  **CONTEXT**: Time, Place, Jurisdiction, Access.
""")

# 2. Direct vs Event Relationships
write_md("17_relationship_patterns_model.md", """
# Direct vs Event-Mediated Relationships

The ontology explicitly defines two architectural patterns for relationships.

## 1. Direct Relationship
Used for relatively simple, static, or stateful linkages that do not require extensive n-ary attributes (like amounts, specific timestamps, or multiple roles).
*   **Pattern**: `Entity ──RELATIONSHIP──> Entity`
*   **Examples**: `A ──OWNS──> B`, `A ──KNOWS──> B`, `A ──LOCATED_AT──> C`.

## 2. Qualified / Event-Mediated Relationship
Used for interactions, transactions, and bounded occurrences where the relationship itself is a first-class object with its own attributes and multiple participants.
*   **Pattern**: 
    ```text
    Entity
      ↓ participation role (e.g., sender)
    Event
      ↓ participation role (e.g., receiver)
    Entity
    ```
*   **Examples**: A financial transfer (`TransactionEvent` with `amount`, `timestamp`, `instrument`). A phone call (`CommunicationEvent` with `duration`, `channel`).
""")

# 3. Assertion and Claim Model
write_md("18_assertion_claim_model.md", """
# Assertion / Claim Semantics

## Assertion as a First-Class Concept
An Assertion is a claim about the world, produced by an agent (e.g., Qwen, an Analyst, a Rule Engine). It is the intermediate state between raw text (Observation) and Canonical Truth.

## Structure of an Assertion
```text
Assertion
 ├── subject = Person A
 ├── predicate = OWNS
 ├── object = Vehicle X
 ├── extraction method = Qwen-72B
 ├── source observation = Obs-998
 └── confidence = 0.91
```

## Lifecycle
An Assertion must undergo Entity Resolution and Semantic Validation. Its state transitions are:
*   `CANDIDATE`: Newly extracted.
*   `CONFIRMED`: Semantically valid and accepted into the Canonical KG.
*   `NEEDS_REVIEW`: Ambiguous or missing context.
*   `REJECTED`: Contradicted or invalid.
""")

# 4. Identity Semantics Model
write_md("19_identity_semantics_model.md", """
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
""")

# 5. Final V1 Proposal
write_md("20_NETRA_GENERIC_ONTOLOGY_V1_FINAL.md", """
# NETRA Generic Investigative Ontology Framework V1.0

## 1. Core Principle
**Ontology defines the concepts, semantics, and valid forms of representation within the investigative domain; it does not determine whether a particular assertion is true.**

## 2. The Final Top-Level Model
```text
NETRA GENERIC INVESTIGATIVE ONTOLOGY
│
├── DOMAIN OBJECTS
│   ├── ENTITY
│   │   ├── Actor
│   │   ├── Organization
│   │   ├── Digital Object
│   │   ├── Physical Object
│   │   ├── Asset
│   │   └── Location
│   │
│   └── EVENT / ACTION
│       ├── Communication
│       ├── Financial
│       ├── Movement
│       ├── Cyber
│       ├── Criminal Incident
│       └── Other Investigative Events
│
├── SEMANTIC ASSERTIONS
│   ├── Relationship (Direct linkages like OWNS)
│   └── Assertion / Claim (First-class claim objects)
│
├── INVESTIGATION
│   ├── Case
│   ├── Finding
│   └── Investigative Hypothesis
│
├── EVIDENCE & OBSERVATION
│   ├── Evidence
│   ├── SourceRecord
│   ├── Observation
│   ├── DerivedArtifact
│   └── ProcessingRun
│
├── PROVENANCE
│   ├── Agent (e.g., Qwen, Analyst)
│   ├── Activity
│   ├── Source
│   └── Chain of Custody
│
└── CONTEXT
    ├── Time
    ├── Place
    ├── Jurisdiction
    └── Classification / Access
```

## 3. Relationship vs Event Architecture
The framework natively supports both **Direct Relationships** (e.g., `Person ──OWNS──> Vehicle`) and **Qualified Event Relationships** (e.g., `Person ──participates(sender)──> TransactionEvent ──participates(receiver)──> Person`). Complex interactions require Event models.

## 4. Assertion Semantics
Assertions are first-class concepts representing the output of an extraction agent (e.g., Qwen). They hold subjects, predicates, objects, and heuristic confidence scores. Validation logic determines if an Assertion graduates to Canonical Knowledge. Qwen is one producer of assertions, not the arbiter of ontology or truth.

## 5. Evidence & Provenance Strict Separation
The ontology separates the *Claim* (`Assertion`) from the *Observation* (text snippet), from the *Evidence* (DerivedArtifact/PDF), from the *Provenance* (Chain of Custody, Agents). No canonical relationship can exist without this traceback.

## 6. Identity Semantics & Cross-Case Bridging
Shared identifiers (phones, emails, UPIs) act as **pivots**. `PHONE-123` -> `USED_BY` -> `Person A` and `Person B` creates a strong cross-case candidate link, but the ontology does not automatically collapse them via `SAME_AS` without supporting investigative evidence. This prevents catastrophic merging of family members, organizations, or recycled numbers.

## 7. Context Broadening
`Case` is subsumed under `Context`, allowing for nested definitions of scope, including `Jurisdiction`, `Time Window`, and `Source System` context.

## 8. Implementation Independence
This Ontology dictates the semantic model. PostgreSQL tables, Python classes, and Apache AGE graphs are mere downstream implementations and projections of this model, designed to satisfy its semantic rules.
""")

print("Final V1 Ontology models generated.")
