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
