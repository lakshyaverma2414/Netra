from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.clients.llama_client import llama_client

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    qwen: str
    database: str
    graph: str

@router.get("/api/v1/health", response_model=HealthResponse)
async def health_check(response: Response, db: Session = Depends(get_db)):
    db_status = "connected"
    graph_status = "connected"
    
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    try:
        conn = db.connection().connection
        with conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, \"$user\", public;")
            cur.execute("SELECT * FROM ag_graph LIMIT 1;")
    except Exception:
        graph_status = "disconnected"
        
    qwen_is_up = await llama_client.check_health()
    qwen_status = "connected" if qwen_is_up else "disconnected"

    if db_status == "disconnected" or graph_status == "disconnected" or qwen_status == "disconnected":
        status = "degraded"
        response.status_code = 503
    else:
        status = "ok"

    return HealthResponse(
        status=status,
        qwen=qwen_status,
        database=db_status,
        graph=graph_status
    )
