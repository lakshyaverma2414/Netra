from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class IngestionMetadata(BaseModel):
    source_file: str

class NormalizedRecord(BaseModel):
    record_id: str = Field(..., description="Evidence ID or unique record ID")
    source_type: str = Field(..., description="FIR, CDR, TRANSACTION, SURVEILLANCE")
    case_id: Optional[str] = Field(default=None, description="Optional case reference")
    content_type: str = Field(..., description="TEXT, STRUCTURED, SEMI_STRUCTURED")
    text: Optional[str] = Field(default=None, description="Extracted text")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Structured parsed data")
    metadata: IngestionMetadata = Field(..., description="Source provenance metadata")

class IngestionRequest(BaseModel):
    source_file_path: str
    source_type: str
    case_id: Optional[str] = None

class IngestionResponse(BaseModel):
    source_type: str
    record_count: int
    records: List[NormalizedRecord]
