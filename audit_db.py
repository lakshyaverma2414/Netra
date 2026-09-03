import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('ai-service/.env')
dsn = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"

with psycopg2.connect(dsn) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # 1. Version & Extensions
        cur.execute("SELECT version();")
        print("--- VERSION ---")
        print(cur.fetchone()['version'])
        
        cur.execute("SELECT extname, extversion FROM pg_extension;")
        print("\n--- EXTENSIONS ---")
        for r in cur.fetchall(): print(r)
        
        # Schemas
        cur.execute("SELECT schema_name FROM information_schema.schemata;")
        print("\n--- SCHEMAS ---")
        for r in cur.fetchall(): print(r['schema_name'])
        
        # 2. Relational Tables
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog') 
            AND table_type = 'BASE TABLE';
        """)
        tables = cur.fetchall()
        print("\n--- TABLES ---")
        for t in tables:
            schema, name = t['table_schema'], t['table_name']
            cur.execute(f"SELECT count(*) FROM {schema}.{name}")
            count = cur.fetchone()['count']
            
            cur.execute(f"""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_schema = '{schema}' AND table_name = '{name}';
            """)
            cols = cur.fetchall()
            print(f"Table: {schema}.{name} (Rows: {count})")
            for c in cols: print(f"  {c['column_name']}: {c['data_type']} ({c['character_maximum_length']})")

        # Indexes
        cur.execute("""
            SELECT schemaname, tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """)
        print("\n--- INDEXES ---")
        for r in cur.fetchall(): print(r)

        # AGE Nodes & Edges
        cur.execute("LOAD 'age';")
        cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        
        print("\n--- AGE LABELS (Vertices) ---")
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH (n) RETURN distinct label(n), count(n) $$) as (label agtype, cnt agtype);")
        for r in cur.fetchall(): print(r)

        print("\n--- AGE LABELS (Edges) ---")
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH ()-[e]->() RETURN distinct type(e), count(e) $$) as (type agtype, cnt agtype);")
        for r in cur.fetchall(): print(r)
        
        print("\n--- AGE VERTEX SAMPLE ---")
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH (n) RETURN properties(n), label(n) LIMIT 5 $$) as (props agtype, label agtype);")
        for r in cur.fetchall(): print(r)

        print("\n--- AGE EDGE SAMPLE ---")
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH ()-[e]->() RETURN properties(e), type(e) LIMIT 5 $$) as (props agtype, type agtype);")
        for r in cur.fetchall(): print(r)
