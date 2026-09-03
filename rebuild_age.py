import psycopg2
from psycopg2.extras import RealDictCursor

dsn = "dbname=postgres user=postgres password=netra_secure_dev_password host=127.0.0.1 port=5433"
with psycopg2.connect(dsn) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("LOAD 'age';")
        cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        
        # Drop legacy graph
        cur.execute("SELECT drop_graph('crime_network', true);")
        
        # Create fresh graph
        cur.execute("SELECT create_graph('crime_network');")
        
        # Rebuild vertices
        cur.execute("SELECT entity_id, entity_type, canonical_name FROM entities;")
        entities = cur.fetchall()
        for e in entities:
            # Cypher doesn't allow dynamic labels easily in standard AGE execution, so we construct the query
            label = e['entity_type']
            props = f"{{entity_id: '{e['entity_id']}', canonical_name: '{e['canonical_name']}'}}"
            query = f"SELECT * FROM cypher('crime_network', $$ CREATE (n:{label} {props}) $$) as (a agtype);"
            cur.execute(query)
            
        # Rebuild edges
        cur.execute("SELECT relationship_id, source_entity_id, relationship_type, target_entity_id, status FROM relationships WHERE status = 'CONFIRMED';")
        edges = cur.fetchall()
        for edge in edges:
            rel_type = edge['relationship_type']
            props = f"{{relationship_id: '{edge['relationship_id']}', status: '{edge['status']}'}}"
            
            # AGE MATCH and CREATE edge
            query = f"""
            SELECT * FROM cypher('crime_network', $$ 
                MATCH (a), (b) 
                WHERE a.entity_id = '{edge['source_entity_id']}' AND b.entity_id = '{edge['target_entity_id']}' 
                CREATE (a)-[r:{rel_type} {props}]->(b) 
            $$) as (a agtype);
            """
            cur.execute(query)
            
        # Verify counts
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH (n) RETURN count(n) $$) as (cnt agtype);")
        new_v = cur.fetchone()['cnt']
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH ()-[e]->() RETURN count(e) $$) as (cnt agtype);")
        new_e = cur.fetchone()['cnt']
        
        print(f"New AGE Projection -> Vertices: {new_v}, Edges: {new_e}")
        
    conn.commit()
