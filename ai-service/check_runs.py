from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    for row in conn.execute(text("SELECT status, COUNT(*) FROM processing_runs GROUP BY status;")):
        print(row)
