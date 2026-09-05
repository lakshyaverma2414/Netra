from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Evidence, ProcessingRun, DerivedArtifact, Observation

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
Session = sessionmaker(bind=engine)
db = Session()

evs = db.query(Evidence).filter(Evidence.case_id == "C-003").all()
print(f"Total Evidence in C-003: {len(evs)}")

runs = db.query(ProcessingRun).join(Evidence, ProcessingRun.input_batch_id == Evidence.evidence_id, isouter=True).all()
# Actually ProcessingRun is tied to batch_id. We can just count total runs for C-003 by batch.
# For simplicity let's just count Observations.
obs = db.query(Observation).join(DerivedArtifact).join(Evidence).filter(Evidence.case_id == "C-003").all()
print(f"Total Observations in C-003: {len(obs)}")

