import pytest
import os
import json
import time
import uuid
from sqlalchemy.orm import Session
from app.db.database import get_db, engine
from app.db.models import Base, Case, SourceSystem, SourceDataset, SourceRecord, Event, RelationshipAssertion, Evidence, DerivedArtifact, Observation, Entity, Relationship, EntityMention
from app.ingestion.core.source_registry import initialize_registry
from app.api.ingestion import ingest_structured_batch, ingest_unstructured_evidence, StructuredBatchRequest, UnstructuredEvidenceRequest
from datetime import datetime, timezone

def ensure_test_case(db: Session, case_id: str):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        case = Case(
            case_id=case_id,
            case_number=f"{case_id}-NO",
            title="E2E Demo Investigation",
            status="ACTIVE",
            opened_at=datetime.now(timezone.utc)
        )
        db.add(case)
        db.commit()

def test_phase3_orchestration_e2e(tmp_path):
    db = next(get_db())
    case_id = f"C-DEMO-{int(time.time())}"
    ensure_test_case(db, case_id)
    initialize_registry(db)
    
    unique_run = str(uuid.uuid4())[:8]
    
    # 1. FIR (Unstructured JSON via FileConnector/Pipeline mapping mocked inside)
    # Since unstructured routes through 'process_unstructured_evidence', we will create a text file mimicking it
    fir_path = str(tmp_path / "fir_report.txt")
    with open(fir_path, 'wb') as f: f.write(b"FIR: Vikram Singh owns 987-111-2222.")
    
    # We route it as TXT to hit unstructured_pipeline.py which parses text
    req_fir = UnstructuredEvidenceRequest(filepath=fir_path, file_type="TXT", case_id=case_id)
    resp = ingest_unstructured_evidence(req_fir, db)
    assert resp["status"] == "success"
    
    # 2. CDR (Structured)
    cdr_data = [
        {"caller_number": "987-111-2222", "receiver_number": "555-999-0000", "duration": "120", "call_time": "2026-08-01T10:00:00Z"},
        {"caller_number": "987-111-2222", "receiver_number": "111-222-3333", "duration": "45", "call_time": "2026-08-01T11:00:00Z"}
    ]
    cdr_path = str(tmp_path / "cdr.json")
    with open(cdr_path, 'w') as f: json.dump(cdr_data, f)
    
    req_cdr = StructuredBatchRequest(filepath=cdr_path, file_type="JSON", system_id="SYS_FINANCIAL_DEMO", dataset_id="NETRA-DEMO-CDR", case_id=case_id)
    ingest_structured_batch(req_cdr, db)
    
    # 3. TXN (Structured)
    txn_data = [
        {"sender_account": "ACCT-AMIT", "receiver_account": "ACCT-RAJ", "amount": "50000", "timestamp": "2026-08-02T10:00:00Z"}
    ]
    txn_path = str(tmp_path / "txn.json")
    with open(txn_path, 'w') as f: json.dump(txn_data, f)
    req_txn = StructuredBatchRequest(filepath=txn_path, file_type="JSON", system_id="SYS_FINANCIAL_DEMO", dataset_id="NETRA-DEMO-TXN", case_id=case_id)
    ingest_structured_batch(req_txn, db)
    
    # 3b. UNSUPPORTED SCHEMA (Vehicle or anything not in schema_mapper)
    veh_data = [{"vehicle_number": "KA-01", "owner": "Unknown"}]
    veh_path = str(tmp_path / "veh.json")
    with open(veh_path, 'w') as f: json.dump(veh_data, f)
    req_veh = StructuredBatchRequest(filepath=veh_path, file_type="JSON", system_id="SYS_VEHICLE", dataset_id="NETRA-UNKNOWN", case_id=case_id)
    ingest_structured_batch(req_veh, db)
    # Check it was marked UNSUPPORTED
    bad_rec = db.query(SourceRecord).filter(SourceRecord.dataset_id == "NETRA-UNKNOWN").first()
    assert bad_rec.processing_status == "UNSUPPORTED_DATASET_TYPE"
    
    # 4. Multimedia (Image, Audio, Video)
    img_path = str(tmp_path / "surveillance.jpg")
    audio_path = str(tmp_path / "wiretap.wav")
    video_path = str(tmp_path / "cctv.mp4")
    
    for p in [img_path, audio_path, video_path]:
        with open(p, 'wb') as f: f.write(os.urandom(1024)) # Dummy media bytes
        
    ingest_unstructured_evidence(UnstructuredEvidenceRequest(filepath=img_path, file_type="IMAGE", case_id=case_id), db)
    ingest_unstructured_evidence(UnstructuredEvidenceRequest(filepath=audio_path, file_type="AUDIO", case_id=case_id), db)
    ingest_unstructured_evidence(UnstructuredEvidenceRequest(filepath=video_path, file_type="VIDEO", case_id=case_id), db)
    
    # VERIFICATION
    # Check that Canonical Relationships exist in PostgreSQL
    rels = db.query(Relationship).all()
    assert len(rels) > 0
    
    # Verify provenance exists for at least one assertion
    assertion = db.query(RelationshipAssertion).first()
    assert assertion is not None
    # We must have either an observation_id or document_chunk_id or source_record_id
    assert assertion.source_record_id is not None or assertion.observation_id is not None
    
    # Idempotency test
    init_rec_count = db.query(SourceRecord).filter(SourceRecord.dataset_id == "NETRA-DEMO-CDR").count()
    ingest_structured_batch(req_cdr, db)
    final_rec_count = db.query(SourceRecord).filter(SourceRecord.dataset_id == "NETRA-DEMO-CDR").count()
    
    assert init_rec_count == final_rec_count # No duplicates created
