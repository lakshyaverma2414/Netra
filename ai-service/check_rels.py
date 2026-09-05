from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    res = conn.execute(text("SELECT relationship_type, status FROM relationship_assertions;")).fetchall()
    print("Assertions:", res)
    res = conn.execute(text("SELECT relationship_type, status FROM relationships;")).fetchall()
    print("Relationships:", res)
