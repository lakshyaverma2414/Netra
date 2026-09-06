import logging
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import Observation, Event, RelationshipAssertion, Relationship, ValidationStatus
from app.schemas.resolution import ResolutionRequest, MentionInput, ResolutionStatusEnum
from app.services.resolution_service import resolve_mentions
from app.schemas.validation import ValidationRequest, ValidationStatusEnum
from app.services.validation_service import validate_relationship

logger = logging.getLogger(__name__)

class IngestionOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        
    def process_observation(self, observation: Observation, case_id: str, mocked_mentions: List[MentionInput] = None, mocked_assertions: List[Dict] = None):
        """
        Routes an Observation through the existing AI Intelligence pipeline:
        1. Observation -> Entity Mentions (Mocked for Demo or via Qwen/Spacy)
        2. Resolve Mentions (using existing resolution_service)
        3. Observation -> Relationship Assertions (using existing Qwen logic, mocked here for E2E speed/deterministic tests)
        4. Validate Assertions (using existing validation_service)
        """
        
        # 1 & 2. Entities
        if mocked_mentions:
            req = ResolutionRequest(case_id=case_id, mentions=mocked_mentions)
            # This calls the existing NETRA ER system which returns CONFIRMED/PROBABLE etc.
            # and persists EntityMention -> EntityResolutionLog -> Entity
            res_response = resolve_mentions(self.db, req)
            
            # Create a lookup for resolved entities
            resolved_map = {}
            for res_item in res_response.results:
                if res_item.entity_id:
                    resolved_map[res_item.mention] = res_item.entity_id
                    
            # 3 & 4. Relationships
            if mocked_assertions:
                for ma in mocked_assertions:
                    src_ent_id = resolved_map.get(ma["source_mention"]) or ma.get("source_fallback")
                    tgt_ent_id = resolved_map.get(ma["target_mention"]) or ma.get("target_fallback")
                    
                    if not src_ent_id or not tgt_ent_id:
                        continue
                        
                    # Create the Assertion (from Qwen step conceptually)
                    assertion = RelationshipAssertion(
                        assertion_id=uuid.uuid4(),
                        source_entity_id=src_ent_id,
                        target_entity_id=tgt_ent_id,
                        relationship_type=ma["type"],
                        source_record_id=observation.source_record_id,
                        observation_id=observation.observation_id,
                        evidence_text=observation.raw_text,
                        extraction_method="Orchestrator",
                        extraction_confidence=0.9,
                        status="CANDIDATE"
                    )
                    self.db.add(assertion)
                    self.db.commit()
                    self.db.refresh(assertion)
                    
                    # Call existing Validation Service
                    val_req = ValidationRequest(
                        assertion_id=str(assertion.assertion_id),
                        case_id=case_id,
                        source_entity_id=src_ent_id,
                        relationship_type=ma["type"],
                        target_entity_id=tgt_ent_id,
                        extracted_text=observation.raw_text,
                        source_record_id=observation.source_record_id or ma.get("evidence_id"),
                        evidence_ids=[str(observation.source_record_id)] if observation.source_record_id else
                                     ([ma["evidence_id"]] if ma.get("evidence_id") else [])
                    )
                    
                    val_resp = validate_relationship(self.db, val_req)
                    
                    if val_resp.status == ValidationStatusEnum.CONFIRMED:
                        # Convert to canonical relationship
                        existing = self.db.query(Relationship).filter(
                            Relationship.source_entity_id == src_ent_id,
                            Relationship.target_entity_id == tgt_ent_id,
                            Relationship.relationship_type == ma["type"]
                        ).first()
                        
                        if not existing:
                            rel = Relationship(
                                relationship_id=f"R-{uuid.uuid4().hex[:8]}",
                                source_entity_id=src_ent_id,
                                relationship_type=ma["type"],
                                target_entity_id=tgt_ent_id,
                                status=ValidationStatus.CONFIRMED,
                                confidence=0.95
                            )
                            self.db.add(rel)
                            self.db.commit()
                    
                    # Note: Error handling and batch status aggregation omitted for brevity but conceptually tracked here.
