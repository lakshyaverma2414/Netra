from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories.entity_repository import EntityRepository

router = APIRouter(prefix="/api/v1", tags=["entities"])

@router.get("/cases/{case_id}/entities")
def list_case_entities(case_id: str, db: Session = Depends(get_db)):
    repo = EntityRepository(db)
    entities = repo.list_by_case(case_id)
    return [{"entity_id": e.entity_id, "entity_type": e.entity_type, "canonical_name": e.canonical_name} for e in entities]

@router.get("/entities/{entity_id}")
def get_entity(entity_id: str, db: Session = Depends(get_db)):
    repo = EntityRepository(db)
    e = repo.get_by_id(entity_id)
    if not e:
        raise HTTPException(status_code=404)
    return {"entity_id": e.entity_id, "entity_type": e.entity_type, "canonical_name": e.canonical_name, "status": e.resolution_status}
