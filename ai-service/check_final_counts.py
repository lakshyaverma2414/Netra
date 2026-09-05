from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    print("Mentions:")
    print(conn.execute(text("SELECT COUNT(*) FROM entity_mentions;")).fetchone()[0])
    print("Entities:")
    print(conn.execute(text("SELECT COUNT(*) FROM entities;")).fetchone()[0])
    print("Relationship Assertions:")
    print(conn.execute(text("SELECT COUNT(*) FROM relationship_assertions;")).fetchone()[0])
    print("Relationships:")
    print(conn.execute(text("SELECT COUNT(*) FROM relationships;")).fetchone()[0])
