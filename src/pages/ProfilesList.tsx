import { useParams, NavLink } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import { ProfileCard } from '../components/ProfileCard';
import profiles from '../mockData/profiles.json';
import cases from '../mockData/cases.json';

const ProfilesList = () => {
    const { caseId } = useParams();
    const caseData = cases.find(c => c.id === caseId) || cases[0];
    const caseProfiles = profiles.filter(p => p.caseId === caseId);

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
                            <span>{caseData.id}</span>
                        </div>
                        <h1 className="text-2xl font-bold text-primary">Suspect Profiles</h1>
                        <p className="text-sm text-on-surface-variant mt-1">Showing {caseProfiles.length} profiles for {caseData.title}</p>
                    </div>

                    <div className="p-4 md:p-8 max-w-container-max mx-auto w-full">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                            {caseProfiles.length > 0 ? (
                                caseProfiles.map(p => <ProfileCard key={p.id} profile={p} />)
                            ) : (
                                <div className="col-span-full py-12 text-center text-on-surface-variant">
                                    <span className="material-symbols-outlined text-4xl mb-2">person_off</span>
                                    <p>No criminal profiles have been logged for this case yet.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </main>
            </div>
        </PageTransition>
    );
};
export default ProfilesList;
