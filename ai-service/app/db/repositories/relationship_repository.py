from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.db.models import Relationship, RelationshipAssertion, RelationshipCase, RelationshipAssertionLink

class RelationshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_canonical(self, relationship_id: str, source_entity_id: str, relationship_type: str, target_entity_id: str, status: str = 'NEEDS_REVIEW') -> Relationship:
        rel = Relationship(
            relationship_id=relationship_id,
            source_entity_id=source_entity_id,
            relationship_type=relationship_type,
            target_entity_id=target_entity_id,
            status=status
        )
        self.db.add(rel)
        self.db.flush()
        return rel

    def get_by_id(self, relationship_id: str) -> Optional[Relationship]:
        return self.db.query(Relationship).filter(Relationship.relationship_id == relationship_id).first()

    def find_existing(self, source: str, type: str, target: str) -> Optional[Relationship]:
        return self.db.query(Relationship).filter(
            Relationship.source_entity_id == source,
            Relationship.relationship_type == type,
            Relationship.target_entity_id == target
        ).first()

    def add_case_context(self, relationship_id: str, case_id: str):
        rc = RelationshipCase(
            relationship_id=relationship_id,
            case_id=case_id
        )
        self.db.merge(rc) # Idempotent associate
        self.db.flush()
        return rc

    def list_by_case(self, case_id: str) -> List[Relationship]:
        return self.db.query(Relationship).join(RelationshipCase).filter(RelationshipCase.case_id == case_id).all()

class AssertionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, source_entity_id: str, target_entity_id: str, relationship_type: str, status: str, source_record_id: str = None) -> RelationshipAssertion:
        assertion = RelationshipAssertion(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            status=status,
            source_record_id=source_record_id
        )
        self.db.add(assertion)
        self.db.flush()
        return assertion
        
    def link_assertion(self, relationship_id: str, assertion_id: str):
        link = RelationshipAssertionLink(relationship_id=relationship_id, assertion_id=assertion_id)
        self.db.merge(link)
        self.db.flush()
