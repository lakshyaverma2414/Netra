import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    
    const [officerId, setOfficerId] = useState('');
    const [password, setPassword] = useState('');
    const [captcha, setCaptcha] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        
        if (!officerId || !password || !captcha) {
            setError('Please fill out all required fields.');
            return;
        }

        if (captcha.length < 3) {
            setError('Please enter a valid CAPTCHA code.');
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ officerId: officerId.trim(), password, captcha: captcha.trim() })
            });


            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.message || 'Invalid credentials');
            }


            const data = await response.json();
            
            // Expected data structure: { token: "...", user: { userId, username, name, role } }
            // Let's adapt based on typical Spring Boot JWT responses
            const token = data.token;
            const officer = {
                officerId: data.user?.officerId || officerId,
                name: data.user?.name || "Officer",
                role: data.user?.role || "OFFICER"
            };

            login(token, officer);
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.message || 'Login failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <PageTransition>
            <div className="min-h-screen bg-surface flex items-center justify-center p-4">
                <div className="w-full max-w-[1000px] bg-surface-container-low rounded-xl shadow-elevation-2 flex overflow-hidden flex-col md:flex-row">
                    <div className="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center">
                        <div className="mb-8">
                            <h2 className="font-headline-md text-primary text-headline-lg">Secure Government Login</h2>
                            <p className="text-body-md font-body-md text-on-surface-variant">Enter your official credentials to access the portal.</p>
                        </div>
                        {error && (
                            <div className="bg-error-container text-on-error-container px-4 py-3 rounded text-sm font-bold flex items-center gap-2 mb-2 border border-error/20">
                                <span className="material-symbols-outlined text-error">error</span>
                                {error}
                            </div>
                        )}
                        <form onSubmit={handleLogin} className="flex flex-col gap-stack-md">
                            <div className="flex flex-col gap-base">
                                <label className="text-label-md font-label-md text-on-surface" htmlFor="officer-id">Officer ID / Username</label>
                                <div className="relative">
                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-outline">badge</span>
                                    <input className="w-full pl-10 pr-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT text-body-md font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors" id="officer-id" name="officer-id" placeholder="e.g. OFFICER_001" required={true} type="text" value={officerId} onChange={(e) => setOfficerId(e.target.value)} disabled={isLoading} />
                                </div>
                            </div>
                            <div className="flex flex-col gap-base">
                                <label className="text-label-md font-label-md text-on-surface" htmlFor="password">Password</label>
                                <div className="relative">
                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-outline">lock</span>
                                    <input className="w-full pl-10 pr-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT text-body-md font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors" id="password" name="password" placeholder="••••••••" required={true} type="password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading} />
                                </div>
                            </div>
                            <div className="flex flex-col gap-base">
                                <label className="text-label-md font-label-md text-on-surface" htmlFor="captcha">Security CAPTCHA</label>
                                <div className="flex gap-4">
                                    <div className="bg-surface-container-highest px-4 py-2 rounded-DEFAULT flex items-center justify-center font-mono font-bold tracking-widest text-lg select-none line-through text-on-surface w-32 border border-outline-variant border-dashed">
                                        Q8x2P
                                    </div>
                                    <input className="flex-1 px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT text-body-md font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors" id="captcha" name="captcha" placeholder="Enter CAPTCHA" required={true} type="text" value={captcha} onChange={(e) => setCaptcha(e.target.value)} disabled={isLoading} />
                                </div>
                            </div>
                            <button className="w-full bg-primary hover:bg-primary/90 text-on-primary py-2.5 rounded-DEFAULT font-label-lg font-bold flex items-center justify-center gap-2 transition-colors mt-2" disabled={isLoading} type="submit">
                                {isLoading ? (
                                    <span className="material-symbols-outlined animate-spin">progress_activity</span>
                                ) : (
                                    <>
                                        <span className="material-symbols-outlined">login</span>
                                        Secure Login
                                    </>
                                )}
                            </button>
                        </form>
                    </div>
                    <div className="hidden md:flex w-1/2 bg-primary flex-col items-center justify-center p-12 text-center text-on-primary relative overflow-hidden">
                        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white to-transparent" />
                        <span className="material-symbols-outlined text-[100px] mb-6 relative z-10 font-light">admin_panel_settings</span>
                        <h3 className="font-headline-lg text-3xl mb-4 relative z-10 font-bold tracking-tight">National Crime Records Bureau</h3>
                        <p className="text-lg opacity-90 relative z-10 font-body-lg">
                            Advanced Network Tracking and Relationship Analysis Platform
                        </p>
                        <div className="mt-auto relative z-10 bg-error/20 text-white border border-error/50 px-6 py-4 rounded backdrop-blur-sm shadow-sm flex flex-col gap-2">
                            <span className="text-label-md font-label-md font-bold uppercase tracking-wide">Restricted Access</span>
                            <span className="text-body-sm font-body-sm opacity-90 leading-relaxed text-left">
                                Unauthorized access is strictly prohibited and punishable under the Information Technology Act. This portal is for authorized NCRB personnel only.
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </PageTransition>
    );
};

export default Login;
