from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    # Check relationships and their case links
    res = conn.execute(text("""
        SELECT r.relationship_id, r.relationship_type, r.source_entity_id, r.target_entity_id, rc.case_id
        FROM relationships r
        LEFT JOIN relationship_cases rc ON r.relationship_id = rc.relationship_id
        LIMIT 20;
    """)).fetchall()
    print("Relationships with case links:")
    for row in res:
        print(row)
    
    # Check case_entities
    res2 = conn.execute(text("SELECT case_id, entity_id FROM case_entities LIMIT 20;")).fetchall()
    print("\nCase-Entity links:")
    for row in res2:
        print(row)
