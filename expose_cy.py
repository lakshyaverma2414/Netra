import re
with open('src/pages/GraphExplorer.tsx', 'r', encoding='utf-8') as f:
    code = f.read()
if 'window.cy =' not in code:
    code = code.replace("const cy = cyRef.current;", "const cy = cyRef.current;\n        (window as any).cy = cy;")
    with open('src/pages/GraphExplorer.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
