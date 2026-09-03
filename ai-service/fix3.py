import os

for path in ['app/api/graph.py', 'app/graph/age_writer.py']:
    with open(path, 'r') as f:
        data = f.read()
    data = data.replace('\\"\\"\\"', '\"\"\"')
    with open(path, 'w') as f:
        f.write(data)
