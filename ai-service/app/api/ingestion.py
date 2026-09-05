from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.ingestion.core.batch_manager import BatchManager
from app.ingestion.connectors.file_connector import FileConnector
from app.ingestion.pipelines.structured_pipeline import process_structured_batch
from app.ingestion.pipelines.unstructured_pipeline import process_unstructured_evidence

router = APIRouter()

class StructuredBatchRequest(BaseModel):
    filepath: str
    file_type: str
    system_id: str
    dataset_id: str
    case_id: str

class UnstructuredEvidenceRequest(BaseModel):
    filepath: str
    file_type: str
    case_id: str

@router.post("/batch/structured")
def ingest_structured_batch(req: StructuredBatchRequest, db: Session = Depends(get_db)):
    try:
        # Connect & fetch
        conn = FileConnector(req.filepath, req.file_type)
        if not conn.connect():
            raise HTTPException(status_code=404, detail="File not found")
            
        raw_records = list(conn.fetch())
        
        # Create Batch
        mgr = BatchManager(db)
        batch = mgr.create_batch(req.dataset_id, req.case_id, req.filepath, req.file_type, "dummy-hash-if-not-calc")
        
        # Route to Pipeline
        process_structured_batch(db, batch.batch_id, req.system_id, req.dataset_id, req.case_id, raw_records)
        
        return {"status": "success", "batch_id": batch.batch_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/unstructured")
def ingest_unstructured_evidence(req: UnstructuredEvidenceRequest, db: Session = Depends(get_db)):
    try:
        # Create Batch
        mgr = BatchManager(db)
        batch = mgr.create_batch("DS_UNSTRUCTURED", req.case_id, req.filepath, req.file_type, "evidence-hash-placeholder")
        
        # Route to Pipeline
        process_unstructured_evidence(db, batch.batch_id, req.filepath, req.file_type, req.case_id)
        
        return {"status": "success", "batch_id": batch.batch_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
