import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition';

const Login = () => {
    const navigate = useNavigate();
    const [officerId, setOfficerId] = useState('');
    const [password, setPassword] = useState('');
    const [captcha, setCaptcha] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        
        if (!officerId || !password || !captcha) {
            setError('Please fill out all required fields.');
            return;
        }

        // Mock flow: Accepting any CAPTCHA for ease of testing
        if (captcha.length < 3) {
            setError('Please enter a valid CAPTCHA code.');
            return;
        }

        setIsLoading(true);
        setTimeout(() => {
            if (officerId === 'admin' && password === 'admin') {
                navigate('/dashboard');
            } else if (officerId === 'admin') {
                setError('Incorrect password.');
                setIsLoading(false);
            } else {
                navigate('/dashboard'); // accept anything for the mock
            }
        }, 1000);
    };

    return (
        
        <PageTransition>
      <div className="bg-surface text-on-surface min-h-screen flex flex-col font-body-md antialiased selection:bg-saffron-accent selection:text-white overflow-hidden">
            

{/*  Top Navigation Bar (Transactional/Login State: Nav suppressed, Brand anchored)  */}

<header className="docked full-width top-0 border-b border-outline-variant flat no shadows bg-deep-navy">

<div className="flex justify-between items-center w-full px-margin-mobile md:px-margin-desktop h-16 max-w-container-max mx-auto">

<div className="flex items-center gap-4">

{/*  National Emblem Placeholder  */}

<div className="h-10 w-10 bg-surface-container-high rounded-full overflow-hidden border border-outline-variant flex items-center justify-center bg-white">

<img alt="National Emblem" className="h-8 w-8 object-contain opacity-80 mix-blend-multiply" data-alt="A highly detailed, professional vector illustration of the State Emblem of India (Lion Capital of Ashoka). The emblem is rendered in a formal, high-contrast style suitable for a government portal, presented on a stark white background. The rendering uses crisp, clean lines and subtle shading to convey authority, institutional reliability, and minimalist elegance, typical of modern digital governance aesthetics." src="https://lh3.googleusercontent.com/aida-public/AB6AXuCvtmALfrOAuuVds2Muhcg-81HijQHr7Y5b-NOO0vZoLVbtBfklchHOMNcy9OQNe6Z6aSVinD52usfSxQ6n2FLvGsrWVhFKrT8XCM95jGxv3tIr-Ice1PvQVy9U8Obrgk4GENBQmfERNOfC9YhgZ5d7Am66GU7VUZrbDDDFLwzaKzN2J1t5dJilNy_H6i45A3XlINbIzuRAyISxa4-ZXMBESzrwow2cHp3EDDwUG3TA8366oyeLolLOOA" />

</div>

{/*  Brand Title  */}

<h1 className="text-title-lg font-title-lg md:text-headline-md md:font-headline-md font-bold text-on-primary">National Crime Records Portal</h1>

</div>

{/*  Language Switcher (Trailing Secondary Action)  */}

<div className="hidden md:flex items-center text-on-primary opacity-80 hover:opacity-100 transition-opacity">

<span className="text-label-md font-label-md cursor-pointer hover:text-saffron-accent transition-colors">हिन्दी/English</span>

</div>

</div>

</header>

{/*  Main Content Area  */}

<main className="flex-grow flex items-center justify-center p-margin-mobile md:p-margin-desktop bg-white relative overflow-hidden">

{/*  Background Subtle Pattern (CSS)  */}

<div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: "radial-gradient(circle at 2px 2px, #0B2447 1px, transparent 0)", backgroundSize: "32px 32px" }}></div>

{/*  Login Container  */}

<div className="w-full max-w-md bg-surface-container-lowest border border-outline-variant rounded-lg relative z-10 shadow-sm overflow-hidden flex flex-col transition-all duration-300 hover:shadow-[0px_4px_12px_rgba(11,36,71,0.08)]">

{/*  Top Categorization Border  */}

<div className="h-1 w-full bg-saffron-accent"></div>

<div className="p-8 flex flex-col gap-stack-lg">

{/*  Header  */}

<div className="flex flex-col items-center text-center gap-stack-sm">

<div className="h-12 w-12 rounded-full flex items-center justify-center mb-2 bg-deep-navy">

<span className="material-symbols-outlined text-on-primary text-[28px]" data-icon="admin_panel_settings">admin_panel_settings</span>

</div>

<h2 className="font-headline-md text-primary text-headline-lg">Secure Government Login</h2>

<p className="text-body-md font-body-md text-on-surface-variant">Enter your official credentials to access the portal.</p>

</div>

{/*  Form  */}

{error && (
        <div className="bg-error-container text-on-error-container px-4 py-3 rounded text-sm font-bold flex items-center gap-2 mb-2 border border-error/20">
            <span className="material-symbols-outlined text-error">error</span>
            {error}
        </div>
    )}
    <form onSubmit={handleLogin} className="flex flex-col gap-stack-md">

{/*  Officer ID Input  */}

<div className="flex flex-col gap-base">

<label className="text-label-md font-label-md text-on-surface" htmlFor="officer-id">Officer ID / Username</label>

<div className="relative">

<span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-outline">badge</span>

<input className="w-full pl-10 pr-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT text-body-md font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors" id="officer-id" name="officer-id" placeholder="e.g. NCRB-2024-X89" required={true} type="text" value={officerId} onChange={(e) => setOfficerId(e.target.value)} disabled={isLoading} />

</div>

</div>

{/*  Password Input  */}

<div className="flex flex-col gap-base">

<label className="text-label-md font-label-md text-on-surface" htmlFor="password">Password</label>

<div className="relative">

<span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-outline">lock</span>

<input className="w-full pl-10 pr-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT text-body-md font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors" id="password" name="password" placeholder="••••••••" required={true} type="password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading} />

<button className="absolute right-3 top-1/2 -translate-y-1/2 text-outline hover:text-primary transition-colors focus:outline-none" type="button">

<span className="material-symbols-outlined" data-icon="visibility">visibility</span>

</button>

</div>

</div>

{/*  CAPTCHA Section  */}

<div className="flex flex-col gap-base mt-2">

<label className="text-label-md font-label-md text-on-surface">Security Challenge</label>

<div className="flex gap-4 items-center">

{/*  CAPTCHA Image Placeholder  */}

<div className="flex-grow h-12 bg-surface-container flex items-center justify-center border border-outline-variant rounded-DEFAULT overflow-hidden relative">

<img alt="CAPTCHA" className="h-full w-full object-cover opacity-80" data-alt="A generic, heavily distorted alphanumeric CAPTCHA image reading 'W8KX9Z' on a noisy, grainy gray background with intersecting strike-through lines. Designed to represent a high-security visual challenge in a minimalist, light-mode institutional UI context." src="https://lh3.googleusercontent.com/aida-public/AB6AXuDp3Y0NpLhmqq5fqUtuoSrcqDw08OYbSFPP3aIwWZBQC7ORVIRKiCeb6sJ6ip3KtyT4sMWIAiea8uzXaRAifOHfTbsPuuq1xi8gMcUFhfgPbFupE86BvebmV4tTtM0i09t55Qu4MKTA-U1PYVv0HmOnqOYtsN-9J29qb-rH_xO6tGTozx1sM_gcAkgrKQvv4nviViDoVgOSjCbrblUJDD3w-LPgwAO7Pae6Q8lUT-dqSM1k8PI5o23f1g" />

{/*  Overlay to ensure text isn't confused with real image text in demo  */}

<div className="absolute inset-0 flex items-center justify-center pointer-events-none mix-blend-difference text-white opacity-20 font-mono tracking-[0.5em]">CAPTCHA</div>

</div>

<button aria-label="Refresh CAPTCHA" className="h-12 w-12 bg-surface-container-high border border-outline-variant rounded-DEFAULT flex items-center justify-center text-on-surface-variant hover:bg-surface-container-highest hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1" type="button">

<span className="material-symbols-outlined" data-icon="refresh">refresh</span>

</button>

</div>

<input className="w-full px-4 py-2 mt-2 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT text-body-md font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors" id="captcha-input" name="captcha" placeholder="Enter code shown above (7G2X9)" required={true} type="text" value={captcha} onChange={(e) => setCaptcha(e.target.value)} disabled={isLoading} />

</div>

{/*  Actions  */}

<div className="flex items-center justify-between mt-2">

<div className="flex items-center gap-2">

<input className="w-4 h-4 text-primary bg-surface-container-lowest border-outline-variant rounded focus:ring-primary focus:ring-offset-surface" id="remember" type="checkbox" />

<label className="text-label-sm font-label-sm text-on-surface-variant cursor-pointer select-none" htmlFor="remember">Remember Device</label>

</div>

<a className="text-label-sm font-label-sm text-primary hover:underline underline-offset-2" href="#">Forgot Password?</a>

</div>

{/*  Login Button  */}

<button className="w-full mt-4 bg-saffron-accent text-on-primary py-3 px-4 rounded-DEFAULT text-label-md font-label-md font-bold uppercase tracking-wider hover:bg-[#e68a2e] transition-colors focus:outline-none focus:ring-2 focus:ring-saffron-accent focus:ring-offset-2 shadow-sm flex justify-center items-center gap-2" type="submit">

<span className="">Login</span>

<span className="material-symbols-outlined text-[18px]" data-icon="arrow_forward">arrow_forward</span>

</button>

</form>

{/*  Security Badge  */}

<div className="flex items-center justify-center gap-2 pt-4 border-t border-surface-container-high text-on-surface-variant">

<span className="material-symbols-outlined text-india-green text-[16px]" data-icon="verified_user">verified_user</span>

<span className="text-label-sm font-label-sm">256-bit SSL Encrypted Connection</span>

</div>

</div>

</div>

</main>

{/*  Institutional Footer  */}

<footer className="bg-surface-container-highest docked full-width bottom-0 border-t border-outline-variant py-6 px-margin-mobile md:px-margin-desktop w-full">

<div className="max-w-container-max mx-auto flex flex-col items-center text-center gap-stack-sm">

<div className="flex items-center gap-2 text-error mb-2">

<span className="material-symbols-outlined text-[18px]" data-icon="warning">warning</span>

<span className="text-label-md font-label-md font-bold uppercase tracking-wide">Restricted Access</span>

</div>

<p className="text-label-sm font-label-sm text-on-surface-variant max-w-3xl leading-relaxed">

                Unauthorized access is strictly prohibited and punishable under the Information Technology Act. This portal is for authorized NCRB personnel only.

            </p>

<p className="text-label-sm font-label-sm text-outline mt-4">© 2024 National Crime Records Portal. All Rights Reserved. Govt of India.</p>

</div>

</footer>






        </div>
    </PageTransition>
  );
};

export default Login;
