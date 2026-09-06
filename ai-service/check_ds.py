from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    ds = conn.execute(text("SELECT dataset_id, name FROM source_datasets LIMIT 10")).fetchall()
    print("source_datasets:", ds)
    
    ss = conn.execute(text("SELECT system_id, name FROM source_systems LIMIT 10")).fetchall()
    print("source_systems:", ss)
