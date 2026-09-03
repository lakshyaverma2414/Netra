import re

with open('src/pages/GraphExplorer.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("const data = await res.json();", "const data = await res.json(); console.log('DATA:', data);")

with open('src/pages/GraphExplorer.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
