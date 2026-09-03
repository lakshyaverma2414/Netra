import os
import json
import psycopg2
import logging
from typing import List, Dict, Any
from app.graph.graph_writer import GraphWriter
from app.schemas.validation import RelationshipValidationResult, ValidationStatus
from app.schemas.resolution import CanonicalEntity
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def escape_cypher_string(s: str) -> str:
    if not isinstance(s, str):
        return str(s)
    return s.replace('\\', '\\\\').replace("'", "''")

class AgeGraphWriter(GraphWriter):
    def __init__(self, dsn: str = None, graph_name: str = None):
        self.dsn = dsn or f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"
        self.graph_name = graph_name or os.getenv('AGE_GRAPH_NAME')
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(self.dsn)
        with self.conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        self.conn.commit()
        
    def disconnect(self):
        if self.conn:
            self.conn.close()

    def write_entities(self, entities: List[CanonicalEntity]) -> int:
        if not self.conn:
            raise RuntimeError("Not connected")
            
        written = 0
        with self.conn.cursor() as cur:
            for ent in entities:
                if ent.resolution_status not in ["CONFIRMED", "PROBABLE"]:
                    continue
                    
                aliases_str = escape_cypher_string(json.dumps(ent.aliases or []))
                
                query = f"""
                SELECT * FROM cypher('{self.graph_name}', $$
                    MERGE (n:{ent.entity_type} {{entity_id: '{escape_cypher_string(ent.entity_id)}'}})
                    SET n.canonical_name = '{escape_cypher_string(ent.canonical_name)}',
                        n.resolution_status = '{escape_cypher_string(ent.resolution_status)}',
                        n.resolution_score = {float(ent.resolution_score)},
                        n.aliases = '{aliases_str}'
                $$) AS (v agtype);
                """
                cur.execute(query)
                written += 1
            self.conn.commit()
        return written

    def write_relationships(self, validation_results: List[RelationshipValidationResult]) -> int:
        if not self.conn:
            raise RuntimeError("Not connected")
            
        written = 0
        with self.conn.cursor() as cur:
            for res in validation_results:
                if res.status != ValidationStatus.CONFIRMED:
                    continue
                    
                s_recs_str = escape_cypher_string(json.dumps(res.source_record_ids))
                e_ids_str = escape_cypher_string(json.dumps(res.evidence_ids))
                val_at_str = escape_cypher_string(res.validated_at.isoformat())
                
                query = f"""
                SELECT * FROM cypher('{self.graph_name}', $$
                    MATCH (a {{entity_id: '{escape_cypher_string(res.source_entity_id)}'}})
                    MATCH (b {{entity_id: '{escape_cypher_string(res.target_entity_id)}'}})
                    MERGE (a)-[r:{res.relationship_type} {{relationship_id: '{escape_cypher_string(res.relationship_id)}'}}]->(b)
                    SET r.source_record_ids = '{s_recs_str}',
                        r.evidence_ids = '{e_ids_str}',
                        r.validator_version = '{escape_cypher_string(res.validator_version)}',
                        r.status = 'CONFIRMED',
                        r.validated_at = '{val_at_str}'
                $$) AS (v agtype);
                """
                cur.execute(query)
                written += 1
            self.conn.commit()
        return written
