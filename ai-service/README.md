# NETRA AI Service

This service provides the intelligence layer for the NETRA criminal network analysis system. It connects unstructured data to a local Qwen LLM for entity and relationship extraction, manages entity resolution, and synchronizes authoritative relationships with PostgreSQL and Apache AGE.

## Requirements
- Python 3.10+
- PostgreSQL 16+ with Apache AGE and pgvector extensions
- llama.cpp HTTP server running locally with Qwen3-4B-Instruct-2507

## Local Startup Instructions

### 1. Configure Environment
Copy the example environment file and configure it with your database and LLM server details:
```bash
cp .env.example .env
```
Ensure `QWEN_BASE_URL` points to your running llama.cpp server.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI Server
From the `ai-service` directory, start the server using uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Verify API
Navigate to http://localhost:8000/docs in your browser to view the Swagger UI.
Test the `GET /api/v1/health` endpoint to ensure the database, graph, and Qwen model are connected.

## Running Tests
To run the automated tests for the API layer:
```bash
pytest -v ../tests/test_step10_ai_foundation.py
```
