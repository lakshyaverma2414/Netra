from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.db.models import Case, CaseEntity, Entity, CaseStatus, CaseLink

class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, case_id: str, case_number: str, title: str, description: str = None) -> Case:
        db_case = Case(
            case_id=case_id,
            case_number=case_number,
            title=title,
            description=description,
            status=CaseStatus.ACTIVE
        )
        self.db.add(db_case)
        self.db.flush()
        return db_case

    def get_by_id(self, case_id: str) -> Optional[Case]:
        return self.db.query(Case).filter(Case.case_id == case_id).first()

    def list_accessible_cases(self, limit: int = 100) -> List[Case]:
        return self.db.query(Case).limit(limit).all()

    def add_entity(self, case_id: str, entity_id: str, association_type: str = 'ASSOCIATED', confidence: float = 1.0):
        ce = CaseEntity(
            case_id=case_id,
            entity_id=entity_id,
            association_type=association_type,
            confidence=confidence
        )
        self.db.merge(ce)  # Safe upsert
        self.db.flush()
        return ce

    def get_case_entities(self, case_id: str) -> List[Entity]:
        return self.db.query(Entity).join(CaseEntity).filter(CaseEntity.case_id == case_id).all()
