from app.db.database import SessionLocal
from app.db.models import RelationshipAssertionLink
db = SessionLocal()
links = db.query(RelationshipAssertionLink).filter_by(relationship_id="R-009").all()
print(f"R-009 links: {len(links)}")
