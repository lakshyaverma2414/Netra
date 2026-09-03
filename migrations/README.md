# NETRA Production Database Schema (V2)

This directory contains the production schema definition for NETRA. The architecture uses a **Hybrid Relational + Graph** model utilizing **PostgreSQL 16+** as the system of record and **Apache AGE** as the graph projection layer.

## Architectural Philosophy

1. **PostgreSQL is the System of Record**: All investigations, source documents, raw extractions, and evidence are durably stored in standard relational tables.
2. **Apache AGE is the Projection Layer**: The graph (`crime_network`) is purely an analytical projection of **CONFIRMED** relationships. The graph must never become a separate, conflicting source of truth.
3. **Global Entities, Contextual Cases**: Entities (e.g., `Vikram Singh` or `+91-9999988888`) exist globally. They are tied to specific investigations via associative tables (`case_entities`). We do not duplicate nodes per case.

---

## Core Schema Modules

### 1. Investigations & Cases
- `cases`: The top-level investigation boundaries (e.g., `C-001: Operation Black Web`).
- `case_links`: Associates related investigations.

### 2. Ingestion & Source Records
Tracks exactly where data came from to ensure 100% legal provenance.
- `ingestion_batches`: Tracks bulk uploads.
- `source_records`: Individual structured records (e.g., a CDR row or FIR entry).
- `documents` / `document_chunks`: Unstructured files and parsed text chunks.

### 3. Entity Resolution Pipeline
Models the journey from "fragmented text" to "known canonical identity."
- `entity_mentions`: The exact text string found in a document (e.g., *"V. Singh"*).
- `entities`: The canonical, resolved global identity (e.g., `P-002` / *"Vikram Singh"*).
- `entity_aliases`: Alternate names or monikers.
- `entity_resolution_log`: Audit trail explaining *why* a mention was merged into a canonical entity (including Splink/AI probability scores).
- `case_entities`: Maps a global entity to the cases it appears in.

### 4. Relationships & Assertions
Relationships are treated as hypotheses until validated.
- `relationship_assertions`: A single observation of a relationship from a specific document. (Status: `ACCEPTED`, `NEEDS_REVIEW`, `REJECTED`).
- `relationships`: The canonical, global relationship (e.g., `P-003 --OWNS--> UPI-001`). Only populated when assertions are validated.
- `relationship_cases`: Maps the global relationship to specific cases for isolated case-graph viewing.

### 5. Evidence & Findings
- `evidence`: Cryptographically hashed files/records.
- `evidence_cases`, `evidence_entities`, `evidence_relationships`: Explicit mapping bridging investigative insights back to raw legal evidence.
- `evidence_custody_log`: Chain of custody tracking (Collected -> Forensics -> Investigator).
- `findings`: AI or Investigator-generated leads (e.g., "Suspicious cross-case financial bridge detected").

---

## Apache AGE Integration

The schema maintains an Apache AGE graph named **`crime_network`**.

### Sync Rules
- **Vertices**: Created from the `entities` table.
- **Edges**: Created from the `relationships` table.
- **Validation Gate**: A relationship is **only** written to AGE if its status is `CONFIRMED`. Unverified AI assertions (`NEEDS_REVIEW`) stay in Postgres but never enter the graph.

### Querying the Graph (psql)
To query the graph via CLI, you must load the AGE extension and set the search path:
```sql
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- Example: Count all cross-case edges
SELECT * FROM cypher('crime_network', $$ 
    MATCH ()-[e]->() RETURN count(e) 
$$) as (edge_count agtype);
```

---

## Strict Ontology Constraints
The schema enforces a strict relationship ontology to prevent graph pollution:
- **Valid Types**: `USES`, `OWNS`, `COMMUNICATES_WITH`, `LOCATED_AT`, `ASSOCIATED_WITH`, `TRANSFERRED_TO`, `LINKED_TO`.
- **Directionality**: Relationships must use proper canonical direction. (e.g., `PERSON --OWNS--> UPI_ACCOUNT`). Inverse relationships (like `OWNED_BY`) are handled at the query/UI level, **not** stored as separate edge types in the database.
