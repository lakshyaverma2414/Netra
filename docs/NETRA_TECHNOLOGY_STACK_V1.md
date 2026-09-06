# NETRA Technology Stack V1

| Layer            | Technology         | Version        | Purpose                       | Status |
| ---------------- | ------------------ | -------------- | ----------------------------- | ------ |
| Frontend         | React              | ^18.3.1        | Investigator UI               | IMPLEMENTED |
| Language         | TypeScript         | ^5.5.3         | Frontend                      | IMPLEMENTED |
| Build            | Vite               | ^5.4.1         | Frontend build                | IMPLEMENTED |
| Styling          | Tailwind CSS       | ^3.4.10        | UI                            | IMPLEMENTED |
| Graph UI         | Cytoscape.js       | ^3.30.2        | Network visualization         | IMPLEMENTED |
| Maps             | Leaflet            | N/A            | Geographic visualization      | PLANNED |
| Charts           | Recharts           | ^3.10.1        | Analytics                     | IMPLEMENTED |
| Backend          | Spring Boot        | 3.3.3          | Main API/security gateway     | IMPLEMENTED |
| Security         | Spring Security    | 3.3.3          | Authentication/RBAC           | IMPLEMENTED |
| AI API           | FastAPI            | 0.115.0        | AI service                    | IMPLEMENTED |
| LLM              | Qwen (Qwen3-4B)    | Instruct-2507  | Semantic extraction/reasoning | IMPLEMENTED |
| Agent            | LangGraph          | 0.2.14         | Investigation workflow        | IMPLEMENTED |
| Inference        | llama.cpp          | (binary)       | Local model inference         | IMPLEMENTED |
| Database         | PostgreSQL         | (active)       | System of record              | IMPLEMENTED |
| Graph            | Apache AGE         | (active)       | Graph projection/traversal    | IMPLEMENTED |
| Vector           | pgvector           | (schema built) | Semantic retrieval            | PARTIAL |
| Analytics        | NetworkX           | 3.3            | Graph analytics               | IMPLEMENTED |
| ML               | scikit-learn       | N/A            | Statistical/ML analysis       | PLANNED |
| Documents        | Docling            | N/A            | Document processing           | PLANNED |
| OCR              | PaddleOCR          | N/A            | OCR                           | PLANNED |
| NER              | GLiNER             | N/A            | Entity extraction             | PLANNED |
| ER               | Splink             | 4.0.0          | Entity resolution             | IMPLEMENTED |
| Blockchain       | Hyperledger Fabric | N/A            | Evidence integrity/provenance | MOCK |
| Storage          | MinIO/S3/etc.      | N/A            | Evidence storage              | PLANNED |
| Containerization | Docker             | N/A            | Deployment                    | PLANNED |
| Reverse proxy    | Nginx/etc.         | N/A            | Gateway                       | PLANNED |
