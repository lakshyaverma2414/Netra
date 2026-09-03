import os

for f in ['app/graph/age_writer.py', 'app/api/graph.py']:
    with open(f, 'r') as file:
        data = file.read()
    data = data.replace('\"\"', '\"\"')
    with open(f, 'w') as file:
        file.write(data)
