import re

with open('src/pages/GraphExplorer.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

controls_injection = '''
                        <div className="flex flex-col gap-2">
                            <input 
                                type="text" 
                                placeholder="Entity ID (e.g. P001)" 
                                value={entityId}
                                onChange={(e) => setEntityId(e.target.value)}
                                className="w-full px-3 py-2 bg-surface-container border border-outline-variant rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary"
                            />
                            <select 
                                value={depth}
                                onChange={(e) => setDepth(Number(e.target.value))}
                                className="w-full px-3 py-2 bg-surface-container border border-outline-variant rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary"
                            >
                                <option value={1}>Depth 1</option>
                                <option value={2}>Depth 2</option>
                                <option value={3}>Depth 3</option>
                            </select>
                            <button 
                                onClick={fetchGraph}
                                disabled={isFetching}
                                className="w-full py-2 bg-primary text-on-primary rounded-lg text-sm font-bold hover:opacity-90 disabled:opacity-50"
                            >
                                {isFetching ? 'Loading...' : 'Fetch Graph'}
                            </button>
                            {fetchError && <p className="text-error text-xs">{fetchError}</p>}
                        </div>
'''

code = re.sub(r'<div className="relative">.*?</div>', controls_injection, code, flags=re.DOTALL, count=1)

with open('src/pages/GraphExplorer.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
