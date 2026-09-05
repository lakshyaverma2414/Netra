from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import RelationshipAssertion

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
Session = sessionmaker(bind=engine)
db = Session()

assertion = db.query(RelationshipAssertion).first()
if assertion:
    print("Assertion source_record_id:", assertion.source_record_id)
