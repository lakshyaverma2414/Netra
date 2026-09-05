from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Evidence

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
Session = sessionmaker(bind=engine)
db = Session()

evs = db.query(Evidence).filter(Evidence.case_id == "C-003").all()
for e in evs:
    print(e.storage_uri)
