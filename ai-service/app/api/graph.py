from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.graph.age_graph_repository import AgeGraphRepository
from app.graph.projection_service import ProjectionService
from pydantic import BaseModel

router = APIRouter(tags=["graph"])

class ProjectionResponse(BaseModel):
    status: str
    vertices_created: int
    vertices_updated: int
    edges_created: int
    edges_updated: int
    edges_removed: int
    projection_version: str

@router.post("/project", response_model=ProjectionResponse)
def project_graph_api(db: Session = Depends(get_db)):
    svc = ProjectionService(db)
    return svc.project_all()

@router.get("/explore")
def explore_graph_api(case_id: str, entity_id: str = None, depth: int = 1, db: Session = Depends(get_db)):
    # Validate bounds
    if depth < 1 or depth > 3:
        raise HTTPException(status_code=400, detail="Depth must be between 1 and 3")
    
    # Delegate to repository which enforces case scopes server-side via SQL check
    repo = AgeGraphRepository(db)
    subgraph = repo.get_case_subgraph(case_id, entity_id=entity_id, depth=depth)
    return subgraph

@router.get("/cases/{case_id}")
def get_case_graph(case_id: str, entity_id: str = None, depth: int = 1, db: Session = Depends(get_db)):
    repo = AgeGraphRepository(db)
    return repo.get_case_subgraph(case_id, entity_id=entity_id, depth=depth)

@router.get("/global")
def get_global_graph(entity_id: str = None, depth: int = 1, db: Session = Depends(get_db)):
    repo = AgeGraphRepository(db)
    return repo.get_global_subgraph(entity_id=entity_id, depth=depth)
