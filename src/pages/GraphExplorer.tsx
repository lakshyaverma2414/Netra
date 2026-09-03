import cases from '../mockData/cases.json';
import { useState, useEffect, useRef } from 'react';

import CytoscapeComponent from 'react-cytoscapejs';
import Chatbot from '../components/Chatbot';
import { PageTransition } from '../components/PageTransition';
import { useParams } from 'react-router-dom';
import { getInvestigationGraph, getInvestigationAnalytics } from '../api/graph';

const INITIAL_ENTITIES: Record<string, string> = {
    "C-001": "P-001",
    "C-002": "P-002",
    "C-003": "P-003"
};

const GraphExplorer = () => {
    const { caseId } = useParams();
    const caseExists = cases.some(c => c.id === caseId);
    
    if (caseId && !caseExists) {
        return <div className="h-screen flex items-center justify-center bg-surface text-on-surface">
            <div className="text-center">
                <h1 className="text-4xl text-error font-bold">404</h1>
                <p className="mt-2 text-on-surface-variant">Case Not Found</p>
                <a href="/dashboard" className="mt-4 block text-primary hover:underline">Return to Dashboard</a>
            </div>
        </div>;
    }

    const [selectedNode, setSelectedNode] = useState<any>(null);
    const [selectedEdge, setSelectedEdge] = useState<any>(null);
    const [selectedLead, setSelectedLead] = useState<any>(null);
    const [search, setSearch] = useState('');
    const [elements, setElements] = useState<any>([]);
    const [analytics, setAnalytics] = useState<any>(null);
    const cyRef = useRef<any>(null);
    const [isLoading, setIsLoading] = useState(true);

    const defaultEntityId = (caseId && INITIAL_ENTITIES[caseId]) || "P-001";
    const [entityId, setEntityId] = useState(defaultEntityId);
    const [depth, setDepth] = useState(1);
    const [fetchError, setFetchError] = useState('');

    const fetchGraphAndAnalytics = async () => {
        setIsLoading(true);
        setFetchError('');
        setSelectedNode(null);
        setSelectedEdge(null);
        setSelectedLead(null);
        try {
            if (!caseId) throw new Error("Case ID missing");
            const [graphData, analyticsData] = await Promise.all([
                getInvestigationGraph({ caseId, entityId, depth }),
                getInvestigationAnalytics(caseId)
            ]);
            
            // Adapt backend schema to cytoscape UI requirements
            const mappedNodes = graphData.nodes.map((n: any) => ({
                data: {
                    ...n.data,
                    type: n.data.entity_type?.toLowerCase() || 'unknown'
                }
            }));
            const mappedEdges = graphData.edges.map((e: any) => ({
                data: {
                    ...e.data,
                    label: e.data.relationship_type
                }
            }));

            setElements([...mappedNodes, ...mappedEdges]);
            setAnalytics(analyticsData);
        } catch (err: any) {
            setFetchError(err.message || 'Error loading graph and analytics');
            setElements([]);
            setAnalytics(null);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchGraphAndAnalytics();
    }, [caseId]);

    useEffect(() => {
        if (!cyRef.current) return;
        const cy = cyRef.current;
        (window as any).cy = cy;
        
        cy.batch(() => {
            cy.elements().removeClass('dimmed highlighted');
            
            if (selectedLead) {
                const nodeIds = selectedLead.entity_ids || [];
                const relIds = selectedLead.relationship_ids || [];
                
                const matches = cy.elements().filter((el: any) => {
                    if (el.isNode()) return nodeIds.includes(el.data('id'));
                    if (el.isEdge()) return relIds.includes(el.data('relationship_id')) || relIds.includes(el.data('id'));
                    return false;
                });
                
                cy.elements().addClass('dimmed').removeClass('highlighted');
                matches.removeClass('dimmed').addClass('highlighted');
                
            } else if (search.trim()) {
                const lowerSearch = search.toLowerCase();
                const matches = cy.nodes().filter((node: any) => {
                    const label = node.data('label');
                    const id = node.data('id');
                    return (label && label.toLowerCase().includes(lowerSearch)) || 
                           (id && id.toLowerCase().includes(lowerSearch));
                });
                
                cy.elements().addClass('dimmed').removeClass('highlighted');
                matches.removeClass('dimmed').addClass('highlighted');
                matches.connectedEdges().removeClass('dimmed').addClass('highlighted');
            }
        });
    }, [search, selectedLead, elements]);

    const stylesheet: any = [
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'color': '#1f2937',
                'font-size': '12px',
                'text-margin-y': 5,
                'font-weight': 'bold',
                'border-width': 2,
                'border-color': '#fff'
            }
        },
        {
            selector: 'node[type="person"]',
            style: { 'background-color': '#0B2447', 'width': 30, 'height': 30 }
        },
        {
            selector: 'node[type="location"]',
            style: { 'background-color': '#16a34a', 'shape': 'rectangle', 'width': 30, 'height': 30 }
        },
        {
            selector: 'node[type="vehicle"]',
            style: { 'background-color': '#f97316', 'shape': 'triangle', 'width': 30, 'height': 30 }
        },
        {
            selector: 'node[type="phone"]',
            style: { 'background-color': '#0ea5e9', 'shape': 'diamond', 'width': 25, 'height': 25 }
        },
        {
            selector: 'node[type="upi_id"]',
            style: { 'background-color': '#eab308', 'shape': 'hexagon', 'width': 30, 'height': 30 }
        },
        {
            selector: 'node[type="organization"]',
            style: { 'background-color': '#9333ea', 'shape': 'hexagon', 'width': 35, 'height': 35 }
        },
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#94a3b8',
                'target-arrow-color': '#94a3b8',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '10px',
                'color': '#64748b',
                'text-rotation': 'autorotate',
                'text-margin-y': -10
            }
        },
        {
            selector: ':selected',
            style: {
                'border-width': 4,
                'border-color': '#FF9933',
                'line-color': '#FF9933',
                'target-arrow-color': '#FF9933'
            }
        },
        {
            selector: 'node.dimmed, edge.dimmed',
            style: { 'opacity': 0.15 }
        },
        {
            selector: 'node.highlighted, edge.highlighted',
            style: { 'opacity': 1, 'border-width': 4, 'border-color': '#FF9933', 'line-color': '#FF9933', 'target-arrow-color': '#FF9933' }
        }
    ];

    return (
        <PageTransition>
        <div className="bg-surface text-on-surface h-screen flex flex-col font-body-md antialiased overflow-hidden">
            <header className="bg-primary text-on-primary w-full border-b border-outline-variant sticky top-0 z-30 flex justify-between items-center px-4 md:px-6 h-12 shrink-0">
              <div className="flex items-center gap-4 h-full">
                <div className="text-title-lg font-bold text-on-primary">NCRB Graph Explorer</div>
              </div>
              <div className="flex items-center gap-4">
                <button className="p-2 hover:bg-primary-container transition-colors rounded-full relative">
                  <span className="material-symbols-outlined text-sm">notifications</span>
                </button>
              </div>
            </header>

            <div className="flex-1 flex overflow-hidden">
                <aside className="w-80 bg-surface-container-lowest border-r border-outline-variant flex flex-col shrink-0">
                    <div className="p-4 border-b border-outline-variant">
                        <div className="flex flex-col gap-2">
                            <input 
                                type="text" 
                                placeholder="Entity ID (e.g. P-001)" 
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
                                <option value={4}>Depth 4</option>
                                <option value={5}>Depth 5</option>
                            </select>
                            <div className="flex bg-surface-container rounded-lg border border-outline-variant overflow-hidden focus-within:border-primary focus-within:ring-1 focus-within:ring-primary">
                                <span className="material-symbols-outlined text-on-surface-variant p-2 text-sm">search</span>
                                <input 
                                    type="text" 
                                    placeholder="Search in graph..." 
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    className="w-full py-2 pr-3 bg-transparent text-sm focus:outline-none"
                                />
                            </div>
                            <div className="flex gap-2">
                                <button 
                                    onClick={fetchGraphAndAnalytics}
                                    disabled={isLoading}
                                    className="flex-1 py-2 bg-primary text-on-primary rounded-lg text-sm font-bold hover:opacity-90 disabled:opacity-50"
                                >
                                    {isLoading ? 'Searching...' : 'Explore'}
                                </button>
                                <button 
                                    onClick={fetchGraphAndAnalytics}
                                    disabled={isLoading}
                                    title="Refresh Graph"
                                    className="px-3 py-2 bg-surface-container text-on-surface rounded-lg border border-outline-variant hover:bg-surface-container-high"
                                >
                                    <span className="material-symbols-outlined text-sm">refresh</span>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto p-4 space-y-6">
                        {analytics && (
                            <div>
                                <h3 className="text-label-sm font-bold text-on-surface-variant mb-2 uppercase tracking-wider">Network Analysis</h3>
                                <div className="text-sm text-on-surface mb-4">
                                    <p>Entities analyzed: <span className="font-bold">{analytics.entities_analyzed}</span></p>
                                </div>
                                
                                <h3 className="text-label-sm font-bold text-on-surface-variant mb-3 uppercase tracking-wider flex justify-between items-center">
                                    Investigative Leads
                                    {selectedLead && (
                                        <button 
                                            onClick={() => setSelectedLead(null)}
                                            className="text-xs text-primary hover:underline normal-case flex items-center"
                                        >
                                            <span className="material-symbols-outlined text-[14px]">close</span> Clear
                                        </button>
                                    )}
                                </h3>
                                
                                {analytics.leads && analytics.leads.length > 0 ? (
                                    <div className="space-y-3">
                                        {analytics.leads.map((lead: any, idx: number) => {
                                            const isSelected = selectedLead?.lead_id === lead.lead_id;
                                            return (
                                                <div 
                                                    key={idx} 
                                                    onClick={() => setSelectedLead(isSelected ? null : lead)}
                                                    className={`p-3 rounded border cursor-pointer transition-colors ${
                                                        isSelected 
                                                        ? 'bg-primary-container border-primary text-on-primary-container shadow-sm' 
                                                        : 'bg-surface-container-low border-outline-variant hover:bg-surface-container'
                                                    }`}
                                                >
                                                    <div className="flex items-start gap-2">
                                                        <span className="material-symbols-outlined text-sm mt-0.5 text-primary">search</span>
                                                        <div>
                                                            <h4 className="font-bold text-sm leading-tight mb-1">{lead.title}</h4>
                                                            <p className="text-xs opacity-90">{lead.description}</p>
                                                            <div className="mt-2 flex gap-2">
                                                                <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                                                                    lead.priority === 'HIGH' ? 'bg-error text-white' : 'bg-saffron-accent text-white'
                                                                }`}>
                                                                    {lead.priority} Priority
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <p className="text-sm text-on-surface-variant">No suspicious patterns detected in the current scope.</p>
                                )}
                            </div>
                        )}
                    </div>
                </aside>

                <main className="flex-1 relative bg-surface-container-highest">
                    {isLoading ? (
                        <div className="absolute inset-0 flex items-center justify-center bg-surface-container-highest z-20">
                            <div className="text-center">
                                <span className="material-symbols-outlined text-primary text-4xl animate-spin">refresh</span>
                                <p className="mt-2 text-on-surface-variant font-bold">Loading investigation network...</p>
                            </div>
                        </div>
                    ) : fetchError ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-surface-container-highest text-on-surface-variant z-10">
                            <span className="material-symbols-outlined text-6xl mb-4 text-error">error</span>
                            <h3 className="text-xl font-bold text-error">{fetchError}</h3>
                        </div>
                    ) : elements.length === 0 ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-surface-container-highest text-on-surface-variant z-10">
                            <span className="material-symbols-outlined text-6xl mb-4 opacity-50">hub</span>
                            <h3 className="text-xl font-bold">No confirmed network relationships found.</h3>
                            <p className="text-sm mt-2 text-center max-w-md">This does not indicate absence of activity.<br/>Only validated relationships are displayed.</p>
                        </div>
                    ) : (
                        <CytoscapeComponent 
                            elements={elements} 
                            style={{ width: '100%', height: '100%' }} 
                            layout={{ name: 'cose', padding: 50, animate: true }}
                            stylesheet={stylesheet}
                            cy={(cy) => {
                                cyRef.current = cy; (window as any).cy = cy;
                                cy.removeListener('tap');
                                cy.on('tap', 'node', (evt) => {
                                    setSelectedEdge(null);
                                    setSelectedNode(evt.target.data());
                                });
                                cy.on('tap', 'edge', (evt) => {
                                    setSelectedNode(null);
                                    setSelectedEdge(evt.target.data());
                                });
                                cy.on('tap', (evt) => {
                                    if(evt.target === cy) {
                                        setSelectedNode(null);
                                        setSelectedEdge(null);
                                        setSelectedLead(null);
                                    }
                                });
                            }}
                        />
                    )}
                </main>

                {/* Right Details Panel */}
                {(selectedNode || selectedEdge) ? (
                    <aside className="w-80 bg-surface-container-lowest border-l border-outline-variant flex flex-col shrink-0 overflow-y-auto z-10 shadow-[-4px_0_15px_rgba(0,0,0,0.05)]">
                        {selectedNode && (
                            <>
                            <div className="p-4 border-b border-outline-variant bg-primary-container text-on-primary-container flex justify-between items-center shrink-0">
                                <div className="flex items-center gap-2">
                                    <span className="material-symbols-outlined">
                                        {selectedNode.type === 'person' ? 'person' : 
                                         selectedNode.type === 'location' ? 'location_on' :
                                         selectedNode.type === 'vehicle' ? 'directions_car' :
                                         selectedNode.type === 'upi_id' ? 'account_balance_wallet' :
                                         selectedNode.type === 'phone' ? 'call' : 'corporate_fare'}
                                    </span>
                                    <h2 className="font-bold truncate" title={selectedNode.label}>{selectedNode.label}</h2>
                                </div>
                                <button onClick={() => setSelectedNode(null)} className="hover:bg-primary rounded p-1 text-on-primary">
                                    <span className="material-symbols-outlined text-sm">close</span>
                                </button>
                            </div>
                            <div className="p-4 space-y-4">
                                <div className="flex gap-4">
                                    <div className="flex-1">
                                        <label className="text-xs text-on-surface-variant uppercase font-bold tracking-wider">Entity ID</label>
                                        <p className="text-sm font-mono text-primary bg-surface-container-low p-2 rounded mt-1">{selectedNode.id}</p>
                                    </div>
                                    <div className="flex-1">
                                        <label className="text-xs text-on-surface-variant uppercase font-bold tracking-wider">Type</label>
                                        <p className="text-sm capitalize mt-1 border border-outline-variant inline-block px-2 py-1 rounded bg-surface-container">{selectedNode.type}</p>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-xs text-on-surface-variant uppercase font-bold tracking-wider">Canonical Name</label>
                                    <p className="text-sm text-on-surface mt-1">{selectedNode.label}</p>
                                </div>
                                
                                {analytics && analytics.metrics && (
                                    <div>
                                        <label className="text-xs text-on-surface-variant uppercase font-bold tracking-wider">Graph Metrics</label>
                                        <div className="mt-2 space-y-2">
                                            {(() => {
                                                const met = analytics.metrics.find((m: any) => m.entity_id === selectedNode.id);
                                                if (!met) return <p className="text-sm text-on-surface-variant">No metrics available</p>;
                                                return (
                                                    <>
                                                    <div className="flex justify-between items-center bg-surface-container-low p-2 rounded border border-outline-variant">
                                                        <span className="text-sm">Degree Centrality</span>
                                                        <span className="text-sm font-mono font-bold">{met.degree}</span>
                                                    </div>
                                                    <div className="flex justify-between items-center bg-surface-container-low p-2 rounded border border-outline-variant">
                                                        <span className="text-sm">Betweenness</span>
                                                        <span className="text-sm font-mono font-bold">{met.betweenness_centrality.toFixed(4)}</span>
                                                    </div>
                                                    </>
                                                )
                                            })()}
                                        </div>
                                    </div>
                                )}
                            </div>
                            </>
                        )}

                        {selectedEdge && (
                            <>
                            <div className="p-4 border-b border-outline-variant bg-saffron-accent text-white flex justify-between items-center shrink-0">
                                <div className="flex items-center gap-2">
                                    <span className="material-symbols-outlined">commit</span>
                                    <h2 className="font-bold truncate">Relationship Details</h2>
                                </div>
                                <button onClick={() => setSelectedEdge(null)} className="hover:bg-white/20 rounded p-1">
                                    <span className="material-symbols-outlined text-sm">close</span>
                                </button>
                            </div>
                            <div className="p-4 space-y-4">
                                <div className="flex flex-col gap-2 bg-surface-container-low border border-outline-variant p-3 rounded">
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-on-surface-variant font-bold uppercase">Relationship ID</span>
                                        <span className="text-xs font-mono text-primary bg-surface-container py-1 px-2 rounded border border-outline-variant">{selectedEdge.relationship_id || selectedEdge.id}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-on-surface-variant font-bold uppercase">Type</span>
                                        <span className="text-sm font-bold text-on-surface">{selectedEdge.relationship_type || selectedEdge.label}</span>
                                    </div>
                                </div>
                                
                                <div>
                                    <label className="text-xs text-on-surface-variant uppercase font-bold tracking-wider">Endpoints</label>
                                    <div className="mt-2 space-y-2">
                                        <div className="text-sm flex flex-col p-2 bg-surface-container-low border border-outline-variant rounded">
                                            <span className="text-xs text-on-surface-variant uppercase">Source</span>
                                            <span className="font-mono mt-1 text-primary">{selectedEdge.source}</span>
                                        </div>
                                        <div className="flex justify-center text-on-surface-variant">
                                            <span className="material-symbols-outlined text-sm">arrow_downward</span>
                                        </div>
                                        <div className="text-sm flex flex-col p-2 bg-surface-container-low border border-outline-variant rounded">
                                            <span className="text-xs text-on-surface-variant uppercase">Target</span>
                                            <span className="font-mono mt-1 text-primary">{selectedEdge.target}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="mt-4 pt-4 border-t border-outline-variant">
                                    <p className="text-xs text-on-surface-variant">
                                        This relationship has been validated by the NETRA backend and projected into Apache AGE.
                                    </p>
                                </div>
                            </div>
                            </>
                        )}
                    </aside>
                ) : null}
            </div>
            <Chatbot />
        </div>
        </PageTransition>
    );
};

export default GraphExplorer;
