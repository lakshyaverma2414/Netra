import json
import re
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Set
from collections import deque

def sanitize(val: str) -> str:
    if not isinstance(val, str):
        return str(val)
    return re.sub(r'[^a-zA-Z0-9_.-]', '', val)

class AgeGraphRepository:
    def __init__(self, db: Session, graph_name: str = "crime_network"):
        self.db = db
        self.graph_name = sanitize(graph_name)
        self._ensure_path()

    def _ensure_path(self):
        conn = self.db.connection().connection
        with conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, \"$user\", public;")

    def sync_confirmed_relationship(self, relationship_id: str, source_id: str, target_id: str, rel_type: str, source_label: str, target_label: str, props: dict):
        # Sanitize all inputs to prevent Cypher injection
        relationship_id = sanitize(relationship_id)
        source_id = sanitize(source_id)
        target_id = sanitize(target_id)
        rel_type = sanitize(rel_type)
        source_label = sanitize(source_label)
        target_label = sanitize(target_label)

        conn = self.db.connection().connection
        with conn.cursor() as cur:
            sprops = f"{{entity_id: '{source_id}'}}"
            cur.execute(f"SELECT * FROM cypher('{self.graph_name}', $$ MERGE (n:{source_label} {sprops}) RETURN n $$) as (a agtype);")
            
            tprops = f"{{entity_id: '{target_id}'}}"
            cur.execute(f"SELECT * FROM cypher('{self.graph_name}', $$ MERGE (n:{target_label} {tprops}) RETURN n $$) as (a agtype);")
            
            prop_strs = []
            for k, v in props.items():
                sk = sanitize(k)
                if isinstance(v, str):
                    sv = str(v).replace("'", "\\'") # escape quotes
                    prop_strs.append(f"{sk}: '{sv}'")
                else:
                    prop_strs.append(f"{sk}: {v}")
            eprops = "{" + ", ".join(prop_strs) + "}"
            
            query = f"""
            SELECT * FROM cypher('{self.graph_name}', $$ 
                MATCH (a:{source_label} {{entity_id: '{source_id}'}}), (b:{target_label} {{entity_id: '{target_id}'}})
                MERGE (a)-[r:{rel_type} {{relationship_id: '{relationship_id}'}}]->(b)
                SET r += {eprops}
                RETURN r
            $$) as (a agtype);
            """
            cur.execute(query)

    def _bfs_filter(self, entity_id: str, depth: int, all_nodes: list, all_edges: list) -> tuple:
        if not entity_id or depth < 1:
            return all_nodes, all_edges
            
        # Build adjacency list
        adj = {}
        for edge in all_edges:
            src = edge['data']['source']
            tgt = edge['data']['target']
            adj.setdefault(src, []).append((tgt, edge))
            adj.setdefault(tgt, []).append((src, edge))
            
        visited_nodes = set([entity_id])
        visited_edges = set()
        queue = deque([(entity_id, 0)])
        
        while queue:
            curr, curr_depth = queue.popleft()
            if curr_depth >= depth:
                continue
            
            for neighbor, edge in adj.get(curr, []):
                rel_id = edge['data']['relationship_id']
                visited_edges.add(rel_id)
                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)
                    queue.append((neighbor, curr_depth + 1))
                    
        filtered_nodes = [n for n in all_nodes if n['data']['id'] in visited_nodes]
        filtered_edges = [e for e in all_edges if e['data']['relationship_id'] in visited_edges]
        
        return filtered_nodes, filtered_edges

    def get_case_subgraph(self, case_id: str, entity_id: str = None, depth: int = 1) -> dict:
        sql = "SELECT entity_id FROM case_entities WHERE case_id = :case_id"
        result = self.db.execute(text(sql), {"case_id": case_id}).fetchall()
        allowed_entities = {row[0] for row in result}
        
        if not allowed_entities:
            return {"nodes": [], "edges": []}
            
        sql = "SELECT relationship_id FROM relationship_cases WHERE case_id = :case_id"
        rel_result = self.db.execute(text(sql), {"case_id": case_id}).fetchall()
        allowed_relationships = {row[0] for row in rel_result}

        conn = self.db.connection().connection
        nodes = []
        edges = []
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM cypher('{self.graph_name}', $$ MATCH (n) RETURN properties(n), label(n) $$) as (props agtype, label agtype);")
            raw_nodes = cur.fetchall()
            for rn in raw_nodes:
                props = rn[0]
                if isinstance(props, str): props = json.loads(props)
                eid = props.get('entity_id')
                if eid in allowed_entities:
                    nodes.append({"data": {"id": eid, "label": props.get('canonical_name', eid), "entity_type": rn[1].strip('"')}})
                    
            cur.execute(f"SELECT * FROM cypher('{self.graph_name}', $$ MATCH (a)-[r]->(b) RETURN properties(a).entity_id, type(r), properties(b).entity_id, properties(r) $$) as (s agtype, t agtype, tr agtype, p agtype);")
            raw_edges = cur.fetchall()
            for re in raw_edges:
                s, typ, t, p = re
                if isinstance(p, str): p = json.loads(p)
                rid = p.get('relationship_id')
                if rid in allowed_relationships:
                    s = s.strip('"') if isinstance(s, str) else s
                    t = t.strip('"') if isinstance(t, str) else t
                    edges.append({"data": {"id": rid, "source": s, "target": t, "relationship_type": typ.strip('"'), "relationship_id": rid}})
        
        if entity_id:
            nodes, edges = self._bfs_filter(entity_id, depth, nodes, edges)
            
        return {"case_id": case_id, "nodes": nodes, "edges": edges}
        
    def get_global_subgraph(self, entity_id: str = None, depth: int = 1) -> dict:
        conn = self.db.connection().connection
        nodes = []
        edges = []
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM cypher('{self.graph_name}', $$ MATCH (n) RETURN properties(n), label(n) $$) as (props agtype, label agtype);")
            raw_nodes = cur.fetchall()
            for rn in raw_nodes:
                props = rn[0]
                if isinstance(props, str): props = json.loads(props)
                eid = props.get('entity_id')
                nodes.append({"data": {"id": eid, "label": props.get('canonical_name', eid), "entity_type": rn[1].strip('"')}})
                
            cur.execute(f"SELECT * FROM cypher('{self.graph_name}', $$ MATCH (a)-[r]->(b) RETURN properties(a).entity_id, type(r), properties(b).entity_id, properties(r) $$) as (s agtype, t agtype, tr agtype, p agtype);")
            raw_edges = cur.fetchall()
            for re in raw_edges:
                s, typ, t, p = re
                if isinstance(p, str): p = json.loads(p)
                rid = p.get('relationship_id')
                s = s.strip('"') if isinstance(s, str) else s
                t = t.strip('"') if isinstance(t, str) else t
                edges.append({"data": {"id": rid, "source": s, "target": t, "relationship_type": typ.strip('"'), "relationship_id": rid}})
                
        if entity_id:
            nodes, edges = self._bfs_filter(entity_id, depth, nodes, edges)
            
        return {"nodes": nodes, "edges": edges}
