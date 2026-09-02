from fastapi import APIRouter, HTTPException
from app.schemas.extraction import ExtractionRequest, ExtractionResponse
from app.services.extractor_service import extract_entities

router = APIRouter()

@router.post("/entities", response_model=ExtractionResponse)
def process_extraction(request: ExtractionRequest):
    try:
        entities = extract_entities(request.records)
        return ExtractionResponse(
            record_count=len(request.records),
            entity_count=len(entities),
            entities=entities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
