import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Evidence

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
Session = sessionmaker(bind=engine)
db = Session()

evs = db.query(Evidence).filter(Evidence.case_id.in_([f"C-{i:03d}" for i in range(1,11)])).all()
for e in evs:
    print(e.storage_uri)
