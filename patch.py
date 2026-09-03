import re

with open('src/pages/GraphExplorer.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add states
states_injection = '''
    const [entityId, setEntityId] = useState('P001');
    const [depth, setDepth] = useState(1);
    const [isFetching, setIsFetching] = useState(false);
    const [fetchError, setFetchError] = useState('');

    const fetchGraph = async () => {
        setIsFetching(true);
        setFetchError('');
        setSelectedNode(null);
        try {
            const res = await fetch(http://localhost:8000/api/v1/graph/explore?entity_id=&depth=);
            if (!res.ok) throw new Error('API failure');
            const data = await res.json();
            
            if (!data.nodes || data.nodes.length === 0) {
                setElements([]);
                setFetchError('No nodes found');
            } else {
                const mappedNodes = data.nodes.map((n: any) => ({
                    ...n,
                    data: {
                        ...n.data,
                        type: String(n.data.type || '').toLowerCase(),
                        label: n.data.label || n.data.id,
                        riskLevel: n.data.resolution_status === 'CONFIRMED' ? 'High' : (n.data.resolution_status === 'PROBABLE' ? 'Medium' : 'Low'),
                        riskScore: n.data.resolution_score !== undefined ? n.data.resolution_score * 100 : 50
                    }
                }));
                const mappedEdges = data.edges.map((e: any) => ({
                    ...e,
                    data: {
                        ...e.data,
                        label: String(e.data.label || '').toUpperCase()
                    }
                }));
                setElements([...mappedNodes, ...mappedEdges]);
            }
        } catch (err) {
            setFetchError('Error fetching graph');
            setElements([]);
        } finally {
            setIsFetching(false);
        }
    };

    useEffect(() => {
        fetchGraph();
    }, []);
'''

# Replace the initial data load useEffect
code = re.sub(r'useEffect\(\(\) => \{\s*// Load data initially\s*setElements\(sampleGraph\.filter\(\(el: any\) => el\.data\.caseId === caseId\)\);\s*\}, \[caseId\]\);', states_injection, code)

# 2. Add UI controls to the left sidebar
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

# Replace search bar in left sidebar
code = re.sub(r'<div className="relative">\s*<span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>\s*<input[^>]+/>\s*</div>', controls_injection, code)


with open('src/pages/GraphExplorer.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
