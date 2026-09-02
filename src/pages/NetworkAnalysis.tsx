import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import { CaseCard } from '../components/CaseCard';
import cases from '../mockData/cases.json';

const NetworkAnalysis = () => {
    return (
        <PageTransition>
            <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased overflow-hidden">
                <Sidebar />
                <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-surface">
                    <div className="max-w-container-max mx-auto">
                        <div className="mb-6 border-b border-outline-variant pb-4">
                            <h1 className="text-2xl md:text-3xl font-bold text-primary flex items-center gap-2">
                                <span className="material-symbols-outlined text-3xl">hub</span> Network Analysis
                            </h1>
                            <p className="text-on-surface-variant mt-2 text-sm">Select a case to investigate criminal networks, relationships, and connected entities.</p>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                            {cases.map((c) => (
                                <CaseCard 
                                    key={c.id} 
                                    caseData={c} 
                                    actionLabel="View Network" 
                                    actionPath={`/cases/${c.id}/network`} 
                                />
                            ))}
                        </div>
                    </div>
                </main>
            </div>
        </PageTransition>
    );
};
export default NetworkAnalysis;
