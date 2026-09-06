import json
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')

with engine.connect() as conn:
    print("Mentions:", conn.execute(text("SELECT count(*) FROM entity_mentions")).scalar())
    print("Assertions:", conn.execute(text("SELECT count(*) FROM relationship_assertions")).scalar())
    print("Evidence:", conn.execute(text("SELECT count(*) FROM evidence")).scalar())
    print("Observations:", conn.execute(text("SELECT count(*) FROM observations")).scalar())
    print("Source Records:", conn.execute(text("SELECT count(*) FROM source_records")).scalar())
    
    print("\nEvidence schema:")
    for row in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='evidence'")):
        print(row[0])
