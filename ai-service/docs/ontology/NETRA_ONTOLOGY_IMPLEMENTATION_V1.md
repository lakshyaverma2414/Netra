# NETRA Ontology Implementation V1

## 1. Ontology Version
Version 1.0.0. Semantic contract loaded dynamically from `ontology/` YAMLs.

## 2. Entity and Event Mapping
Subclass hierarchy (e.g., `netra:Person` -> `netra:Actor`) is resolved at runtime via `OntologyRegistry.is_subclass()`.

## 3. Relationship Mapping
Domain and Range constraints dynamically validate classes. 
E.g., `netra:OWNS` now legitimately accepts `netra:Organization` owning `netra:Organization`, solving previous Validation failures.

## 4. Assertion Lifecycle
Assertions are decoupled from PostgreSQL. Qwen output targets `AssertionDef`. Only upon `CONFIRMED` validation does it migrate to canonical space.

## 5. Identity Semantics
`SAME_AS` is explicitly symmetric/transitive. `USED_BY` (e.g., for Phones) maps an identifier to multiple actors without enforcing equivalence.

## 6. PostgreSQL & AGE Mapping
PostgreSQL mapping remains in `app/ontology/mapping.py` as an explicit boundary translation, isolating the DB from semantic rules.

## 7. Migration Notes
The baseline (V0) implementation remains frozen. Next steps: Point `orchestrator.py` and `validation_service.py` to use `OntologyValidator` instead of the legacy hardcoded dictionary.
