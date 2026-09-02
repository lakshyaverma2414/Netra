import json
from typing import List
from pathlib import Path
from app.schemas.ingestion import NormalizedRecord, IngestionMetadata
from app.ingestion.normalizer import normalize_text, normalize_vehicle

def load_fir(filepath: str, case_id: str = None) -> List[NormalizedRecord]:
    records = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
        for item in data:
            rec = NormalizedRecord(
                record_id=item.get('evidence_id', ''),
                source_type="FIR",
                case_id=case_id,
                content_type="TEXT",
                text=normalize_text(item.get('text', '')),
                metadata=IngestionMetadata(source_file=Path(filepath).name)
            )
            records.append(rec)
    return records

def load_surveillance(filepath: str, case_id: str = None) -> List[NormalizedRecord]:
    records = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
        for item in data:
            if 'vehicle_number' in item:
                item['vehicle_number'] = normalize_vehicle(item['vehicle_number'])
            if 'notes' in item:
                item['notes'] = normalize_text(item['notes'])
            
            rec = NormalizedRecord(
                record_id=item.get('evidence_id', ''),
                source_type="SURVEILLANCE",
                case_id=case_id,
                content_type="SEMI_STRUCTURED",
                data=item,
                metadata=IngestionMetadata(source_file=Path(filepath).name)
            )
            records.append(rec)
    return records
