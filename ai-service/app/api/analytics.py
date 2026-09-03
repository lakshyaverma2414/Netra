from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.analytics.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])

@router.get("/cases/{case_id}/network")
def get_case_analytics(case_id: str, db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.generate_leads(case_id=case_id)

@router.get("/global/network")
def get_global_analytics(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.generate_leads(case_id=None)

@router.get("/path")
def get_multi_hop_path(
    source: str = Query(..., description="Source Entity ID"),
    target: str = Query(..., description="Target Entity ID"),
    max_depth: int = Query(5, description="Maximum path depth (1-5)"),
    db: Session = Depends(get_db)
):
    if max_depth < 1 or max_depth > 5:
        raise HTTPException(status_code=400, detail="max_depth must be between 1 and 5")
        
    svc = AnalyticsService(db)
    result = svc.find_multi_hop_path(source, target, max_depth)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result
