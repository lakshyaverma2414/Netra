import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface Officer {
    officerId: string;
    name: string;
    role: string;
}

interface AuthContextType {
    officer: Officer | null;
    token: string | null;
    login: (token: string, officer: Officer) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [officer, setOfficer] = useState<Officer | null>(() => {
        const saved = localStorage.getItem('officer');
        return saved ? JSON.parse(saved) : null;
    });
    
    const [token, setToken] = useState<string | null>(() => {
        return localStorage.getItem('token');
    });

    const login = (newToken: string, newOfficer: Officer) => {
        setToken(newToken);
        setOfficer(newOfficer);
        localStorage.setItem('token', newToken);
        localStorage.setItem('officer', JSON.stringify(newOfficer));
    };

    const logout = () => {
        setToken(null);
        setOfficer(null);
        localStorage.removeItem('token');
        localStorage.removeItem('officer');
    };

    return (
        <AuthContext.Provider value={{ officer, token, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
