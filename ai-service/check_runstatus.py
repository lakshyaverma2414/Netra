from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    res = conn.execute(text("SELECT column_name, data_type, udt_name FROM information_schema.columns WHERE table_name = 'processing_runs' AND column_name = 'status';"))
    for row in res:
        print(row)
