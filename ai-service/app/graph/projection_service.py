from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.models import Entity, Relationship, ResolutionStatus, ValidationStatus
from app.graph.age_graph_repository import AgeGraphRepository
from typing import Dict, Any
import datetime

class ProjectionService:
    def __init__(self, db: Session, graph_name: str = "crime_network"):
        self.db = db
        self.repo = AgeGraphRepository(db, graph_name)
        self.graph_name = self.repo.graph_name

    def project_all(self) -> Dict[str, Any]:
        stats = {
            "status": "success",
            "vertices_created": 0,
            "vertices_updated": 0,
            "edges_created": 0,
            "edges_updated": 0,
            "edges_removed": 0,
            "projection_version": datetime.datetime.now().isoformat()
        }

        # 1. Project Confirmed Entities
        confirmed_entities = self.db.query(Entity).filter(Entity.resolution_status == ResolutionStatus.CONFIRMED).all()
        conn = self.db.connection().connection
        
        projected_entity_ids = set()
        with conn.cursor() as cur:
            for ent in confirmed_entities:
                ent_type = ent.entity_type.value if hasattr(ent.entity_type, 'value') else ent.entity_type
                ent_id = ent.entity_id
                c_name = ent.canonical_name.replace("'", "''")
                projected_entity_ids.add(ent_id)
                
                query = f"""
                SELECT * FROM cypher('{self.graph_name}', $$ 
                    MERGE (n:{ent_type} {{entity_id: '{ent_id}'}})
                    SET n.canonical_name = '{c_name}'
                    RETURN n
                $$) as (a agtype);
                """
                cur.execute(query)
                stats["vertices_updated"] += 1 # Merge covers create/update

        # 2. Project Confirmed Relationships
        confirmed_relationships = self.db.query(Relationship).filter(Relationship.status == ValidationStatus.CONFIRMED).all()
        
        projected_rel_ids = set()
        for rel in confirmed_relationships:
            projected_rel_ids.add(rel.relationship_id)
            source_ent = self.db.query(Entity).filter(Entity.entity_id == rel.source_entity_id).first()
            target_ent = self.db.query(Entity).filter(Entity.entity_id == rel.target_entity_id).first()
            
            if not source_ent or not target_ent:
                continue
                
            src_type = source_ent.entity_type.value if hasattr(source_ent.entity_type, 'value') else source_ent.entity_type
            tgt_type = target_ent.entity_type.value if hasattr(target_ent.entity_type, 'value') else target_ent.entity_type
            
            self.repo.sync_confirmed_relationship(
                relationship_id=rel.relationship_id,
                source_id=rel.source_entity_id,
                target_id=rel.target_entity_id,
                rel_type=rel.relationship_type,
                source_label=src_type,
                target_label=tgt_type,
                props={}
            )
            stats["edges_updated"] += 1
            
        # 3. Remove Stale Edges (Edges in AGE that are not CONFIRMED in Postgres)
        # Note: We query all edges and their relationship_ids from AGE
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM cypher('{self.graph_name}', $$ MATCH ()-[r]->() RETURN properties(r).relationship_id $$) as (rid agtype);")
            age_edges = cur.fetchall()
            
            for row in age_edges:
                # Value could be a JSON string like '"R-007"' or None
                val = row[0]
                if val:
                    val_str = str(val).strip('"\'')
                    if val_str and val_str not in projected_rel_ids:
                        # Edge is stale, delete it
                        del_query = f"""
                        SELECT * FROM cypher('{self.graph_name}', $$ 
                            MATCH ()-[r {{relationship_id: '{val_str}'}}]->() 
                            DELETE r 
                            RETURN r 
                        $$) as (r agtype);
                        """
                        cur.execute(del_query)
                        stats["edges_removed"] += 1

        self.db.commit()
        return stats
