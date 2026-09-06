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
