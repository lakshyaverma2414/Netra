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
        
        # Also project the graph so it's instantly available in the UI
        from app.graph.projection_service import ProjectionService
        proj = ProjectionService(db)
        proj.project_all()
        
        return {"status": "success", "batch_id": batch.batch_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import UploadFile, File, Form
import os
import shutil
import uuid

@router.post("/upload/unstructured")
def upload_unstructured_evidence(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Ensure uploads directory exists
        upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file securely
        ext = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
        safe_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(upload_dir, safe_filename)
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create Batch
        mgr = BatchManager(db)
        batch = mgr.create_batch("DS_UNSTRUCTURED", case_id, filepath, ext, "evidence-hash-placeholder")
        
        # Route to Pipeline
        process_unstructured_evidence(db, batch.batch_id, filepath, ext, case_id)
        
        # Project the graph so it's instantly available in the UI
        from app.graph.projection_service import ProjectionService
        proj = ProjectionService(db)
        proj.project_all()
        
        return {"status": "success", "batch_id": batch.batch_id, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
