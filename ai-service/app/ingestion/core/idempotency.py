import hashlib
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import SourceRecord

logger = logging.getLogger(__name__)

def generate_record_hash(system_id: str, dataset_id: str, external_id: str = None, payload: dict = None) -> str:
    """
    Generates a deterministic identity hash for idempotency.
    Prefers external_id if available, otherwise falls back to a payload hash.
    """
    if external_id:
        seed_string = f"{system_id}::{dataset_id}::{external_id}"
    else:
        # Fallback to payload hashing. Must sort keys for determinism.
        canonical_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        seed_string = f"{system_id}::{dataset_id}::PAYLOAD::{canonical_payload}"
        
    return hashlib.sha256(seed_string.encode('utf-8')).hexdigest()

def upsert_source_record(db: Session, record_obj: SourceRecord) -> tuple[SourceRecord, bool]:
    """
    Attempts to insert a SourceRecord. If it already exists (by dataset_id + record_hash),
    it updates the existing record instead of creating a duplicate.
    Returns (record, is_new).
    """
    existing = db.query(SourceRecord).filter(
        SourceRecord.dataset_id == record_obj.dataset_id,
        SourceRecord.source_hash == record_obj.source_hash
    ).first()
    
    if existing:
        # Upsert: update existing with new batch and processing status
        existing.batch_id = record_obj.batch_id
        existing.raw_payload = record_obj.raw_payload
        existing.normalized_payload = record_obj.normalized_payload
        existing.processing_status = record_obj.processing_status  # Preserve status from pipeline
        db.commit()
        db.refresh(existing)
        return existing, False
    else:
        try:
            db.add(record_obj)
            db.commit()
            db.refresh(record_obj)
            return record_obj, True
        except IntegrityError:
            db.rollback()
            # Concurrent insertion fallback
            return upsert_source_record(db, record_obj)
