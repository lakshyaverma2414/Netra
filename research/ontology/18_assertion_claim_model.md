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
