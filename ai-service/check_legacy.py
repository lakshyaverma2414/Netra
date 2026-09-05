from app.db.database import get_db
from app.db.models import Case, Relationship

db = next(get_db())
cases = db.query(Case).filter(Case.case_id.in_(["C-001", "C-002"])).all()
print("Cases:", [c.case_id for c in cases])

r_bad = db.query(Relationship).filter(Relationship.relationship_id == "R-BAD-001").first()
print("R-BAD-001:", r_bad.relationship_id if r_bad else None, r_bad.status.name if r_bad else None)
