import os

with open("/mnt/d/NETRA/SIH2026/ai-service/app/schemas/resolution.py", "a") as f:
    f.write("\n\nclass ProvenanceLink(BaseModel):\n    record_id: str\n    mention_id: str\n    confidence: float\n\nclass CanonicalEntity(BaseModel):\n    entity_id: str\n    entity_type: str\n    canonical_name: str\n    source_mentions: List[ProvenanceLink]\n")
