from app.db.database import SessionLocal
from app.db.models import EvidenceRelationship, RelationshipAssertionLink
db = SessionLocal()
er = db.query(EvidenceRelationship).all()
ral = db.query(RelationshipAssertionLink).all()
print(f"EvidenceRelationship count: {len(er)}")
print(f"RelationshipAssertionLink count: {len(ral)}")
