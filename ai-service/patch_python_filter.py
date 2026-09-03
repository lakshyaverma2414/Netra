import re

with open('app/api/graph.py', 'r') as f:
    code = f.read()

# First, remove the invalid WHERE ALL
code = code.replace("WHERE ALL(rel IN relationships(p) WHERE rel.status = 'CONFIRMED')", "")

# Now find the place where we parse edges and nodes, we will filter in Python instead.
# Actually, it's simpler. We already have nodes_dict and edges_dict populated.
# We just filter edges_dict to only keep CONFIRMED edges.
# Then we find all nodes reachable from safe_entity_id using only those edges!

injection = '''
        # Filter to CONFIRMED and reachable
        confirmed_edges = {eid: e for eid, e in edges_dict.items() if e["data"]["status"] == "CONFIRMED"}
        
        reachable_nodes = {safe_entity_id}
        changed = True
        while changed:
            changed = False
            for e in confirmed_edges.values():
                s = e["data"]["source"]
                t = e["data"]["target"]
                if s in reachable_nodes and t not in reachable_nodes:
                    reachable_nodes.add(t)
                    changed = True
                elif t in reachable_nodes and s not in reachable_nodes:
                    reachable_nodes.add(s)
                    changed = True
                    
        final_nodes = [n for n_id, n in nodes_dict.items() if n_id in reachable_nodes]
        final_edges = [e for e in confirmed_edges.values() if e["data"]["source"] in reachable_nodes and e["data"]["target"] in reachable_nodes]
        
        return {
            "nodes": final_nodes,
            "edges": final_edges
        }
'''

code = re.sub(r'return \{\s*"nodes": list\(nodes_dict\.values\(\)\),\s*"edges": list\(edges_dict\.values\(\)\)\s*\}', injection, code)

with open('app/api/graph.py', 'w') as f:
    f.write(code)
