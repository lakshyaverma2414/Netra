from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    conn.execute(text("UPDATE cases SET created_by = 'a94bc25d-a504-4e60-adec-b627d7d3818b' WHERE case_id LIKE 'C-0%';"))
    conn.commit()
    print("Updated cases.")
