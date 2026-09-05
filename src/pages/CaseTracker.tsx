import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import { CaseCard } from '../components/CaseCard';
import { useState, useEffect } from 'react';
import { fetchWithAuth } from '../api/apiClient';

const CaseTracker = () => {
    const [cases, setCases] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchCases = async () => {
            try {
                const res = await fetchWithAuth('/api/cases');
                if (!res.ok) throw new Error('Failed to load cases');
                const data = await res.json();
                
                // Map Spring Boot CaseResponse to CaseCard format
                const formattedCases = data.map((c: any) => ({
                    id: c.caseId,
                    title: c.title,
                    status: c.status,
                    risk: 'MEDIUM', // Placeholder until implemented in backend
                    assignedOfficer: c.assignedTo || 'Unassigned',
                    lastActivity: c.updatedAt ? new Date(c.updatedAt).toLocaleDateString() : 'Unknown',
                    description: c.description
                }));
                
                setCases(formattedCases);
            } catch (err: any) {
                setError(err.message || 'Error loading cases');
            } finally {
                setIsLoading(false);
            }
        };
        fetchCases();
    }, []);

    return (
        <PageTransition>
            <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased overflow-hidden">
                <Sidebar />
                <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-surface">
                    <div className="max-w-container-max mx-auto">
                        <div className="mb-6 border-b border-outline-variant pb-4">
                            <h1 className="text-2xl md:text-3xl font-bold text-primary flex items-center gap-2">
                                <span className="material-symbols-outlined text-3xl">track_changes</span> My Cases
                            </h1>
                            <p className="text-on-surface-variant mt-2 text-sm">Cases currently assigned to you.</p>
                        </div>
                        
                        {isLoading ? (
                            <div className="flex items-center gap-2 text-on-surface-variant">
                                <span className="material-symbols-outlined animate-spin">progress_activity</span> Loading cases...
                            </div>
                        ) : error ? (
                            <div className="bg-error-container text-on-error-container p-4 rounded text-sm font-bold flex items-center gap-2">
                                <span className="material-symbols-outlined">error</span> {error}
                            </div>
                        ) : cases.length === 0 ? (
                            <div className="bg-surface-container-lowest p-8 rounded-xl border border-outline-variant text-center">
                                <span className="material-symbols-outlined text-4xl text-outline mb-2">folder_off</span>
                                <p className="text-on-surface-variant">No cases found.</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                                {cases.map((c) => (
                                    <CaseCard 
                                        key={c.id} 
                                        caseData={c} 
                                        actionLabel="Open Case" 
                                        actionPath={`/cases/${c.id}`} 
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </PageTransition>
    );
};
export default CaseTracker;
