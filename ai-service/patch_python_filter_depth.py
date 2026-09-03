import re

with open('app/api/graph.py', 'r') as f:
    code = f.read()

injection = '''
        confirmed_edges = {eid: e for eid, e in edges_dict.items() if e["data"]["status"] == "CONFIRMED"}
        
        adj = {}
        for e in confirmed_edges.values():
            s = e["data"]["source"]
            t = e["data"]["target"]
            adj.setdefault(s, []).append(t)
            adj.setdefault(t, []).append(s)
            
        reachable_nodes = {safe_entity_id}
        queue = [(safe_entity_id, 0)]
        visited = {safe_entity_id}
        
        while queue:
            curr_node, current_depth = queue.pop(0)
            if current_depth < depth:
                for neighbor in adj.get(curr_node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        reachable_nodes.add(neighbor)
                        queue.append((neighbor, current_depth + 1))
                        
        final_nodes = [n for n_id, n in nodes_dict.items() if n_id in reachable_nodes]
        final_edges = [e for e in confirmed_edges.values() if e["data"]["source"] in reachable_nodes and e["data"]["target"] in reachable_nodes]
        
        return {
            "nodes": final_nodes,
            "edges": final_edges
        }
'''

code = re.sub(r'# Filter to CONFIRMED and reachable.*return \{(?:\s*"nodes": final_nodes,\s*"edges": final_edges\s*)\}', injection, code, flags=re.DOTALL)

with open('app/api/graph.py', 'w') as f:
    f.write(code)
