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
