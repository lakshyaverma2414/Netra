import logging
import uuid
import hashlib
import os
from sqlalchemy.orm import Session
from app.db.models import Evidence, DerivedArtifact, Observation, ProcessingRun
from app.schemas.extraction import EntityTypeEnum
from app.schemas.resolution import MentionInput
from app.ingestion.core.batch_manager import BatchManager
from app.ingestion.core.orchestrator import IngestionOrchestrator
from app.llm.qwen_client import extract_relationships_with_qwen

logger = logging.getLogger(__name__)

def extract_text_from_file(filepath: str, file_type: str) -> str:
    """Basic text extraction mock/stub for supported types."""
    if file_type == 'TXT':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    # In a real system, we'd use PyPDF2/pdfplumber for PDF, Tesseract for IMAGE
    return ""

def process_unstructured_evidence(db: Session, batch_id: uuid.UUID, filepath: str, file_type: str, case_id: str):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    ev_hash = h.hexdigest()
    
    ev = db.query(Evidence).filter(Evidence.file_hash == ev_hash).first()
    if not ev:
        ev = Evidence(
            evidence_id=str(uuid.uuid4()),
            case_id=case_id,
            evidence_type=file_type,
            storage_uri=filepath,
            file_hash=ev_hash,
            provenance_status='VERIFIED'
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        
    bm = BatchManager(db)
    
    # 1. Multimedia handling
    if file_type in ['AUDIO', 'VIDEO', 'IMAGE']:
        # We don't have CV / ASR models loaded. Register and stop.
        run = ProcessingRun(
            run_id=uuid.uuid4(),
            pipeline_name=f"{file_type}_EXTRACTOR",
            pipeline_version="1.0",
            model_version="mock-1.0",
            input_batch_id=batch_id,
            status="NOT_SUPPORTED_YET"
        )
        db.add(run)
        db.commit()
        bm.update_batch_stats(batch_id, received=1, failed=0, complete=True)
        return
        
    # 2. Text/Document handling
    raw_text = extract_text_from_file(filepath, file_type)
    if not raw_text.strip():
        # Empty or unsupported parsing
        run = ProcessingRun(
            run_id=uuid.uuid4(),
            pipeline_name=f"{file_type}_EXTRACTOR",
            pipeline_version="1.0",
            model_version="parser-1.0",
            input_batch_id=batch_id,
            status="NEEDS_REVIEW"
        )
        db.add(run)
        db.commit()
        bm.update_batch_stats(batch_id, received=1, failed=1, complete=True)
        return

    # 3. Successful Extraction
    run = ProcessingRun(
        run_id=uuid.uuid4(),
        pipeline_name=f"{file_type}_EXTRACTOR",
        pipeline_version="1.0",
        model_version="qwen-1.0",
        input_batch_id=batch_id,
        status="SUCCESS"
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    art = DerivedArtifact(
        artifact_id=uuid.uuid4(),
        evidence_id=ev.evidence_id,
        processing_run_id=run.run_id,
        artifact_type="EXTRACTED_TEXT",
        storage_uri=f"/mock/derived/{ev.evidence_id}.txt",
        artifact_hash=hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
    )
    db.add(art)
    
    obs = Observation(
        observation_id=uuid.uuid4(),
        derived_artifact_id=art.artifact_id,
        processing_run_id=run.run_id,
        observation_type="NLP_TEXT",
        raw_text=raw_text,
        extraction_confidence=1.0
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)

    # 4. Invoke Real Qwen Extraction
    llm_response = extract_relationships_with_qwen(raw_text)
    if llm_response and llm_response.relationships:
        logger.info(f"Qwen extracted {len(llm_response.relationships)} relationships from {filepath}")
        mentions = []
        assertions = []
        orchestrator = IngestionOrchestrator(db)
        
        for rel in llm_response.relationships:
            try:
                src_type = EntityTypeEnum(rel.source_type)
            except ValueError:
                src_type = EntityTypeEnum.PERSON
            try:
                tgt_type = EntityTypeEnum(rel.target_type)
            except ValueError:
                tgt_type = EntityTypeEnum.PERSON
                
            mentions.append(MentionInput(
                text=rel.source_text,
                entity_type=src_type,
                source_record_id=None,  # entity_mentions FK → source_records; not evidence
                observation_id=str(obs.observation_id)
            ))
            mentions.append(MentionInput(
                text=rel.target_text,
                entity_type=tgt_type,
                source_record_id=None,  # entity_mentions FK → source_records; not evidence
                observation_id=str(obs.observation_id)
            ))
            assertions.append({
                "source_mention": rel.source_text,
                "target_mention": rel.target_text,
                "type": rel.relationship_type.name if hasattr(rel.relationship_type, 'name') else str(rel.relationship_type),
                "evidence_id": ev.evidence_id,
            })
            
        if assertions:
            orchestrator.process_observation(obs, case_id, mentions, assertions)
    else:
        logger.warning(f"Qwen returned no relationships for {filepath}")

    bm.update_batch_stats(batch_id, received=1, failed=0, complete=True)


