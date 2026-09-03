# NETRA_STEP10_4_IMPLEMENTATION_REPORT_V1

## Overview
Step 10.4 successfully implemented the **Entity Resolution Engine**, bridging the gap between raw LLM extractions (from Step 10.3) and canonical graph nodes, fully utilizing deterministic normalization, alias tracking, and fuzzy matching.

**Crucially, Qwen is completely excluded from the identity decision process.** The resolution engine operates entirely via code and exact heuristic scoring.

## Accomplishments

### 1. Robust Deterministic Normalization
- **Phones**: Enforces valid prefixes and strips spacing to resolve `+91-9999988888` and `919999888888` against the exact identifier representation.
- **Vehicles**: Condenses spaces and standardizes case (`RJ 14 XYZ` seamlessly matches `RJ-14-XYZ`).
- **People/Locations/Orgs**: Automatically folds extra spaces, normalizes cases, and resolves exact and near-exact names.

### 2. Multi-Tiered Candidate Generation & Scoring
The system queries PostgreSQL against the known Ground Truth universe to score candidates deterministically:
- **Tier 1 (Score 1.00)**: Exact Identifiers (`PHONE`, `UPI_ID`, `VEHICLE`).
- **Tier 2 (Score 0.95)**: Known Aliases (`V. Singh` -> `Vikram Singh`).
- **Tier 3 (Score 0.90)**: Exact Normalized Name (`Vikram Singh`).
- **Tier 4 (Score 0.80+)**: Fuzzy similarity for typos or minor variations.

### 3. Safe Ambiguity Handling
- To prevent the "False Merge" scenario, if multiple candidates exist with high but similar scores (e.g. multiple "Rajan"s in the DB with < 0.1 score variance), the system safely falls back to a **`CANDIDATE`** status rather than forcing a `CONFIRMED` merge.
- Unrelated entities (e.g. "Rahul") safely resolve to **`REJECTED`**.

### 4. Fully Auditable Provenance
- Resolutions are inserted into `entity_mentions` and `entity_resolution_log` as required by the schema.
- The logs explicitly contain the scoring reasoning in a JSON column (`methods: ["alias_match"]`), ensuring investigators can trace *why* a particular alias was mapped.

## API Integration
The REST layer successfully supports `POST /api/v1/resolution/resolve`:
```json
{
  "request_id": "...",
  "results": [
    {
      "mention": "V. Singh",
      "entity_type": "PERSON",
      "status": "CONFIRMED",
      "entity_id": "P-002",
      "canonical_name": "Vikram Singh",
      "score": 0.95,
      "matching_methods": ["alias_match"]
    }
  ]
}
```

## Testing Status
All acceptance criteria automated tests passed against the PostgreSQL schema:
- [x] Alias resolution (`V. Singh` -> `P-002`)
- [x] Exact identifier resolution (`ghost@bank`, `RJ 14 XYZ`)
- [x] Canonical Name Resolution
- [x] Ambiguity rejection
- [x] Negative match rejection
- [x] DB Provenance validation

## Next Steps
The mentions extracted by Qwen can now be successfully traced back to existing nodes in the database. The next natural architectural milestone is **Step 10.5 (Relationship Validation)**, where we validate whether `P-002` actually has a valid `TRANSFERRED_TO` edge pointing to `UPI-001`, and formally authorize it before writing to the Apache AGE graph in Step 10.6.
