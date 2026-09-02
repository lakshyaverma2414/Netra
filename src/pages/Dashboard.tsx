import { useNavigate, NavLink, Link } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import sampleGraph from '../mockData/sampleGraph.json';
import Chatbot from '../components/Chatbot';
import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import { DashboardSkeleton } from '../components/Skeleton';
import { useState, useEffect } from 'react';
import cases from '../mockData/cases.json';

const Dashboard = () => {
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResult, setSearchResult] = useState<any>(null);
    const [searchStatus, setSearchStatus] = useState<'idle' | 'empty' | 'not-found' | 'found'>('idle');
    const navigate = useNavigate();

    const handleSearch = () => {
        try {
            const query = searchQuery.trim();
            if (!query) {
                setSearchStatus('empty');
                setSearchResult(null);
                return;
            }

            let localCases = [];
            try {
                localCases = JSON.parse(localStorage.getItem('userCases') || '[]');
                if (!Array.isArray(localCases)) localCases = [];
            } catch (err) {
                console.error(err);
            }
            
            const allCases = [...cases, ...localCases];
            
            const found = allCases.find((c: any) => c.id && String(c.id).toLowerCase() === query.toLowerCase());
            
            if (found) {
                setSearchResult(found);
                setSearchStatus('found');
            } else {
                setSearchResult(null);
                setSearchStatus('not-found');
            }
        } catch (error) {
            setSearchStatus('not-found');
        }
    };
    useEffect(() => { setTimeout(() => setIsLoading(false), 800); }, []);

    const nodes = sampleGraph.filter((el: any) => !el.data.source);
    const totalEntities = nodes.length;
    const totalOrgs = nodes.filter((n: any) => n.data.type === 'organization').length;
    const totalPersons = nodes.filter((n: any) => n.data.type === 'person').length;
    const criticalEntities = nodes.filter((n: any) => n.data.riskLevel === 'Critical').length;

    const topInfluencers = nodes
        .filter((n: any) => n.data.type === 'person')
        .sort((a: any, b: any) => (b.data.riskScore || 0) - (a.data.riskScore || 0))
        .slice(0, 3);
        
    const recentEntities = nodes
        .sort((a: any, b: any) => (b.data.riskScore || 0) - (a.data.riskScore || 0))
        .slice(0, 3);

    const typeCounts = nodes.reduce((acc: any, node: any) => {
        acc[node.data.type] = (acc[node.data.type] || 0) + 1;
        return acc;
    }, {});

    const pieData = Object.entries(typeCounts).map(([key, val]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value: val
    }));

    const COLORS: Record<string, string> = {
        Person: '#0B2447',
        Location: '#16a34a',
        Vehicle: '#f97316',
        Organization: '#9333ea',
        Phone: '#0ea5e9'
    };

    
    
    return (
        
        <PageTransition>
      <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased selection:bg-saffron-accent selection:text-white overflow-hidden">
            
{/*  SideNavBar (Hidden on Mobile, Visible on md+)  */}
<Sidebar />
<div className="flex-1 flex flex-col min-w-0">
{/*  TopNavBar (Used primarily as mobile header and desktop secondary nav)  */}
<header className="bg-primary text-on-primary w-full border-b border-outline-variant sticky top-0 z-30 flex justify-between items-center px-margin-mobile md:px-margin-desktop h-12 max-w-container-max mx-auto md:w-full">
<div className="flex items-center gap-4">
{/*  Mobile Menu Button (Hidden on Desktop)  */}
<button className="md:hidden p-2 text-on-primary hover:bg-primary-container rounded transition-colors">
<span className="material-symbols-outlined">menu</span>
</button>
<div className="text-title-lg font-display-lg font-bold text-on-primary md:hidden">
                    NCRB
                </div>
{/*  Desktop Navigation Links in Top Bar  */}

</div>
<div className="flex items-center gap-4">
<span className="text-label-md font-label-md hidden sm:inline-block">हिन्दी/English</span>
<button className="p-2 hover:bg-primary-container transition-colors rounded-full opacity-80 hover:opacity-100 relative">
<span className="material-symbols-outlined">notifications</span>
<span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full"></span>
</button>
<button className="p-2 hover:bg-primary-container transition-colors rounded-full opacity-80 hover:opacity-100">
<span className="material-symbols-outlined">account_circle</span>
</button>
</div>
</header>
{/*  Main Content Area  */}
<main className="flex-1 overflow-y-auto p-2 md:p-4 max-w-container-max mx-auto w-full flex flex-col gap-3 md:gap-4">
{isLoading ? <DashboardSkeleton /> : (
<>

{/*  Page Header  */}
<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
<div>
<h2 className="text-title-md md:text-title-lg font-headline-lg-mobile md:font-headline-lg text-primary">Dashboard Overview</h2>
<p className="text-body-md font-body-md text-on-surface-variant mt-1">Network Analysis &amp; Intelligence Summary</p>
</div>
<div className="flex gap-2">
<button className="px-3 py-1 text-sm bg-surface-container-lowest border border-outline-variant rounded-lg text-label-md font-label-md flex items-center gap-2 hover:bg-surface-container-low transition-colors">
<span className="material-symbols-outlined text-sm">download</span>
                        Export Report
                    </button>
<button className="px-3 py-1 text-sm bg-surface-container-lowest border border-outline-variant rounded-lg text-label-md font-label-md flex items-center gap-2 hover:bg-surface-container-low transition-colors">
<span className="material-symbols-outlined text-sm">filter_list</span>
                        Filter
                    </button>
</div>
</div>
{/*  Case Search Section  */}
<div className="bg-surface-container-lowest p-6 rounded-xl border border-outline-variant shadow-sm mb-4">
    <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
        <span className="material-symbols-outlined">search</span> Case Search
    </h3>
    <form 
          onSubmit={(e) => { e.preventDefault(); handleSearch(); }} 
          className="flex gap-2"
      >
          <input 
              type="text" 
              placeholder="Search Case ID (e.g. NCRB-2026-001)" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 bg-surface-container border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary"
          />
          <button 
              type="submit"
              className="px-6 py-2 bg-primary text-on-primary rounded-lg font-bold hover:bg-opacity-90 flex items-center gap-2 transition-all shadow-md active:scale-95 cursor-pointer"
          >
              <span className="material-symbols-outlined text-sm">search</span> Search
          </button>
      </form>

    {searchStatus === 'empty' && (
        <p className="text-error mt-2 text-sm font-bold">Please enter a Case ID.</p>
    )}
    
    {searchStatus === 'not-found' && (
        <p className="text-error mt-2 text-sm font-bold">No case found for this Case ID.</p>
    )}

    {searchStatus === 'found' && searchResult && (
        <div className="mt-6 border border-outline-variant rounded-xl overflow-hidden bg-surface-container-lowest">
            <div className="bg-primary-container p-4 border-b border-outline-variant flex justify-between items-center">
                <h4 className="text-lg font-bold text-primary flex items-center gap-2">
                    <span className="material-symbols-outlined">folder_special</span> Case Summary: {searchResult.id}
                </h4>
                <span className={`px-3 py-1 rounded text-xs font-bold ${searchResult.status === 'ACTIVE' ? 'bg-india-green/20 text-india-green' : 'bg-surface-container-highest text-on-surface-variant'}`}>
                    {searchResult.status || "UNKNOWN"}
                </span>
            </div>
            
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Case Info */}
                <div className="space-y-3">
                    <h5 className="font-bold text-on-surface-variant text-xs uppercase tracking-wider border-b border-outline-variant pb-1">Case Information</h5>
                    <div className="text-sm"><span className="font-bold text-on-surface-variant">Crime Type:</span> {searchResult.crimeType || "N/A"}</div>
                    <div className="text-sm"><span className="font-bold text-on-surface-variant">Date of Incident:</span> {searchResult.dateOfIncident || "N/A"}</div>
                    <div className="text-sm"><span className="font-bold text-on-surface-variant">Location:</span> {searchResult.location || "N/A"}</div>
                    <div className="text-sm"><span className="font-bold text-on-surface-variant">Description:</span> {searchResult.description || searchResult.title || "N/A"}</div>
                    
                    <h5 className="font-bold text-on-surface-variant text-xs uppercase tracking-wider border-b border-outline-variant pb-1 mt-4">Investigation Information</h5>
                    <div className="text-sm"><span className="font-bold text-on-surface-variant">Investigating Officer:</span> {searchResult.assignedOfficer || "Unassigned"}</div>

                    <h5 className="font-bold text-on-surface-variant text-xs uppercase tracking-wider border-b border-outline-variant pb-1 mt-4">Final Investigation Result</h5>
                    {searchResult.status === 'SOLVED' || searchResult.status === 'CLOSED' ? (
                        <>
                            <div className="text-sm"><span className="font-bold text-on-surface-variant">Final Perpetrator:</span> <span className="text-error font-bold">{searchResult.finalPerpetrator || "Unknown"}</span></div>
                            <div className="text-sm"><span className="font-bold text-on-surface-variant">Final Status:</span> <span className="text-india-green font-bold">{searchResult.status}</span></div>
                            <div className="text-sm"><span className="font-bold text-on-surface-variant">Key Findings:</span> {searchResult.keyFindings || "N/A"}</div>
                        </>
                    ) : (
                        <div className="text-sm text-on-surface-variant italic font-bold">Investigation Ongoing / Perpetrator Not Yet Identified</div>
                    )}
                </div>

                {/* Suspect & Evidence Info */}
                <div className="space-y-3">
                    <h5 className="font-bold text-on-surface-variant text-xs uppercase tracking-wider border-b border-outline-variant pb-1">Initial Suspect</h5>
                    {searchResult.initialSuspect ? (
                        <>
                            <div className="text-sm"><span className="font-bold text-on-surface-variant">Name:</span> {searchResult.initialSuspect.name || "Unknown"}</div>
                            <div className="text-sm"><span className="font-bold text-on-surface-variant">Phone:</span> {searchResult.initialSuspect.phone || "Unknown"}</div>
                            <div className="text-sm"><span className="font-bold text-on-surface-variant">Address:</span> {searchResult.initialSuspect.address || "Unknown"}</div>
                        </>
                    ) : (
                        <div className="text-sm text-on-surface-variant italic">Not Yet Identified</div>
                    )}
                    
                    <h5 className="font-bold text-on-surface-variant text-xs uppercase tracking-wider border-b border-outline-variant pb-1 mt-4">Evidence & Findings</h5>
                    <div className="text-sm"><span className="font-bold text-on-surface-variant">Total Evidence Items:</span> {searchResult.evidence || 0}</div>
                    {searchResult.evidence === 0 ? <div className="text-sm text-error italic mt-1">No evidence uploaded yet</div> : null} 
                </div>
            </div>

            <div className="bg-surface-container p-4 border-t border-outline-variant flex justify-end">
                <Link 
                      to={`/cases/${searchResult.id}/network`}
                      className="px-6 py-2 bg-saffron-accent text-white rounded-lg font-bold hover:bg-opacity-90 flex items-center gap-2 transition-all shadow-sm cursor-pointer"
                  >
                      <span className="material-symbols-outlined text-sm">explore</span> View & Explore
                  </Link>
            </div>
        </div>
    )}
</div>
{/*  Hero Stats Grid  */}
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
{/*  Stat Card 1  */}
<div className="bg-surface-container-lowest p-3 rounded-xl border border-outline-variant border-t-4 border-t-primary shadow-sm hover:shadow-md transition-shadow">
<div className="flex justify-between items-start mb-2">
<p className="text-label-sm font-label-sm text-on-surface-variant uppercase tracking-wider">Total Entities</p>
<div className="p-2 bg-primary-fixed rounded-lg text-primary">
<span className="material-symbols-outlined text-lg">folder_open</span>
</div>
</div>
<h3 className="text-2xl font-bold text-primary">{totalEntities}</h3>
<div className="flex items-center gap-1 mt-2 text-india-green text-label-sm font-label-sm">
<span className="material-symbols-outlined text-sm">trending_up</span>
<span className="">Live Tracking</span>
</div>
</div>
{/*  Stat Card 2  */}
<div className="bg-surface-container-lowest p-3 rounded-xl border border-outline-variant border-t-4 border-t-saffron-accent shadow-sm hover:shadow-md transition-shadow">
<div className="flex justify-between items-start mb-2">
<p className="text-label-sm font-label-sm text-on-surface-variant uppercase tracking-wider">Active Networks</p>
<div className="p-2 bg-secondary-fixed rounded-lg text-secondary">
<span className="material-symbols-outlined text-lg">hub</span>
</div>
</div>
<h3 className="text-2xl font-bold text-primary">{totalOrgs}</h3>
<div className="flex items-center gap-1 mt-2 text-error text-label-sm font-label-sm">
<span className="material-symbols-outlined text-sm">warning</span>
<span className="">Active threat</span>
</div>
</div>
{/*  Stat Card 3  */}
<div className="bg-surface-container-lowest p-3 rounded-xl border border-outline-variant border-t-4 border-t-primary shadow-sm hover:shadow-md transition-shadow">
<div className="flex justify-between items-start mb-2">
<p className="text-label-sm font-label-sm text-on-surface-variant uppercase tracking-wider">Persons Tracked</p>
<div className="p-2 bg-primary-fixed rounded-lg text-primary">
<span className="material-symbols-outlined text-lg">groups</span>
</div>
</div>
<h3 className="text-2xl font-bold text-primary">{totalPersons}</h3>
<div className="flex items-center gap-1 mt-2 text-on-surface-variant text-label-sm font-label-sm">
<span className="material-symbols-outlined text-sm">horizontal_rule</span>
<span className="">Stable</span>
</div>
</div>
{/*  Stat Card 4  */}
<div className="bg-surface-container-lowest p-3 rounded-xl border border-outline-variant border-t-4 border-t-error shadow-sm hover:shadow-md transition-shadow">
<div className="flex justify-between items-start mb-2">
<p className="text-label-sm font-label-sm text-on-surface-variant uppercase tracking-wider">Critical Risk</p>
<div className="p-2 bg-error-container rounded-lg text-error">
<span className="material-symbols-outlined text-lg">dangerous</span>
</div>
</div>
<h3 className="text-2xl font-bold text-error">{criticalEntities}</h3>
<div className="flex items-center gap-1 mt-2 text-error text-label-sm font-label-sm">
<span className="material-symbols-outlined text-sm">priority_high</span>
<span className="">Requires Attention</span>
</div>
</div>
</div>

{/*  Middle Section Grid  */}
<div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
{/*  Left: Recent Cases Table (2/3 width)  */}
<div className="lg:col-span-2 bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden shadow-sm flex flex-col">
<div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-bright">
<h3 className="text-title-lg font-title-lg text-primary">High Risk Entities</h3>
<a className="text-label-sm font-label-sm text-primary hover:underline flex items-center" href="#">View All <span className="material-symbols-outlined text-sm">chevron_right</span></a>
</div>
<div className="overflow-x-auto">
<table className="w-full text-left border-collapse">
<thead>
<tr className="bg-surface-container-low text-label-sm font-label-sm text-on-surface-variant">
<th className="p-2 text-xs font-medium border-b border-outline-variant">Entity ID</th>
<th className="p-2 text-xs font-medium border-b border-outline-variant">Name / Label</th>
<th className="p-2 text-xs font-medium border-b border-outline-variant">Type</th>
<th className="p-2 text-xs font-medium border-b border-outline-variant">Risk Level</th>
<th className="p-2 text-xs font-medium border-b border-outline-variant">Score</th>
</tr>
</thead>
<tbody className="text-body-md font-body-md divide-y divide-outline-variant">
{recentEntities.map((entity: any, idx: number) => (
<tr key={idx} className="hover:bg-surface-bright transition-colors">
<td className="p-2 text-sm font-medium text-primary uppercase">{entity.data.id}</td>
<td className="p-2 text-sm">{entity.data.label}</td>
<td className="p-2 text-sm capitalize">{entity.data.type}</td>
<td className="p-2 text-sm">
<span className={`inline-flex items-center px-2 py-1 rounded-full text-[10px] font-bold ${
    entity.data.riskLevel === 'Critical' ? 'bg-error text-white' :
    entity.data.riskLevel === 'High' ? 'bg-saffron-accent text-white' :
    entity.data.riskLevel === 'Medium' ? 'bg-primary-container text-on-primary-container' : 'bg-surface-container-highest text-on-surface-variant'
}`}>
{entity.data.riskLevel}
</span>
</td>
<td className="p-2 text-sm font-medium">{entity.data.riskScore}</td>
</tr>
))}
</tbody>
</table>
</div>
</div>
{/*  Right: Chart (1/3 width)  */}
<div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 shadow-sm flex flex-col">
<h3 className="text-title-md font-bold text-primary mb-2">Entity Type Distribution</h3>
<div className="flex-1 w-full min-h-[120px]">
<ResponsiveContainer width="100%" height="100%">
    <PieChart>
        <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            innerRadius={30}
            outerRadius={50}
            paddingAngle={5}
            dataKey="value"
        >
            {pieData.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#8884d8'} />
            ))}
        </Pie>
        <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
    </PieChart>
</ResponsiveContainer>
</div>
<div className="mt-2 grid grid-cols-2 gap-2">
{pieData.map((entry: any, idx: number) => (
    <div key={idx} className="flex items-center gap-2 text-[10px] font-medium text-on-surface-variant">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[entry.name] || '#8884d8' }}></span> 
        {entry.name} ({entry.value})
    </div>
))}
</div>
</div>
</div>

{/*  Bottom Section: Top Influencers  */}
<div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 shadow-sm hover:shadow-md">
<div className="flex justify-between items-center mb-2">
<h3 className="text-title-md font-bold text-primary">Top Network Influencers</h3>
<button className="p-1 hover:bg-surface-container-low rounded"><span className="material-symbols-outlined text-on-surface-variant">more_vert</span></button>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
{topInfluencers.map((person: any, idx: number) => (
<div key={idx} className="flex items-center gap-3 p-2 border border-outline-variant rounded-lg hover:border-primary transition-colors cursor-pointer bg-surface-bright">
<div className="w-8 h-8 bg-surface-container-highest rounded-full flex items-center justify-center shrink-0">
<span className="material-symbols-outlined text-sm text-on-surface-variant">person</span>
</div>
<div className="flex-1 min-w-0">
<h4 className="text-label-md font-label-md font-semibold text-primary truncate">{person.data.label}</h4>
<p className="text-[10px] text-on-surface-variant truncate">ID: {person.data.id.toUpperCase()}</p>
<div className="mt-1 w-full bg-surface-container-high rounded-full h-1.5">
<div className={`h-1.5 rounded-full ${person.data.riskScore >= 90 ? 'bg-error' : 'bg-saffron-accent'}`} style={{ width: `${person.data.riskScore}%` }}></div>
</div>
<p className={`text-[9px] text-right mt-1 font-bold ${person.data.riskScore >= 90 ? 'text-error' : 'text-saffron-accent'}`}>
{person.data.riskScore} / 100 Risk
</p>
</div>
</div>
))}
</div>
</div>


</>
)}
</main>
{/*  Footer  */}
<footer className="bg-surface-container-highest w-full border-t border-outline-variant py-2 px-margin-mobile md:px-margin-desktop mt-auto">
<div className="max-w-container-max mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
<div className="text-center md:text-left">
<p className="text-label-md font-label-md font-bold text-primary mb-0 text-xs">NCRB AI-Portal</p>
<p className="text-label-sm font-label-sm text-on-surface-variant">© 2024 National Crime Records Portal. All Rights Reserved. Govt of India.</p>
</div>
<div className="flex flex-wrap justify-center gap-4 text-label-sm font-label-sm">
<a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Privacy Policy</a>
<a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Terms of Service</a>
<a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Hyperlinking Policy</a>
<a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Help</a>
</div>
</div>
</footer>
</div>


<Chatbot />
</div>
    </PageTransition>
  );
};

export default Dashboard;
