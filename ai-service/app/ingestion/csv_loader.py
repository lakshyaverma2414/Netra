import csv
from typing import List
from pathlib import Path
from app.schemas.ingestion import NormalizedRecord, IngestionMetadata
from app.ingestion.normalizer import normalize_phone

def load_cdr(filepath: str, case_id: str = None) -> List[NormalizedRecord]:
    records = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record_id = row.get('evidence_id', '')
            data = {
                'caller': normalize_phone(row.get('caller', '')),
                'receiver': normalize_phone(row.get('receiver', '')),
                'timestamp': row.get('timestamp', ''),
                'duration': row.get('duration', '')
            }
            rec = NormalizedRecord(
                record_id=record_id,
                source_type="CDR",
                case_id=case_id,
                content_type="STRUCTURED",
                data=data,
                metadata=IngestionMetadata(source_file=Path(filepath).name)
            )
            records.append(rec)
    return records

def load_transaction(filepath: str, case_id: str = None) -> List[NormalizedRecord]:
    records = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record_id = row.get('evidence_id', '')
            data = {
                'sender_account': row.get('sender_account', ''),
                'receiver_account': row.get('receiver_account', ''),
                'amount': row.get('amount', ''),
                'timestamp': row.get('timestamp', '')
            }
            rec = NormalizedRecord(
                record_id=record_id,
                source_type="TRANSACTION",
                case_id=case_id,
                content_type="STRUCTURED",
                data=data,
                metadata=IngestionMetadata(source_file=Path(filepath).name)
            )
            records.append(rec)
    return records
