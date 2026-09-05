from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    res = conn.execute(text("SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c JOIN pg_class t ON c.conrelid = t.oid WHERE t.relname = 'entity_mentions' AND c.contype = 'c';"))
    for row in res:
        print(row[0])
