from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='source_datasets'")).fetchall()
    print("source_datasets cols:", [c[0] for c in cols])
    
    rows = conn.execute(text("SELECT * FROM source_datasets LIMIT 5")).fetchall()
    print("rows:", rows)
    
    sys_cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='source_systems'")).fetchall()
    print("source_systems cols:", [c[0] for c in sys_cols])
    
    sys_rows = conn.execute(text("SELECT * FROM source_systems LIMIT 5")).fetchall()
    print("sys rows:", sys_rows)
