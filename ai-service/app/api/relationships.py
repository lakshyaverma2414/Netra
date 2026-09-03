from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.schemas.resolution import CanonicalEntity
from app.schemas.validation import RelationshipValidationResult
from app.services.relationship_service import extract_all_relationships
from app.services.qwen_relationship_service import extract_qwen_relationships_for_record
from app.validation.relationship_validator import RelationshipValidator
from app.graph.graph_writer import MockGraphWriter as GraphWriter

router = APIRouter()

class RelationshipProcessRequest(BaseModel):
    records: List[NormalizedRecord]
    mentions: List[EntityMention]
    canonical_entities: List[CanonicalEntity]
    method: str = "HYBRID"

class RelationshipProcessResponse(BaseModel):
    total_candidates: int
    confirmed: int
    needs_review: int
    rejected: int
    graph_written: int
    validation_results: List[RelationshipValidationResult]

# We need a shared global or injected GraphWriter in a real app.
# For prototype, we instantiate it here.
graph_writer = GraphWriter()
graph_writer.connect() # Stub

@router.post("/process", response_model=RelationshipProcessResponse)
def process_relationships(request: RelationshipProcessRequest):
    try:
        candidates = []
        
        if request.method in ["RULE", "HYBRID"]:
            candidates.extend(extract_all_relationships(
                request.records, request.mentions, request.canonical_entities
            ))
            
        if request.method in ["QWEN", "HYBRID"]:
            for record in request.records:
                qwen_cands = extract_qwen_relationships_for_record(
                    record, request.mentions, request.canonical_entities
                )
                candidates.extend(qwen_cands)
                
        validator = RelationshipValidator(request.records, request.canonical_entities)
        validation_results = validator.validate(candidates)
        
        written_count = graph_writer.write_relationships(validation_results)
        
        confirmed_count = sum(1 for r in validation_results if r.status.value == "CONFIRMED")
        needs_review_count = sum(1 for r in validation_results if r.status.value == "NEEDS_REVIEW")
        rejected_count = sum(1 for r in validation_results if r.status.value == "REJECTED")
        
        return RelationshipProcessResponse(
            total_candidates=len(candidates),
            confirmed=confirmed_count,
            needs_review=needs_review_count,
            rejected=rejected_count,
            graph_written=written_count,
            validation_results=validation_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
