# NETRA System Architecture Specification V1

## 1. Executive Architecture
NETRA is a generic, AI-powered investigative intelligence platform capable of consuming heterogeneous authorized data, constructing an evidence-aware semantic knowledge graph, discovering relationships and patterns, and assisting investigators. It intentionally separates AI reasoning (Qwen) from deterministic orchestration (LangGraph) and authoritative semantic validation (Generic Ontology).

## 2. Component Architecture Status
| Component      | Technology | Responsibility       | Current Status | Data In | Data Out | PPT Layer    |
| -------------- | ---------- | -------------------- | -------------- | ------- | -------- | ------------ |
| React          | TypeScript | Investigator UI      | IMPLEMENTED    | JSON    | JSON     | Presentation |
| Spring Boot    | Java 21    | API/security         | IMPLEMENTED    | HTTP    | SQL/HTTP | Application  |
| FastAPI        | Python 3   | AI service           | IMPLEMENTED    | HTTP    | SQL/Graph| AI           |
| Qwen           | llama.cpp  | Semantic reasoning   | IMPLEMENTED    | Text    | JSON     | AI           |
| LangGraph      | Python     | Agent orchestration  | IMPLEMENTED    | Events  | Actions  | AI           |
| PostgreSQL     | PSQL 16    | System of record     | IMPLEMENTED    | SQL     | SQL      | Data         |
| Apache AGE     | Extension  | Graph projection     | IMPLEMENTED    | Cypher  | Cypher   | Data         |
| pgvector       | Extension  | Semantic retrieval   | PARTIAL        | Vectors | Nodes    | Data         |
| NetworkX       | Python     | Graph analytics      | IMPLEMENTED    | Graph   | Metrics  | Analytics    |
| Pattern Engine | Python     | Pattern discovery    | PARTIAL        | Cypher  | Leads    | Analytics    |
| Object Storage | Local/S3   | Evidence             | PLANNED        | Files   | Links    | Evidence     |
| Fabric         | Blockchain | Integrity/provenance | MOCK           | Hashes  | Receipts | Trust        |

## 3. Generic AI & Ontology Architecture
The AI layer is rigorously decoupled from the 10-case evaluation corpus.
- **Qwen** is responsible for generic semantic understanding, extracting entities, events, and raw relationships.
- **Generic Ontology V1.1 (YAML)** strictly defines the semantic boundaries. 
- **Validation Engine** structurally maps Qwen's generic criminal relationships (e.g., `CONSPIRED_WITH`) into strict event-mediated projections (e.g., `netra:CriminalIncident`) without hardcoding case-specific logic.

## 4. Security & Evidence Architecture
- **Authentication**: JWT-based RBAC enforced entirely at the Spring Boot Gateway boundary. The Python AI service sits securely behind this firewall.
- **Case-Level Access**: Evaluated dynamically based on `cases.created_by` mappings in PostgreSQL.
- **Provenance**: Every canonical relationship retains a direct link to the `chunk_id` and `evidence_id`, allowing a full audit trail back to the source text. Hyperledger Fabric hashing is mocked/planned for future implementation.

## 5. Scalability & Limitations
- **Current Bottleneck**: `llama.cpp` CPU inference limits concurrent document processing.
- **Future Solution**: Transition to vLLM/TensorRT on distributed GPU nodes. Move asynchronous pipeline execution into Kafka consumers to decouple the API from heavy extraction workloads.

## 6. PPT Architecture Diagram Specification (Target Architecture)

```text
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                         │
│ CCTNS/ICJS* | FIR | CDR | Financial | Reports | Media │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 INGESTION & PROCESSING                  │
│ Connectors | Parsing | OCR | Normalization | Validation │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    AI / SEMANTIC LAYER                  │
│ Qwen | LangGraph | Entity/Event/Relation Extraction     │
│ Entity Resolution | Semantic Understanding              │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│              KNOWLEDGE & EVIDENCE LAYER                 │
│ Generic Ontology | PostgreSQL | Apache AGE | pgvector   │
│ Evidence | Provenance | Assertions                      │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 ANALYTICS / INTELLIGENCE                │
│ Graph Analytics | Pattern Detection | Cross-case Links  │
│ Anomaly Detection | Investigative Leads                 │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 INVESTIGATOR CONSOLE                    │
│ Graph | Evidence | Leads | AI Assistant | Findings      │
│                    Human Decision                       │
└─────────────────────────────────────────────────────────┘
* Authorized integrations (Target future state)
```
