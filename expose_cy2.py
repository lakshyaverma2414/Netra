import re
with open('src/pages/GraphExplorer.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'cyRef\.current = cy;', 'cyRef.current = cy; (window as any).cy = cy;', code)

with open('src/pages/GraphExplorer.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
