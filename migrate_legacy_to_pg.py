import psycopg2
from psycopg2.extras import RealDictCursor
import json

dsn = "dbname=postgres user=postgres password=netra_secure_dev_password host=127.0.0.1 port=5433"
with psycopg2.connect(dsn) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("LOAD 'age';")
        cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        
        cur.execute("""
            INSERT INTO cases (case_id, case_number, title, status) 
            VALUES ('CASE-LEGACY', 'LEGACY-001', 'Legacy Prototype Graph', 'CLOSED') 
            ON CONFLICT DO NOTHING;
        """)

        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH (n) RETURN properties(n), label(n) $$) as (props agtype, label agtype);")
        legacy_nodes = cur.fetchall()
        
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH (a)-[e]->(b) RETURN properties(a).entity_id, type(e), properties(b).entity_id, properties(e) $$) as (src agtype, rel_type agtype, tgt agtype, props agtype);")
        legacy_edges = cur.fetchall()

        for node in legacy_nodes:
            props = json.loads(node['props']) if isinstance(node['props'], str) else node['props']
            label = node['label'].strip('"')
            if label == 'UPI_ACCOUNT': label = 'UPI_ID'
            entity_id = props.get('entity_id')
            canonical_name = props.get('canonical_name', 'Unknown')
            res_status = props.get('resolution_status', 'CONFIRMED')
            res_score = props.get('resolution_score', 1.0)
            
            if not entity_id: continue
            
            cur.execute("""
                INSERT INTO entities (entity_id, entity_type, canonical_name, normalized_value, resolution_status, resolution_score)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (entity_id) DO NOTHING;
            """, (entity_id, label, canonical_name, canonical_name.upper(), res_status, res_score))
            
            cur.execute("""
                INSERT INTO case_entities (case_id, entity_id, association_type, confidence)
                VALUES ('CASE-LEGACY', %s, 'LEGACY_IMPORT', 1.0)
                ON CONFLICT DO NOTHING;
            """, (entity_id,))

        import uuid
        for edge in legacy_edges:
            src = edge['src'].strip('"')
            tgt = edge['tgt'].strip('"')
            rel_type = edge['rel_type'].strip('"')
            props = json.loads(edge['props']) if isinstance(edge['props'], str) else edge['props']
            
            rel_id = props.get('relationship_id')
            status = props.get('status', 'CONFIRMED')
            if not rel_id: continue
            
            # check if relationship_id exists
            cur.execute("SELECT 1 FROM relationships WHERE relationship_id = %s", (rel_id,))
            if cur.fetchone():
                rel_id = rel_id + "-" + uuid.uuid4().hex[:4]
            
            try:
                cur.execute("""
                    INSERT INTO relationships (relationship_id, source_entity_id, relationship_type, target_entity_id, status)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (source_entity_id, relationship_type, target_entity_id) DO NOTHING;
                """, (rel_id, src, rel_type, tgt, status))
                
                cur.execute("""
                    INSERT INTO relationship_cases (relationship_id, case_id)
                    VALUES (%s, 'CASE-LEGACY')
                    ON CONFLICT DO NOTHING;
                """, (rel_id,))
            except Exception as e:
                print(f"Skipping edge {src}-{rel_type}-{tgt}: {e}")
                conn.rollback() # rollback current transaction block
            
    conn.commit()
    print("PostgreSQL authoritative records populated successfully.")
    
