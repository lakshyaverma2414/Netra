import { useParams, NavLink } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import cases from '../mockData/cases.json';

const CaseWorkspace = () => {
    const { caseId } = useParams();
    const caseData = cases.find(c => c.id === caseId) || cases[0];

    return (
        <PageTransition>
            <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased overflow-hidden">
                <Sidebar />
                <main className="flex-1 overflow-y-auto bg-surface flex flex-col">
                    {/* Case Header */}
                    <div className="bg-surface-container-lowest border-b border-outline-variant p-4 md:px-8 py-6 sticky top-0 z-10 shadow-sm">
                        <div className="flex items-center gap-2 text-sm text-on-surface-variant mb-2">
                            <NavLink to="/case-tracker" className="hover:text-primary transition-colors flex items-center gap-1">
                                <span className="material-symbols-outlined text-sm">arrow_back</span> My Cases
                            </NavLink>
                            <span>/</span>
                            <span>{caseData.id}</span>
                        </div>
                        <div className="flex justify-between items-start">
                            <div>
                                <h1 className="text-2xl font-bold text-primary">{caseData.id} — {caseData.title}</h1>
                                <div className="flex gap-4 mt-2 text-sm">
                                    <span className={`font-bold ${caseData.status === 'ACTIVE' ? 'text-india-green' : 'text-on-surface-variant'}`}>● {caseData.status}</span>
                                    <span className="text-on-surface-variant">Priority: <strong className={`font-bold ${caseData.risk === 'CRITICAL' ? 'text-error' : 'text-primary'}`}>{caseData.risk}</strong></span>
                                </div>
                            </div>
                        </div>
                        
                        {/* Case Navigation Tabs */}
                        <div className="flex gap-6 mt-6 border-b border-outline-variant">
                            <NavLink end to={`/cases/${caseId}`} className={({ isActive }) => `pb-2 font-bold text-sm ${isActive ? 'text-saffron-accent border-b-2 border-saffron-accent' : 'text-on-surface-variant hover:text-primary'}`}>Overview</NavLink>
                            <NavLink to={`/cases/${caseId}/network`} className={({ isActive }) => `pb-2 font-bold text-sm ${isActive ? 'text-saffron-accent border-b-2 border-saffron-accent' : 'text-on-surface-variant hover:text-primary'}`}>Network</NavLink>
                            <NavLink to={`/cases/${caseId}/profiling`} className={({ isActive }) => `pb-2 font-bold text-sm ${isActive ? 'text-saffron-accent border-b-2 border-saffron-accent' : 'text-on-surface-variant hover:text-primary'}`}>Persons</NavLink>
                            <NavLink to={`/upload`} className={({ isActive }) => `pb-2 font-bold text-sm ${isActive ? 'text-saffron-accent border-b-2 border-saffron-accent' : 'text-on-surface-variant hover:text-primary'}`}>Evidence</NavLink>
                        </div>
                    </div>

                    {/* Workspace Content */}
                    <div className="p-4 md:p-8 max-w-container-max mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2 space-y-6">
                            <div className="bg-surface-container-lowest border border-outline-variant p-6 rounded-xl shadow-sm">
                                <h2 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
                                    <span className="material-symbols-outlined">analytics</span> Investigation Progress
                                </h2>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-on-surface-variant">Overall Completion</span>
                                    <span className="font-bold text-primary">{caseData.investigationProgress}%</span>
                                </div>
                                <div className="w-full bg-surface-container-highest rounded-full h-2 mb-4">
                                    <div className="bg-primary h-2 rounded-full" style={{ width: `${caseData.investigationProgress}%` }}></div>
                                </div>
                                <div className="grid grid-cols-3 gap-4 text-center">
                                    <div className="bg-surface-container p-3 rounded-lg">
                                        <div className="text-2xl font-bold text-primary">{caseData.tasks.completed}/{caseData.tasks.total}</div>
                                        <div className="text-[10px] uppercase tracking-wider text-on-surface-variant mt-1">Tasks</div>
                                    </div>
                                    <div className="bg-surface-container p-3 rounded-lg">
                                        <div className="text-2xl font-bold text-primary">{caseData.evidence}</div>
                                        <div className="text-[10px] uppercase tracking-wider text-on-surface-variant mt-1">Evidence Files</div>
                                    </div>
                                    <div className="bg-surface-container p-3 rounded-lg">
                                        <div className="text-2xl font-bold text-primary">{caseData.leads}</div>
                                        <div className="text-[10px] uppercase tracking-wider text-on-surface-variant mt-1">Active Leads</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="bg-surface-container-lowest border border-outline-variant p-6 rounded-xl shadow-sm">
                                <h2 className="text-sm font-bold text-on-surface-variant uppercase tracking-wider mb-4">Case Details</h2>
                                <div className="space-y-3 text-sm">
                                    <div className="flex justify-between border-b border-outline-variant pb-2">
                                        <span className="text-on-surface-variant">Assigned Officer</span>
                                        <span className="font-medium">{caseData.assignedOfficer}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-outline-variant pb-2">
                                        <span className="text-on-surface-variant">Creation Date</span>
                                        <span className="font-medium">{caseData.creationDate}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-outline-variant pb-2">
                                        <span className="text-on-surface-variant">Last Activity</span>
                                        <span className="font-medium">{caseData.lastActivity}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </PageTransition>
    );
};
export default CaseWorkspace;
