from app.db.database import SessionLocal
from app.db.models import Finding
db = SessionLocal()
findings = db.query(Finding).all()
for f in findings:
    if f.status != "NEW":
        print(f"Finding {f.finding_id} status is {f.status}")
