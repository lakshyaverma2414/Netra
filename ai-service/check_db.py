from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    res = conn.execute(text("SELECT status, count(*) FROM relationship_assertions GROUP BY status")).fetchall()
    print("Assertion Statuses:", res)
    res2 = conn.execute(text("SELECT count(*) FROM relationships")).scalar()
    print("Canonical Relationships:", res2)
