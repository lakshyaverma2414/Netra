export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('token');
    
    const headers = new Headers(options.headers || {});
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token');
        localStorage.removeItem('officer');
        window.location.href = '/';
    }

    return response;
};
