import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Evidence, Relationship, Entity, Observation

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
Session = sessionmaker(bind=engine)
db = Session()

evidence_count = db.query(Evidence).count()
entities_count = db.query(Entity).count()
rels_count = db.query(Relationship).count()
obs_count = db.query(Observation).count()

print(f"Total Evidence: {evidence_count}")
print(f"Total Entities: {entities_count}")
print(f"Total Relationships: {rels_count}")
print(f"Total Observations: {obs_count}")
