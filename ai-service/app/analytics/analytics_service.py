from typing import List, Dict, Any
import networkx as nx
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.graph.age_graph_repository import AgeGraphRepository

class AnalyticsService:
    def __init__(self, db: Session, graph_name: str = "crime_network"):
        self.db = db
        self.repo = AgeGraphRepository(db, graph_name)

    def _build_networkx_graph(self, global_graph: dict) -> nx.Graph:
        G = nx.Graph()
        for node in global_graph.get("nodes", []):
            G.add_node(node["data"]["id"], **node["data"])
        for edge in global_graph.get("edges", []):
            d = edge["data"]
            G.add_edge(d["source"], d["target"], **d)
        return G

    def _get_entity_cases_mapping(self) -> Dict[str, List[str]]:
        sql = "SELECT entity_id, case_id FROM case_entities"
        result = self.db.execute(text(sql)).fetchall()
        mapping = {}
        for eid, cid in result:
            mapping.setdefault(eid, []).append(cid)
        return mapping

    def generate_leads(self, case_id: str = None) -> Dict[str, Any]:
        # Always run patterns on the global graph for global awareness, but filter results if case_id provided
        global_graph = self.repo.get_global_subgraph()
        G = self._build_networkx_graph(global_graph)
        entity_cases = self._get_entity_cases_mapping()
        
        leads = []
        metrics = {}
        patterns = []
        
        if not G.nodes:
            return {"entities_analyzed": 0, "metrics": [], "patterns": [], "leads": []}

        # 1. Degree Centrality
        degree_dict = dict(G.degree())
        
        # 2. Betweenness Centrality
        betweenness_dict = nx.betweenness_centrality(G, normalized=True)
        
        for node_id in G.nodes():
            metrics[node_id] = {
                "degree": degree_dict.get(node_id, 0),
                "betweenness_centrality": betweenness_dict.get(node_id, 0.0)
            }
            
        # Analytics #3: Cross-Case Bridge
        for node_id, cases in entity_cases.items():
            if node_id in G.nodes and len(set(cases)) > 1:
                # Find relationships for this node
                edges = G.edges(node_id, data=True)
                rel_ids = [e[2].get("relationship_id") for e in edges if "relationship_id" in e[2]]
                
                leads.append({
                    "lead_id": f"LEAD-CCB-{node_id}",
                    "lead_type": "CROSS_CASE_BRIDGE",
                    "priority": "HIGH",
                    "title": "Potential cross-case bridge",
                    "description": f"Entity {node_id} participates in confirmed relationships across {len(set(cases))} cases.",
                    "entity_ids": [node_id],
                    "case_ids": list(set(cases)),
                    "relationship_ids": rel_ids,
                    "supporting_metrics": metrics.get(node_id, {})
                })
                patterns.append({"type": "CROSS_CASE_BRIDGE", "entity_id": node_id, "cases": list(set(cases))})

        # Analytics #5: Shared Identifier Pattern
        identifier_types = ["PHONE", "UPI_ID", "VEHICLE", "LOCATION"]
        for node_id, data in G.nodes(data=True):
            if data.get("entity_type") in identifier_types:
                neighbors = list(G.neighbors(node_id))
                if len(neighbors) > 1:
                    # Collect neighbor cases
                    ncases = set()
                    for n in neighbors:
                        ncases.update(entity_cases.get(n, []))
                    
                    edges = G.edges(node_id, data=True)
                    rel_ids = [e[2].get("relationship_id") for e in edges if "relationship_id" in e[2]]
                    
                    leads.append({
                        "lead_id": f"LEAD-SID-{node_id}",
                        "lead_type": "SHARED_IDENTIFIER",
                        "priority": "MEDIUM" if len(ncases) <= 1 else "HIGH",
                        "title": f"Shared {data.get('entity_type')} Identifier",
                        "description": f"Multiple confirmed entities are connected to the same {data.get('entity_type')} identifier.",
                        "entity_ids": [node_id] + neighbors,
                        "case_ids": list(ncases),
                        "relationship_ids": rel_ids,
                        "supporting_metrics": metrics.get(node_id, {})
                    })
                    patterns.append({"type": "SHARED_IDENTIFIER", "identifier": node_id, "connected_entities": neighbors})

        # Analytics #6: Financial Convergence
        for node_id, data in G.nodes(data=True):
            if data.get("entity_type") in ["UPI_ID", "BANK_ACCOUNT"]:
                # Financial convergence: multiple entities connected to the same financial endpoint
                neighbors = list(G.neighbors(node_id))
                
                if len(neighbors) > 1:
                    sources = neighbors
                    edges = G.edges(node_id, data=True)
                    rel_ids = [e[2].get("relationship_id") for e in edges if "relationship_id" in e[2]]
                    ncases = set()
                    for s in sources: ncases.update(entity_cases.get(s, []))
                    
                    leads.append({
                        "lead_id": f"LEAD-FC-{node_id}",
                        "lead_type": "FINANCIAL_CONVERGENCE",
                        "priority": "HIGH",
                        "title": "Financial Convergence",
                        "description": f"Multiple confirmed entities converge on the same financial identifier {node_id}.",
                        "entity_ids": [node_id] + sources,
                        "case_ids": list(ncases),
                        "relationship_ids": rel_ids,
                        "supporting_metrics": metrics.get(node_id, {})
                    })
                    patterns.append({"type": "FINANCIAL_CONVERGENCE", "identifier": node_id, "sources": sources})

        # Analytics #7: Communication Concentration
        for node_id, data in G.nodes(data=True):
            if data.get("entity_type") == "PHONE":
                neighbors = list(G.neighbors(node_id))
                if len(neighbors) > 2: # "unusually many"
                    edges = G.edges(node_id, data=True)
                    rel_ids = [e[2].get("relationship_id") for e in edges if "relationship_id" in e[2]]
                    ncases = set()
                    for n in neighbors: ncases.update(entity_cases.get(n, []))
                    
                    leads.append({
                        "lead_id": f"LEAD-CC-{node_id}",
                        "lead_type": "COMMUNICATION_CONCENTRATION",
                        "priority": "MEDIUM",
                        "title": "Communication Concentration",
                        "description": f"Communication identifier {node_id} has an unusually high number of confirmed relationships ({len(neighbors)}).",
                        "entity_ids": [node_id] + neighbors,
                        "case_ids": list(ncases),
                        "relationship_ids": rel_ids,
                        "supporting_metrics": metrics.get(node_id, {})
                    })
                    patterns.append({"type": "COMMUNICATION_CONCENTRATION", "identifier": node_id, "connections": len(neighbors)})

        # Filter by case_id if requested
        if case_id:
            leads = [L for L in leads if case_id in L.get("case_ids", [])]
            # Optionally filter metrics to only those in the case
            case_nodes = [eid for eid, cids in entity_cases.items() if case_id in cids]
            metrics = {k: v for k, v in metrics.items() if k in case_nodes}

        # Format output
        metric_list = [{"entity_id": k, **v} for k, v in metrics.items()]
        
        return {
            "case_id": case_id or "GLOBAL",
            "entities_analyzed": len(metrics),
            "metrics": metric_list,
            "patterns": patterns,
            "leads": leads
        }

    def find_multi_hop_path(self, source_entity_id: str, target_entity_id: str, max_depth: int = 5) -> Dict[str, Any]:
        global_graph = self.repo.get_global_subgraph()
        G = self._build_networkx_graph(global_graph)
        
        if source_entity_id not in G or target_entity_id not in G:
            return {"path": [], "relationships": [], "error": "One or both entities not found in authoritative graph"}
            
        try:
            # We enforce max depth by checking if shortest path length <= max_depth
            path = nx.shortest_path(G, source=source_entity_id, target=target_entity_id)
            if len(path) - 1 > max_depth:
                return {"path": [], "relationships": [], "error": f"Path exists but exceeds max depth of {max_depth}"}
                
            relationships = []
            for i in range(len(path)-1):
                u = path[i]
                v = path[i+1]
                edata = G.get_edge_data(u, v)
                relationships.append(edata.get("relationship_id"))
                
            return {
                "path": path,
                "relationships": relationships
            }
        except nx.NetworkXNoPath:
            return {"path": [], "relationships": [], "error": "No confirmed path found between entities"}

