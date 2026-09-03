from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.db.models import Entity, EntityAlias, EntityMention, CaseEntity

class EntityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity_id: str, entity_type: str, canonical_name: str, normalized_value: str, resolution_status: str = 'UNRESOLVED', resolution_score: float = None) -> Entity:
        entity = Entity(
            entity_id=entity_id,
            entity_type=entity_type,
            canonical_name=canonical_name,
            normalized_value=normalized_value,
            resolution_status=resolution_status,
            resolution_score=resolution_score
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def get_by_id(self, entity_id: str) -> Optional[Entity]:
        return self.db.query(Entity).filter(Entity.entity_id == entity_id).first()

    def find_by_normalized_identifier(self, normalized_value: str) -> Optional[Entity]:
        return self.db.query(Entity).filter(Entity.normalized_value == normalized_value).first()

    def list_by_case(self, case_id: str) -> List[Entity]:
        return self.db.query(Entity).join(CaseEntity).filter(CaseEntity.case_id == case_id).all()

    def add_alias(self, entity_id: str, alias: str, normalized_alias: str):
        ea = EntityAlias(
            entity_id=entity_id,
            alias=alias,
            normalized_alias=normalized_alias
        )
        self.db.add(ea)
        self.db.flush()
        return ea
        
    def add_mention(self, mention_id: str, entity_type: str, extracted_text: str, normalized_value: str, method: str, source_record_id: str = None):
        em = EntityMention(
            mention_id=mention_id,
            entity_type=entity_type,
            extracted_text=extracted_text,
            normalized_value=normalized_value,
            extraction_method=method,
            source_record_id=source_record_id
        )
        self.db.add(em)
        self.db.flush()
        return em
