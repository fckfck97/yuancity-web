const AUTH_STORAGE_KEY = 'yuancity_auth';
const USER_STORAGE_KEY = 'yuancity_user';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const buildApiUrl = (path: string): string => {
    if (!path) {
        return API_BASE_URL;
    }
    if (path.startsWith('http://') || path.startsWith('https://')) {
        return path;
    }
    let apiPath = path;
    if (!path.startsWith('/api/')) {
        apiPath = path.startsWith('/') ? `/api${path}` : `/api/${path}`;
    }
    return `${API_BASE_URL}${apiPath}`;
};

export interface AuthData {
    access: string;
    refresh: string;
}

export interface UserData {
    username?: string;
    firstName?: string;
    lastName?: string;
    role?: string;
    subRole?: string;
    [key: string]: any;
}

export const loadAuth = (): AuthData | null => {
    if (typeof window === 'undefined') {
        return null;
    }
    try {
        const raw = localStorage.getItem(AUTH_STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (error) {
        return null;
    }
};

export const saveAuth = (data: AuthData): void => {
    if (typeof window === 'undefined') {
        return;
    }
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data));
};

export const clearAuth = (): void => {
    if (typeof window === 'undefined') {
        return;
    }
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
};

export const getAccessToken = (): string | null => {
    const auth = loadAuth();
    return auth && auth.access ? auth.access : null;
};

export const getRefreshToken = (): string | null => {
    const auth = loadAuth();
    return auth && auth.refresh ? auth.refresh : null;
};

export const loadUser = (): UserData | null => {
    if (typeof window === 'undefined') {
        return null;
    }
    try {
        const raw = localStorage.getItem(USER_STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (error) {
        return null;
    }
};

export const saveUser = (data: UserData): void => {
    if (typeof window === 'undefined') {
        return;
    }
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(data));
};

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const token = getAccessToken();
    const headers = new Headers(options.headers || {});
    const isFormData =
        typeof FormData !== 'undefined' && options.body instanceof FormData;

    if (isFormData) {
        // Let the browser set the correct multipart boundary.
        headers.delete('Content-Type');
    } else if (!headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }

    if (token) {
        headers.set('Authorization', `JWT ${token}`);
    }

    const res = await fetch(url, {
        ...options,
        headers,
    });

    if (res.status === 401) {
        // Here we could handle token refresh, but for now just clear and redirect
        // clearAuth();
    }

    return res;
};
