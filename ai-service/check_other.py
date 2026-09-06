from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    print("Observations:", conn.execute(text("SELECT count(*) FROM observations")).fetchone()[0])
    print("Evidence:", conn.execute(text("SELECT count(*) FROM evidence")).fetchone()[0])
    print("Documents:", conn.execute(text("SELECT count(*) FROM documents")).fetchone()[0])
    print("Findings:", conn.execute(text("SELECT count(*) FROM findings")).fetchone()[0])
