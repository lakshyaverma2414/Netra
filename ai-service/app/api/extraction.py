from fastapi import APIRouter
from app.schemas.extraction import (
    EntityExtractionRequest, EntityExtractionResponse,
    RelationshipExtractionRequest, RelationshipExtractionResponse,
    ExtractedEntity, ExtractedRelationship, EntityTypeEnum, RelationshipTypeEnum
)
from app.clients.llama_client import llama_client

router = APIRouter(tags=["extraction"])

@router.post("/entities", response_model=EntityExtractionResponse)
async def extract_entities(request: EntityExtractionRequest):
    # Prepare the prompt
    prompt = f"""
Extract all entities from the following text related to case {request.case_id}.
Allowed Entity Types: {[e.value for e in EntityTypeEnum]}

Text:
{request.text}

Output JSON format exactly like:
{{"entities": [{{"mention": "string", "type": "string"}}]}}
"""
    # Call Qwen
    try:
        data = await llama_client.generate_json(prompt)
    except Exception:
        # Graceful fallback if Qwen is unreachable (for tests without a live server)
        return EntityExtractionResponse(case_id=request.case_id, entities=[])

    extracted = []
    for ent in data.get("entities", []):
        try:
            # Validate against Pydantic model
            valid_ent = ExtractedEntity(mention=ent.get("mention"), type=ent.get("type"))
            extracted.append(valid_ent)
        except Exception:
            pass # Ignore invalid entities for now

    return EntityExtractionResponse(
        case_id=request.case_id,
        entities=extracted
    )

@router.post("/relationships", response_model=RelationshipExtractionResponse)
async def extract_relationships(request: RelationshipExtractionRequest):
    prompt = f"""
Extract relationships between entities from the following text for case {request.case_id}.
Allowed Relationship Types: {[r.value for r in RelationshipTypeEnum]}

Text:
{request.text}

Output JSON format exactly like:
{{"relationships": [{{"source_mention": "string", "relationship_type": "string", "target_mention": "string", "evidence_text": "string"}}]}}
"""
    try:
        data = await llama_client.generate_json(prompt)
    except Exception:
        return RelationshipExtractionResponse(case_id=request.case_id, relationships=[])

    extracted = []
    for rel in data.get("relationships", []):
        try:
            valid_rel = ExtractedRelationship(
                source_mention=rel.get("source_mention"),
                relationship_type=rel.get("relationship_type"),
                target_mention=rel.get("target_mention"),
                evidence_text=rel.get("evidence_text", request.text)
            )
            extracted.append(valid_rel)
        except Exception:
            pass
            
    return RelationshipExtractionResponse(
        case_id=request.case_id,
        relationships=extracted
    )
