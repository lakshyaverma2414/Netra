import { useNavigate } from 'react-router-dom';

interface CaseCardProps {
    caseData: any;
    actionLabel?: string;
    actionPath: string;
}

export const CaseCard = ({ caseData, actionLabel = "View Case", actionPath }: CaseCardProps) => {
    const navigate = useNavigate();

    return (
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 shadow-sm hover:shadow-md hover:border-primary transition-all flex flex-col h-full">
            <div className="flex justify-between items-start mb-3">
                <div>
                    <p className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">{caseData.id}</p>
                    <h3 className="text-lg font-bold text-primary mt-1 leading-tight">{caseData.title}</h3>
                </div>
                <span className={`px-2 py-1 rounded text-[10px] font-bold ${caseData.status === 'ACTIVE' ? 'bg-india-green/20 text-india-green' : 'bg-surface-container-highest text-on-surface-variant'}`}>
                    {caseData.status}
                </span>
            </div>
            
            <div className="grid grid-cols-2 gap-y-2 mb-4 text-sm">
                <div><span className="text-on-surface-variant">Risk:</span> <span className={`font-bold ${caseData.risk === 'CRITICAL' ? 'text-error' : caseData.risk === 'HIGH' ? 'text-saffron-accent' : 'text-primary'}`}>{caseData.risk}</span></div>
                <div><span className="text-on-surface-variant">Officer:</span> <span className="font-medium text-on-surface">{caseData.assignedOfficer}</span></div>
                
                {caseData.entities && (
                    <>
                        <div><span className="text-on-surface-variant">Persons:</span> <span className="font-medium">{caseData.entities.persons}</span></div>
                        <div><span className="text-on-surface-variant">Evidence:</span> <span className="font-medium">{caseData.evidence}</span></div>
                    </>
                )}
            </div>

            {caseData.investigationProgress !== undefined && (
                <div className="mb-4">
                    <div className="flex justify-between text-xs mb-1">
                        <span className="text-on-surface-variant">Progress</span>
                        <span className="font-bold text-primary">{caseData.investigationProgress}%</span>
                    </div>
                    <div className="w-full bg-surface-container-highest rounded-full h-1.5">
                        <div className="bg-primary h-1.5 rounded-full" style={{ width: `${caseData.investigationProgress}%` }}></div>
                    </div>
                </div>
            )}

            <div className="mt-auto pt-4 border-t border-outline-variant flex items-center justify-between">
                <span className="text-[10px] text-on-surface-variant">Updated: {caseData.lastActivity}</span>
                <button 
                    onClick={() => navigate(actionPath)}
                    className="flex items-center gap-1 text-sm font-bold text-saffron-accent hover:text-[#e68a2e] transition-colors"
                >
                    {actionLabel} <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
            </div>
        </div>
    );
};
