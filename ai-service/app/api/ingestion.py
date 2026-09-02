from fastapi import APIRouter, HTTPException
from app.schemas.ingestion import IngestionRequest, IngestionResponse
from app.services.ingestion_service import process_file

router = APIRouter()

@router.post("/process", response_model=IngestionResponse)
def process_ingestion(request: IngestionRequest):
    try:
        records = process_file(request.source_file_path, request.source_type, request.case_id)
        return IngestionResponse(
            source_type=request.source_type,
            record_count=len(records),
            records=records
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
