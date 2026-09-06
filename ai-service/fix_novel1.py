import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "r") as f:
    code = f.read()

code = code.replace("from app.schemas.resolution import CanonicalEntity, ProvenanceLink", """
from pydantic import BaseModel
from typing import List
class ProvenanceLink(BaseModel):
    record_id: str
    mention_id: str
    confidence: float

class CanonicalEntity(BaseModel):
    entity_id: str
    entity_type: str
    canonical_name: str
    source_mentions: List[ProvenanceLink]
""")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "w") as f:
    f.write(code)
