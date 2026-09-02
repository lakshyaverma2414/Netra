import { useParams, NavLink } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import profiles from '../mockData/profiles.json';

const ProfileDetail = () => {
    const { caseId, profileId } = useParams();
    const profile = profiles.find(p => p.id === profileId) || profiles[0];

    return (
        <PageTransition>
            <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased overflow-hidden">
                <Sidebar />
                <main className="flex-1 overflow-y-auto bg-surface flex flex-col">
                    <div className="bg-surface-container-lowest border-b border-outline-variant p-4 md:px-8 py-6 sticky top-0 z-10 shadow-sm">
                        <div className="flex items-center gap-2 text-sm text-on-surface-variant mb-2">
                            <NavLink to={`/cases/${caseId}/profiling`} className="hover:text-primary transition-colors flex items-center gap-1">
                                <span className="material-symbols-outlined text-sm">arrow_back</span> Suspects List
                            </NavLink>
                            <span>/</span>
                            <span>{profile.id}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-6">
                                <img src={profile.photo} alt={profile.name} className="w-20 h-20 rounded-xl object-cover border-2 border-outline-variant shadow-sm" />
                                <div>
                                    <h1 className="text-3xl font-bold text-primary">{profile.name}</h1>
                                    <p className="text-sm text-on-surface-variant">Alias: <span className="font-bold text-on-surface">{profile.alias}</span></p>
                                </div>
                            </div>
                            <div className={`px-4 py-2 rounded-lg text-center ${profile.riskLevel === 'CRITICAL' ? 'bg-error text-white' : 'bg-saffron-accent text-white'}`}>
                                <div className="text-[10px] uppercase tracking-wider font-bold opacity-80">Risk Level</div>
                                <div className="text-xl font-bold">{profile.riskLevel} ({profile.riskScore})</div>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 md:p-8 max-w-container-max mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2 space-y-6">
                            <div className="bg-surface-container-lowest border border-outline-variant p-6 rounded-xl shadow-sm">
                                <h2 className="text-lg font-bold text-primary mb-4 border-b border-outline-variant pb-2">Criminal History & Background</h2>
                                <p className="text-sm leading-relaxed mb-4">{profile.details.history}</p>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <h3 className="text-xs font-bold text-on-surface-variant uppercase mb-2">Organizations</h3>
                                        <ul className="list-disc pl-4 text-sm">
                                            {profile.details.organizations.map((org, i) => <li key={i}>{org}</li>)}
                                        </ul>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-surface-container-lowest border border-outline-variant p-6 rounded-xl shadow-sm">
                                <h2 className="text-lg font-bold text-primary mb-4 border-b border-outline-variant pb-2">Activity Timeline</h2>
                                <div className="space-y-4">
                                    {profile.details.timeline.map((event, i) => {
                                        const [date, ...desc] = event.split(': ');
                                        return (
                                            <div key={i} className="flex gap-4">
                                                <div className="w-24 shrink-0 text-xs font-bold text-primary text-right pt-1">{date}</div>
                                                <div className="relative pb-4 border-l-2 border-outline-variant pl-4 before:absolute before:w-3 before:h-3 before:bg-saffron-accent before:rounded-full before:-left-[7px] before:top-1">
                                                    <p className="text-sm">{desc.join(': ')}</p>
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="bg-surface-container-lowest border border-outline-variant p-6 rounded-xl shadow-sm">
                                <h2 className="text-sm font-bold text-on-surface-variant uppercase tracking-wider mb-4">Quick Stats</h2>
                                <div className="space-y-3 text-sm">
                                    <div className="flex justify-between border-b border-outline-variant pb-2">
                                        <span className="text-on-surface-variant">Primary Role</span>
                                        <span className="font-bold">{profile.role}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-outline-variant pb-2">
                                        <span className="text-on-surface-variant">Status</span>
                                        <span className="font-bold">{profile.status}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-outline-variant pb-2">
                                        <span className="text-on-surface-variant">Known Associates</span>
                                        <span className="font-bold">{profile.knownAssociates}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-outline-variant pb-2">
                                        <span className="text-on-surface-variant">Associated Locations</span>
                                        <span className="font-bold">{profile.locations}</span>
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
export default ProfileDetail;
