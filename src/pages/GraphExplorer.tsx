import { useState, useEffect, useRef } from 'react';
import { NavLink } from 'react-router-dom';
import CytoscapeComponent from 'react-cytoscapejs';
import sampleGraph from '../mockData/sampleGraph.json';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import Chatbot from '../components/Chatbot';
import { PageTransition } from '../components/PageTransition';
import { GraphSkeleton } from '../components/Skeleton';

const MIN_DATE = new Date('2023-01-01').getTime();
const MAX_DATE = new Date('2027-01-01').getTime();


import { useParams } from 'react-router-dom';
const GraphExplorer = () => {
    const { caseId } = useParams();
    const [selectedNode, setSelectedNode] = useState<any>(null);
    const [search, setSearch] = useState('');
    const [elements, setElements] = useState<any>([]);
    const cyRef = useRef<any>(null);
    const [dateRange, setDateRange] = useState<number[]>([MIN_DATE, MAX_DATE]);
    const [isLoading, setIsLoading] = useState(true);
    useEffect(() => { setTimeout(() => setIsLoading(false), 1200); }, []);

    useEffect(() => {
        // Load data initially
        setElements(sampleGraph.filter((el: any) => el.data.caseId === caseId));
    }, [caseId]);

    useEffect(() => {
        if (!cyRef.current) return;
        const cy = cyRef.current;
        
        cy.batch(() => {
            cy.elements().removeClass('dimmed highlighted hidden-date');
            
            const outOfBounds = cy.elements().filter((el: any) => {
                const dtStr = el.data('date');
                if (!dtStr) return false;
                const dt = new Date(dtStr).getTime();
                return dt < dateRange[0] || dt > dateRange[1];
            });
            outOfBounds.addClass('hidden-date');
            
            if (search.trim()) {
                const lowerSearch = search.toLowerCase();
                const visibleNodes = cy.nodes().not('.hidden-date');
                const matches = visibleNodes.filter((node: any) => {
                    const label = node.data('label');
                    return label && label.toLowerCase().includes(lowerSearch);
                });
                
                cy.elements().not('.hidden-date').addClass('dimmed').removeClass('highlighted');
                matches.removeClass('dimmed').addClass('highlighted');
                matches.connectedEdges().not('.hidden-date').removeClass('dimmed').addClass('highlighted');
            }
        });
    }, [search, dateRange]);

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
            style: {
                'opacity': 0.15
            }
        },
        {
            selector: '.hidden-date',
            style: {
                'display': 'none'
            }
        },
        {
            selector: 'node.highlighted, edge.highlighted',
            style: {
                'opacity': 1,
                'border-width': 4,
                'border-color': '#FF9933'
            }
        }
    ];

    return (
        <PageTransition>
      <div className="bg-surface text-on-surface h-screen flex flex-col font-body-md antialiased selection:bg-saffron-accent selection:text-white overflow-hidden">
            <header className="bg-primary text-on-primary w-full border-b border-outline-variant sticky top-0 z-30 flex justify-between items-center px-4 md:px-6 h-12 shrink-0">
              <div className="flex items-center gap-4 h-full">
                <div className="text-title-lg font-bold text-on-primary">NCRB</div>
                
              </div>
              <div className="flex items-center gap-4">
                <button className="p-2 hover:bg-primary-container transition-colors rounded-full relative">
                  <span className="material-symbols-outlined text-sm">notifications</span>
                </button>
                <button className="p-2 hover:bg-primary-container transition-colors rounded-full">
                  <span className="material-symbols-outlined text-sm">account_circle</span>
                </button>
              </div>
            </header>

            <div className="flex-1 flex overflow-hidden">
                {/* Left Sidebar - Filters & Search */}
                <aside className="w-64 bg-surface-container-lowest border-r border-outline-variant flex flex-col shrink-0">
                    <div className="p-4 border-b border-outline-variant">
                        <div className="relative">
                            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
                            <input 
                                type="text" 
                                placeholder="Search entities..." 
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="w-full pl-9 pr-3 py-2 bg-surface-container border border-outline-variant rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary"
                            />
                        </div>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-6">
                        <div>
                            <h3 className="text-label-sm font-bold text-on-surface-variant mb-3 uppercase tracking-wider">Entity Types</h3>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm cursor-pointer hover:text-primary">
                                    <input type="checkbox" defaultChecked className="rounded text-primary focus:ring-primary" />
                                    <span className="w-3 h-3 rounded-full bg-[#0B2447]"></span>
                                    Person (10)
                                </label>
                                <label className="flex items-center gap-2 text-sm cursor-pointer hover:text-primary">
                                    <input type="checkbox" defaultChecked className="rounded text-primary focus:ring-primary" />
                                    <span className="w-3 h-3 bg-[#16a34a]"></span>
                                    Location (4)
                                </label>
                                <label className="flex items-center gap-2 text-sm cursor-pointer hover:text-primary">
                                    <input type="checkbox" defaultChecked className="rounded text-primary focus:ring-primary" />
                                    <span className="w-0 h-0 border-l-[6px] border-r-[6px] border-b-[10px] border-transparent border-b-[#f97316]"></span>
                                    Vehicle (3)
                                </label>
                                <label className="flex items-center gap-2 text-sm cursor-pointer hover:text-primary">
                                    <input type="checkbox" defaultChecked className="rounded text-primary focus:ring-primary" />
                                    <span className="w-3 h-3 bg-[#9333ea] rotate-45"></span>
                                    Organization (3)
                                </label>
                                <label className="flex items-center gap-2 text-sm cursor-pointer hover:text-primary">
                                    <input type="checkbox" defaultChecked className="rounded text-primary focus:ring-primary" />
                                    <span className="w-3 h-3 bg-[#0ea5e9] rotate-45"></span>
                                    Phone (3)
                                </label>
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Main Graph Area */}
                <main className="flex-1 relative bg-surface-container-highest">
{isLoading ? <GraphSkeleton /> : (
<>

                    
                    {elements.length === 0 && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-surface-container-highest text-on-surface-variant z-10">
                            <span className="material-symbols-outlined text-6xl mb-4 opacity-50">hub</span>
                            <h3 className="text-xl font-bold">No connected entities available</h3>
                            <p className="text-sm mt-2">There is no network data logged for this case yet.</p>
                        </div>
                    )}
                    {elements.length > 0 && (
                        <CytoscapeComponent 
                            elements={elements} 
                            style={{ width: '100%', height: '100%' }} 
                            layout={{ name: 'cose', padding: 50, animate: false }}
                            stylesheet={stylesheet}
                            cy={(cy) => {
                                cyRef.current = cy;
                                cy.removeListener('tap');
                                cy.on('tap', 'node', (evt) => {
                                    setSelectedNode(evt.target.data());
                                });
                                cy.on('tap', (evt) => {
                                    if(evt.target === cy) setSelectedNode(null);
                                });
                            }}
                        />
                    )}
                    <div className="absolute top-4 right-4 flex gap-2">
                        <button className="p-2 bg-surface-container-lowest border border-outline-variant shadow-sm rounded text-primary hover:bg-surface-container-low">
                            <span className="material-symbols-outlined text-sm">zoom_in</span>
                        </button>
                        <button className="p-2 bg-surface-container-lowest border border-outline-variant shadow-sm rounded text-primary hover:bg-surface-container-low">
                            <span className="material-symbols-outlined text-sm">zoom_out</span>
                        </button>
                        <button className="p-2 bg-surface-container-lowest border border-outline-variant shadow-sm rounded text-primary hover:bg-surface-container-low">
                            <span className="material-symbols-outlined text-sm">filter_center_focus</span>
                        </button>
                    </div>
                    
                    {/* Date Timeline Slider */}
                    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[80%] max-w-3xl bg-surface-container-lowest border border-outline-variant p-4 rounded-xl shadow-lg z-20">
                        <div className="flex justify-between items-center mb-3">
                            <h3 className="text-label-sm font-bold text-on-surface-variant flex items-center gap-1">
                                <span className="material-symbols-outlined text-sm">calendar_month</span> Time Window Filter
                            </h3>
                            <div className="text-sm font-bold text-primary">
                                {new Date(dateRange[0]).toLocaleDateString()} - {new Date(dateRange[1]).toLocaleDateString()}
                            </div>
                        </div>
                        <div className="px-2 pb-2">
                            <Slider 
                                range 
                                min={MIN_DATE} 
                                max={MAX_DATE} 
                                value={dateRange} 
                                onChange={(val: any) => setDateRange(val as number[])} 
                                trackStyle={[{ backgroundColor: '#FF9933', height: 6 }]}
                                handleStyle={[{ borderColor: '#0B2447', backgroundColor: '#fff', opacity: 1, width: 16, height: 16, marginTop: -5 }, { borderColor: '#0B2447', backgroundColor: '#fff', opacity: 1, width: 16, height: 16, marginTop: -5 }]}
                                railStyle={{ backgroundColor: '#e2e8f0', height: 6 }}
                                step={24 * 60 * 60 * 1000} 
                            />
                        </div>
                    </div>
                
</>
)}
</main>

                {/* Right Details Panel */}
                {selectedNode ? (
                    <aside className="w-80 bg-surface-container-lowest border-l border-outline-variant flex flex-col shrink-0">
                        <div className="p-4 border-b border-outline-variant bg-primary-container text-on-primary-container flex justify-between items-center shrink-0">
                            <div className="flex items-center gap-2">
                                <span className="material-symbols-outlined">
                                    {selectedNode.type === 'person' ? 'person' : 
                                     selectedNode.type === 'location' ? 'location_on' :
                                     selectedNode.type === 'vehicle' ? 'directions_car' :
                                     selectedNode.type === 'phone' ? 'call' : 'corporate_fare'}
                                </span>
                                <h2 className="font-bold truncate" title={selectedNode.label}>{selectedNode.label}</h2>
                            </div>
                            <button onClick={() => setSelectedNode(null)} className="hover:bg-primary rounded p-1 text-on-primary">
                                <span className="material-symbols-outlined text-sm">close</span>
                            </button>
                        </div>
                        <div className="p-4 space-y-4 flex-1 overflow-y-auto">
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
                                <label className="text-xs text-on-surface-variant uppercase font-bold tracking-wider">Risk Assessment</label>
                                <div className="mt-1 flex items-center gap-3 bg-surface-container-lowest border border-outline-variant p-3 rounded">
                                    <div className={`text-2xl font-bold ${
                                        selectedNode.riskLevel === 'Critical' ? 'text-error' :
                                        selectedNode.riskLevel === 'High' ? 'text-saffron-accent' :
                                        selectedNode.riskLevel === 'Medium' ? 'text-primary' : 'text-india-green'
                                    }`}>{selectedNode.riskScore ?? 'N/A'}</div>
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold text-on-surface">Score</span>
                                        <span className="text-xs text-on-surface-variant">{selectedNode.riskLevel ?? 'Unknown'} Risk</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div>
                                <label className="text-xs text-on-surface-variant uppercase font-bold tracking-wider mb-2 block">Connections ({
                                    elements.filter((el: any) => el.data.source === selectedNode.id || el.data.target === selectedNode.id).length
                                })</label>
                                <ul className="space-y-2">
                                    {elements
                                        .filter((el: any) => el.data.source === selectedNode.id || el.data.target === selectedNode.id)
                                        .map((edge: any, idx: number) => {
                                            const isSource = edge.data.source === selectedNode.id;
                                            const otherId = isSource ? edge.data.target : edge.data.source;
                                            const otherNode = elements.find((el: any) => el.data.id === otherId);
                                            const otherLabel = otherNode ? otherNode.data.label : otherId;
                                            return (
                                                <li key={idx} className="text-sm flex flex-col p-2 bg-surface-container-low border border-outline-variant rounded">
                                                    <span className="font-medium text-primary text-xs uppercase tracking-wide opacity-80">{edge.data.label}</span>
                                                    <div className="flex items-center gap-1 mt-1 text-on-surface">
                                                        <span className="material-symbols-outlined text-xs text-on-surface-variant shrink-0">
                                                            {isSource ? 'arrow_forward' : 'arrow_back'}
                                                        </span>
                                                        <span className="truncate" title={otherLabel}>{otherLabel}</span>
                                                    </div>
                                                </li>
                                            );
                                        })}
                                </ul>
                            </div>
                            <button className="w-full py-2 bg-surface-container border border-outline-variant rounded hover:bg-surface-container-high transition-colors text-sm font-bold text-primary flex items-center justify-center gap-2 mt-4">
                                <span className="material-symbols-outlined text-sm">add</span>
                                Add to Watchlist
                            </button>
                        </div>
                    </aside>
                ) : (
                    <aside className="w-80 bg-surface-container-lowest border-l border-outline-variant flex flex-col items-center justify-center p-6 text-center text-on-surface-variant shrink-0">
                        <span className="material-symbols-outlined text-4xl mb-2 opacity-50">touch_app</span>
                        <p className="text-sm">Select a node on the graph to view intelligence details and entity connections.</p>
                    </aside>
                )}
            </div>
            <Chatbot />
        </div>
    </PageTransition>
  );
};

export default GraphExplorer;
