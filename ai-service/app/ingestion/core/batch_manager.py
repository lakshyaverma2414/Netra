import uuid
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.models import IngestionBatch, IngestionStatus

logger = logging.getLogger(__name__)

class BatchManager:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, dataset_id: str, case_id: str, original_filename: str, file_type: str, file_hash: str) -> IngestionBatch:
        batch = IngestionBatch(
            batch_id=uuid.uuid4(),
            dataset_id=dataset_id,
            case_id=case_id,
            original_filename=original_filename,
            file_type=file_type,
            file_hash=file_hash,
            status=IngestionStatus.PROCESSING
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def update_batch_stats(self, batch_id: uuid.UUID, received: int = 0, failed: int = 0, complete: bool = False):
        batch = self.db.query(IngestionBatch).filter(IngestionBatch.batch_id == batch_id).first()
        if not batch:
            return
        
        batch.records_received += received
        batch.records_failed += failed
        
        if complete:
            if batch.records_failed == 0:
                batch.status = IngestionStatus.COMPLETED
            elif batch.records_failed < batch.records_received:
                batch.status = IngestionStatus.PARTIAL_SUCCESS
            else:
                batch.status = IngestionStatus.FAILED
            batch.completed_at = datetime.now(timezone.utc)
            
        self.db.commit()
        
    def fail_batch(self, batch_id: uuid.UUID, error_msg: str):
        batch = self.db.query(IngestionBatch).filter(IngestionBatch.batch_id == batch_id).first()
        if batch:
            batch.status = IngestionStatus.FAILED
            batch.error_details = error_msg
            batch.completed_at = datetime.now(timezone.utc)
            self.db.commit()
