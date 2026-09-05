import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
    const navigate = useNavigate();
    const { logout, officer } = useAuth();
    
    const handleLogout = () => {
        logout();
        navigate("/");
    };
    
    return (
        <aside className="hidden md:flex flex-col h-screen w-56 bg-surface-container-low border-r border-outline-variant py-4 px-3 sticky top-0 shrink-0 z-20">
            {/* Header / Brand */}
            <div className="flex items-center gap-3 mb-2 px-2">
                <div className="w-10 h-10 bg-surface-container-highest rounded-full flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-primary text-xl">account_balance</span>
                </div>
                <div>
                    <h1 className="text-label-lg font-bold text-primary leading-tight">NCRB</h1>
                    <h2 className="text-[10px] uppercase tracking-wider text-on-surface-variant font-semibold">AI Portal</h2>
                </div>
            </div>
            
            {/* Nav Items */}
            <nav className="flex-1 overflow-y-auto mt-4 space-y-1">
                <NavLink to="/dashboard" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface hover:bg-surface-container-highest'}`}>
                    <span className="material-symbols-outlined text-[20px]">dashboard</span>
                    Dashboard
                </NavLink>
                <NavLink to="/start-investigation" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface hover:bg-surface-container-highest'}`}>
                    <span className="material-symbols-outlined text-[20px]">add_circle</span>
                    Start Investigation
                </NavLink>
                <NavLink to="/network-analysis" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive || window.location.pathname.includes('/network-analysis') || (window.location.pathname.includes('/network') && window.location.pathname.includes('/cases/')) ? 'bg-primary-container text-on-primary-container' : 'text-on-surface hover:bg-surface-container-highest'}`}>
                    <span className="material-symbols-outlined text-[20px]">hub</span>
                    Network Analysis
                </NavLink>
                <NavLink to="/criminal-profiling" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive || window.location.pathname.includes('/criminal-profiling') || (window.location.pathname.includes('/profiling') && window.location.pathname.includes('/cases/')) ? 'bg-primary-container text-on-primary-container' : 'text-on-surface hover:bg-surface-container-highest'}`}>
                    <span className="material-symbols-outlined text-[20px]">person_search</span>
                    Criminal Profiling
                </NavLink>
                <NavLink to="/case-tracker" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive || window.location.pathname === '/case-tracker' || (window.location.pathname.includes('/cases/') && !window.location.pathname.includes('/network') && !window.location.pathname.includes('/profiling')) ? 'bg-primary-container text-on-primary-container' : 'text-on-surface hover:bg-surface-container-highest'}`}>
                    <span className="material-symbols-outlined text-[20px]">track_changes</span>
                    Case Tracker
                </NavLink>
                <NavLink to="/upload" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-primary-container text-on-primary-container' : 'text-on-surface hover:bg-surface-container-highest'}`}>
                    <span className="material-symbols-outlined text-[20px]">upload_file</span>
                    Upload Evidence
                </NavLink>
            </nav>
            
            {/* User Profile / Settings */}
                        <div className="mt-auto pt-4 border-t border-outline-variant space-y-1">
                {officer && (
                    <div className="mb-4 px-3 flex flex-col gap-1">
                        <span className="text-sm font-bold text-on-surface">{officer.name}</span>
                        <span className="text-xs text-on-surface-variant font-mono">{officer.officerId}</span>
                        <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded w-fit uppercase font-bold">{officer.role}</span>
                    </div>
                )}
                <button onClick={handleLogout} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-error hover:bg-error-container hover:text-on-error-container transition-colors">
                    <span className="material-symbols-outlined text-[20px]">logout</span>
                    Logout
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
