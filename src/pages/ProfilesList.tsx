import { useParams, NavLink } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import { ProfileCard } from '../components/ProfileCard';
import { useState, useEffect } from 'react';
import { fetchWithAuth } from '../api/apiClient';

const ProfilesList = () => {
    const { caseId } = useParams();
    const [caseData, setCaseData] = useState<any>(null);
    const [caseProfiles, setCaseProfiles] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchCaseAndProfiles = async () => {
            if (!caseId) return;
            try {
                // Fetch case details from Spring Boot
                const caseRes = await fetchWithAuth(`/api/cases/${caseId}`);
                if (!caseRes.ok) {
                    if (caseRes.status === 404) throw new Error('NOT_FOUND');
                    throw new Error('Failed to load case');
                }
                const caseDataJson = await caseRes.json();
                setCaseData({ id: caseDataJson.caseId, title: caseDataJson.title });

                // Fetch case entities from Python AI Service
                const entRes = await fetch(`/api/v1/cases/${caseId}/entities`);
                if (!entRes.ok) throw new Error('Failed to load profiles');
                const entities = await entRes.json();

                // Map Python Entities to ProfileCard format
                const formattedProfiles = entities
                    .filter((e: any) => e.entity_type === 'PERSON') // Only show people in suspect list
                    .map((e: any) => ({
                        id: e.entity_id,
                        caseId: caseId,
                        name: e.canonical_name,
                        alias: 'Unknown',
                        photo: `https://ui-avatars.com/api/?name=${encodeURIComponent(e.canonical_name)}&background=random`,
                        riskLevel: 'HIGH', // Default placeholder
                        riskScore: 75,
                        role: e.entity_type,
                        status: 'ACTIVE',
                        knownAssociates: 0,
                        incidents: 1
                    }));

                setCaseProfiles(formattedProfiles);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCaseAndProfiles();
    }, [caseId]);

    if (error === 'NOT_FOUND') {
        return <div className="h-screen flex items-center justify-center bg-surface text-on-surface">
            <div className="text-center">
                <h1 className="text-4xl text-error font-bold">404</h1>
                <p className="mt-2 text-on-surface-variant">Case Not Found</p>
                <a href="/dashboard" className="mt-4 block text-primary hover:underline">Return to Dashboard</a>
            </div>
        </div>;
    }

    return (
        <PageTransition>
            <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased overflow-hidden">
                <Sidebar />
                <main className="flex-1 overflow-y-auto bg-surface flex flex-col">
                    <div className="bg-surface-container-lowest border-b border-outline-variant p-4 md:px-8 py-6 sticky top-0 z-10 shadow-sm">
                        <div className="flex items-center gap-2 text-sm text-on-surface-variant mb-2">
                            <NavLink to="/criminal-profiling" className="hover:text-primary transition-colors flex items-center gap-1">
                                <span className="material-symbols-outlined text-sm">arrow_back</span> Case Selection
                            </NavLink>
                            <span>/</span>
                            <span>{caseData?.id || caseId}</span>
                        </div>
                        <h1 className="text-2xl font-bold text-primary">Suspect Profiles</h1>
                        <p className="text-sm text-on-surface-variant mt-1">
                            {isLoading ? 'Loading profiles...' : `Showing ${caseProfiles.length} profiles for ${caseData?.title || 'Case'}`}
                        </p>
                    </div>

                    <div className="p-4 md:p-8 max-w-container-max mx-auto w-full">
                        {isLoading ? (
                            <div className="flex items-center justify-center py-12 gap-2 text-on-surface-variant">
                                <span className="material-symbols-outlined animate-spin">progress_activity</span> Loading profiles...
                            </div>
                        ) : error ? (
                             <div className="bg-error-container text-on-error-container p-4 rounded text-sm font-bold flex items-center gap-2">
                                <span className="material-symbols-outlined">error</span> {error}
                            </div>
                        ) : caseProfiles.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                                {caseProfiles.map(p => <ProfileCard key={p.id} profile={p} />)}
                            </div>
                        ) : (
                            <div className="py-12 text-center text-on-surface-variant">
                                <span className="material-symbols-outlined text-4xl mb-2">person_off</span>
                                <p>No criminal profiles have been logged for this case yet.</p>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </PageTransition>
    );
};
export default ProfilesList;
