# NETRA System Architecture Audit V1

## Objective
This document provides a comprehensive technical audit of the current NETRA system repository, evaluating the implementation status of all proposed capabilities based on actual code paths, runtime integrations, and data flows.

## Component Implementation Status

| Component | Status | Justification |
| :--- | :--- | :--- |
| **React Frontend** | `IMPLEMENTED` | Live UI, dynamic graph explorer, auth context, case tracker fully wired. |
| **Spring Boot API** | `IMPLEMENTED` | Serves as the gateway, handles RBAC, issues JWTs, manages relational Cases/Investigation records. |
| **Spring Security** | `IMPLEMENTED` | Active `JwtAuthenticationFilter`, BCrypt password encoding, route-level authorization. |
| **Python AI Service (FastAPI)** | `IMPLEMENTED` | Manages AI ingestion pipelines, ontology validation, analytics, and graph queries. |
| **Qwen LLM (Semantic Extraction)** | `IMPLEMENTED` | Runs via `llama.cpp` on port 8081. Handles extraction of generic events, entities, and relationships. |
| **LangGraph Orchestration** | `IMPLEMENTED` | Powers the investigation workflow via `app/agent/workflow.py` handling tools and multi-step reasoning. |
| **PostgreSQL System of Record** | `IMPLEMENTED` | Serves as the primary structured data store (users, cases, relationships, entities). |
| **pgvector** | `PARTIALLY_IMPLEMENTED` | Schema explicitly contains `embedding public.vector`, but end-to-end vector retrieval pipelines are not actively routing in current ingestion. |
| **Apache AGE** | `IMPLEMENTED` | The `ProjectGraph` service actively mirrors PostgreSQL verified relationships into a Cypher-queryable graph database (`crime_network`). |
| **NetworkX (Analytics)** | `IMPLEMENTED` | Actively used in `analytics_service.py` for algorithmic pattern matching (e.g. centrality, degree metrics). |
| **Pattern Engine** | `PARTIALLY_IMPLEMENTED` | Analytical rules (Cross-Case Bridge, Shared Identifier, Financial Convergence, Communication Concentration) are coded directly in Python logic rather than executing from standalone YAML rules. |
| **Splink (Entity Resolution)** | `IMPLEMENTED` | Actively integrated via `resolution_service.py` using probabilistic weights for resolving identity variants. |
| **Docling / PaddleOCR / GLiNER** | `NOT_IMPLEMENTED` | Proposed document processing and NLP layers. Currently relying entirely on Qwen via textual prompts for all tasks. |
| **Hyperledger Fabric (Blockchain)** | `MOCK` | Schema includes `fabric_transaction_id`, but the system does not actually write to or query an off-chain/on-chain Fabric ledger. |
| **MinIO/S3 Storage** | `PLANNED` | Current uploads save directly to local `uploads/` directory on disk. |
| **CCTNS / ICJS Connectors** | `NOT_IMPLEMENTED` | All current ingestion relies on manual JSON/TXT upload. No live external data polling exists. |

## First Principle Adherence
The 10-case dataset is utilized strictly as an **Evaluation / Regression Corpus**. The AI architecture correctly abstracts schema handling using a V1.1 Generic Investigative Ontology, enabling successful extraction of unseen data without hardcoding evaluation cases into the parsing logic.
