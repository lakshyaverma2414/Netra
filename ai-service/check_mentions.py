from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    print("Mentions:")
    for row in conn.execute(text("SELECT COUNT(*) FROM entity_mentions;")):
        print(row)
    print("Entities:")
    for row in conn.execute(text("SELECT COUNT(*) FROM entities;")):
        print(row)
