# NETRA Future Architecture Scope

This document specifies the planned roadmap for NETRA's technical evolution, deliberately kept separate from currently implemented features.

| Feature / Capability | Classification | Description |
| :--- | :--- | :--- |
| **CCTNS/ICJS Connectors** | `Long-term` | Authorized automated pooling of FIRs and charge sheets from state CAS architectures. |
| **Multi-state Deployment** | `Long-term` | Distributed multi-region setup with state-level data sovereignty controls. |
| **Multi-tenancy** | `Medium-term` | Isolating tenant data logically within PostgreSQL row-level security. |
| **Kafka Ingestion Pipeline** | `Near-term` | Replacing direct API-driven ingestion with an event-driven `raw_evidence_uploaded` Kafka message bus. |
| **Audio Transcription** | `Medium-term` | Automated Whisper-based transcription of intercepted calls. |
| **Computer Vision / OCR** | `Medium-term` | PaddleOCR and YOLO integration for extracting license plates and faces from video evidence. |
| **Indian-language NLP** | `Medium-term` | Bhashini integration for cross-lingual semantic extraction of regional FIRs. |
| **Advanced Graph Embeddings** | `Medium-term` | DeepWalk / Node2Vec vectorization of the AGE graph for semantic similarity search in pgvector. |
| **Production Hyperledger** | `Long-term` | Live blockchain nodes securing SHA-256 evidence hashes and chain-of-custody. |
| **GPU Inference Cluster** | `Medium-term` | Transitioning from CPU/llama.cpp to vLLM/TensorRT-LLM on dedicated H100 clusters for massive throughput. |
