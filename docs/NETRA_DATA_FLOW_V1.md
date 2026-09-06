# NETRA Data Flow Architecture V1

```text
SOURCE SYSTEMS (Local Files / Authorized Uploads)
     │
     ▼
INGESTION (FastAPI /api/v1/ingestion)
     │
     ▼
NORMALIZATION (Text Extraction)
     │
     ▼
DOCUMENT / STRUCTURED PROCESSING
     │
     ▼
SEMANTIC EXTRACTION (Qwen via llama.cpp)
     │
     ├── Entities (Persons, Locations, Phones)
     ├── Events (CriminalIncidents, Meetings)
     ├── Relationships (CONSPIRED_WITH, LOCATED_AT)
     ├── Temporal context
     └── Evidence spans
     │
     ▼
ENTITY RESOLUTION (Splink Probabilistic Matching)
     │
     ▼
RELATIONSHIP VALIDATION (V1.1 Ontology YAML Rules)
     │
     ▼
EVIDENCE / PROVENANCE (Tracking source chunk IDs)
     │
     ▼
POSTGRESQL (Canonical Relational Storage)
     │
     ▼
APACHE AGE GRAPH (Cypher Projection via ProjectionService)
     │
     ▼
GRAPH ANALYTICS (NetworkX Centrality/Degree Metrics)
     │
     ▼
PATTERN DETECTION (Algorithmically-driven finding generation)
     │
     ▼
INVESTIGATIVE LEADS (Stored in `findings` table)
     │
     ▼
INVESTIGATOR (React UI - Graph Explorer / Workspace)
```

## Transition Specifications

| Stage | Input | Output | Validated By | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Ingestion** | Raw File (TXT, JSON) | Local Temp File | Spring Security (RBAC) | `IMPLEMENTED` |
| **Semantic Extraction** | Raw Text Chunk | JSON Array (Entities, Rels) | Qwen Strict Prompting | `IMPLEMENTED` |
| **Resolution** | Extracted Entity | Canonical Entity UUID | Splink Model Weights | `IMPLEMENTED` |
| **Validation** | Extracted Relationship | `CONFIRMED` / `REJECTED` | OntologyValidator | `IMPLEMENTED` |
| **Graph Projection** | Relational `CONFIRMED` | AGE Vertices/Edges | PostgreSQL Triggers/Service | `IMPLEMENTED` |
| **Analytics/Patterns** | AGE Cypher Output | `INVESTIGATIVE_LEAD` | AnalyticsService | `IMPLEMENTED` |
