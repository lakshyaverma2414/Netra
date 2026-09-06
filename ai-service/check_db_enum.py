from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    res = conn.execute(text("""
        SELECT enum_range(NULL::entity_type_enum)
    """)).fetchall()
    print("DB entity_type_enum:", res)
