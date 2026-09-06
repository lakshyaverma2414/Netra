from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    print("=== Sample REJECTED assertions with reasons ===")
    r = conn.execute(text("""
        SELECT ra.relationship_type, 
               e1.entity_type as src_type, e1.canonical_name as src,
               e2.entity_type as tgt_type, e2.canonical_name as tgt,
               ra.status,
               ra.evidence_text
        FROM relationship_assertions ra
        JOIN entities e1 ON ra.source_entity_id = e1.entity_id
        JOIN entities e2 ON ra.target_entity_id = e2.entity_id
        LIMIT 20
    """)).fetchall()
    for row in r:
        print(f"  [{row[5]}] {row[2]}({row[1]}) --[{row[0]}]--> {row[4]}({row[3]})")

    print("\n=== NEEDS_REVIEW assertions ===")
    r2 = conn.execute(text("""
        SELECT ra.relationship_type,
               e1.entity_type as src_type, e1.canonical_name as src,
               e2.entity_type as tgt_type, e2.canonical_name as tgt,
               ra.source_record_id
        FROM relationship_assertions ra
        JOIN entities e1 ON ra.source_entity_id = e1.entity_id
        JOIN entities e2 ON ra.target_entity_id = e2.entity_id
        WHERE ra.status = 'NEEDS_REVIEW'
    """)).fetchall()
    for row in r2:
        print(f"  {row[2]}({row[1]}) --[{row[0]}]--> {row[4]}({row[3]}) | src_record={row[5]}")

    print("\n=== Distinct relationship types attempted ===")
    r3 = conn.execute(text("""
        SELECT relationship_type, status, count(*) 
        FROM relationship_assertions 
        GROUP BY relationship_type, status 
        ORDER BY count(*) DESC
    """)).fetchall()
    for row in r3:
        print(f"  {row[0]}: {row[1]} x{row[2]}")

    print("\n=== Entity type distribution ===")
    r4 = conn.execute(text("SELECT entity_type, count(*) FROM entities GROUP BY entity_type ORDER BY count(*) DESC")).fetchall()
    for row in r4:
        print(f"  {row[0]}: {row[1]}")
