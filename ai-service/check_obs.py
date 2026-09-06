from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    res = conn.execute(text("SELECT observation_id, case_id, evidence_id FROM observations LIMIT 5")).fetchall()
    for r in res:
        print(r)
