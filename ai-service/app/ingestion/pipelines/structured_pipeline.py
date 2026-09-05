import logging
from sqlalchemy.orm import Session
from app.db.models import SourceRecord, Event, Observation
from app.schemas.extraction import EntityTypeEnum
from app.schemas.resolution import MentionInput
from app.ingestion.core.idempotency import generate_record_hash, upsert_source_record
from app.ingestion.mappers.schema_mapper import SchemaMapper
from app.ingestion.mappers.validators import validate_record
from app.ingestion.core.batch_manager import BatchManager
from app.ingestion.core.orchestrator import IngestionOrchestrator
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

def process_structured_batch(db: Session, batch_id: uuid.UUID, system_id: str, dataset_id: str, case_id: str, raw_records: list):
    batch_mgr = BatchManager(db)
    orchestrator = IngestionOrchestrator(db)
    received = 0
    failed = 0
    
    for raw in raw_records:
        received += 1
        rec_hash = generate_record_hash(system_id, dataset_id, payload=raw)
        
        try:
            normalized = SchemaMapper.map_record(dataset_id, raw)
            is_valid, err = validate_record(dataset_id, normalized)
            proc_status = 'COMPLETED' if is_valid else 'QUARANTINE'
        except Exception as e:
            if "UNSUPPORTED_DATASET_TYPE" in str(e):
                normalized = None
                is_valid = False
                proc_status = 'UNSUPPORTED_DATASET_TYPE'
            else:
                raise
        
        rec = SourceRecord(
            record_id=str(uuid.uuid4()),
            batch_id=batch_id,
            dataset_id=dataset_id,
            case_id=case_id,
            source_type="STRUCTURED",
            raw_payload=raw,
            normalized_payload=normalized if is_valid else None,
            source_hash=rec_hash,
            schema_version="1.0",
            processing_status=proc_status
        )
        
        saved_rec, is_new = upsert_source_record(db, rec)
        if not is_valid:
            failed += 1
            continue
            
        # Create a proxy Observation for structured data to unify pipeline
        obs = Observation(
            observation_id=uuid.uuid4(),
            source_record_id=saved_rec.record_id,
            observation_type="STRUCTURED_RECORD",
            raw_text=str(normalized)
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)
            
        if "DEMO-CDR" in dataset_id:
            src_phone = normalized.get("source_entity")
            tgt_phone = normalized.get("target_entity")
            
            mentions = [
                MentionInput(text=src_phone, entity_type=EntityTypeEnum.PHONE, source_record_id=saved_rec.record_id, observation_id=str(obs.observation_id)),
                MentionInput(text=tgt_phone, entity_type=EntityTypeEnum.PHONE, source_record_id=saved_rec.record_id, observation_id=str(obs.observation_id))
            ]
            assertions = [
                {"source_mention": src_phone, "target_mention": tgt_phone, "type": "COMMUNICATES_WITH", "source_fallback": None, "target_fallback": None}
            ]
            
            orchestrator.process_observation(obs, case_id, mentions, assertions)
            
            ev = Event(
                event_id=str(uuid.uuid4()),
                case_id=case_id,
                event_type="PHONE_CALL",
                source_record_id=saved_rec.record_id,
                description=f"Call from {src_phone} to {tgt_phone}"
            )
            db.add(ev)
            db.commit()

        elif "DEMO-TXN" in dataset_id:
            src_acct = normalized.get("source_entity")
            tgt_acct = normalized.get("target_entity")
            mentions = [
                MentionInput(text=src_acct, entity_type=EntityTypeEnum.ACCOUNT, source_record_id=saved_rec.record_id, observation_id=str(obs.observation_id)),
                MentionInput(text=tgt_acct, entity_type=EntityTypeEnum.ACCOUNT, source_record_id=saved_rec.record_id, observation_id=str(obs.observation_id))
            ]
            assertions = [
                {"source_mention": src_acct, "target_mention": tgt_acct, "type": "TRANSFERRED_TO"}
            ]
            orchestrator.process_observation(obs, case_id, mentions, assertions)
            
            ev = Event(
                event_id=str(uuid.uuid4()),
                case_id=case_id,
                event_type="TRANSACTION",
                source_record_id=saved_rec.record_id,
                description=f"Txn from {src_acct} to {tgt_acct}"
            )
            db.add(ev)
            db.commit()

    batch_mgr.update_batch_stats(batch_id, received=received, failed=failed, complete=True)
