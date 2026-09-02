import { useNavigate } from 'react-router-dom';

export const ProfileCard = ({ profile }: { profile: any }) => {
    const navigate = useNavigate();

    return (
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 shadow-sm hover:shadow-md hover:border-primary transition-all flex flex-col h-full">
            <div className="flex gap-4 mb-4">
                <img src={profile.photo} alt={profile.name} className="w-16 h-16 rounded-lg object-cover bg-surface-container-highest" />
                <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-primary truncate">{profile.name}</h3>
                    <p className="text-xs text-on-surface-variant truncate">Alias: {profile.alias}</p>
                    <span className={`inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-bold ${profile.riskLevel === 'CRITICAL' ? 'bg-error text-white' : 'bg-saffron-accent text-white'}`}>
                        {profile.riskLevel} RISK ({profile.riskScore})
                    </span>
                </div>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-xs mb-4 flex-1">
                <div className="bg-surface-container p-2 rounded">
                    <span className="block text-on-surface-variant mb-0.5">Role</span>
                    <span className="font-bold text-on-surface">{profile.role}</span>
                </div>
                <div className="bg-surface-container p-2 rounded">
                    <span className="block text-on-surface-variant mb-0.5">Status</span>
                    <span className="font-bold text-on-surface">{profile.status}</span>
                </div>
                <div className="bg-surface-container p-2 rounded">
                    <span className="block text-on-surface-variant mb-0.5">Associates</span>
                    <span className="font-bold text-on-surface">{profile.knownAssociates}</span>
                </div>
                <div className="bg-surface-container p-2 rounded">
                    <span className="block text-on-surface-variant mb-0.5">Incidents</span>
                    <span className="font-bold text-on-surface">{profile.incidents}</span>
                </div>
            </div>

            <button 
                onClick={() => navigate(`/cases/${profile.caseId}/profiling/${profile.id}`)}
                className="w-full py-2 bg-primary-container text-on-primary-container rounded-lg text-sm font-bold hover:bg-primary hover:text-white transition-colors"
            >
                View Full Profile
            </button>
        </div>
    );
};
