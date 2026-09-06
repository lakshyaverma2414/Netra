# NETRA Current vs Target Architecture

## Current Prototype Deployment (What is Built)
```text
Developer Machine (Windows / WSL)
│
├── React UI (Port 5173 - vite dev server)
├── Spring Boot API (Port 8080 - Auth & Case Management)
├── FastAPI Python AI Service (Port 8000 - Core AI pipelines)
├── llama.cpp (Port 8081 - Qwen3-4B-Instruct-2507 GGUF)
├── PostgreSQL 16 (Port 5433 - Relational persistence)
└── Apache AGE (PostgreSQL Extension - Graph persistence)
```

## Target Production Architecture (Future Real Deployment)
```text
                    USERS (Investigators / Officers)
                      │
                      ▼
                 Load Balancer
                      │
                      ▼
                  API Gateway (Kong / Nginx)
                      │
             ┌────────┴────────┐
             ▼                 ▼
       Spring Boot         Auth/RBAC (Keycloak / Oauth2)
             │
      ┌──────┼─────────┐
      ▼      ▼         ▼
    AI API  Evidence  Investigation
      │
      ▼
 AI Worker Pool (Celery / Kafka Consumers) <--> Qwen / vLLM GPU Cluster
      │
      ▼
 PostgreSQL / AGE / pgvector (High Availability Cluster)
      │
      ▼
 S3-Compatible Object Storage (MinIO)
      │
      ▼
 Hyperledger Fabric (Immutable Evidence Ledger)
```
