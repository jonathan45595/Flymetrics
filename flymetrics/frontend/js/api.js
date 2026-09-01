const API_BASE = (window.location.protocol === 'file:')
  ? 'http://localhost:3000'
  : (window.location.origin || 'http://localhost:3000');

const BASE_URL = API_BASE + '/api/v1';

const API = {
    async login(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const res = await fetch(`${BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        if (!res.ok) {
            let errorMsg = 'Credenciales inválidas';
            try {
                const errData = await res.json();
                errorMsg = errData.message || errorMsg;
                if (errData.errors && errData.errors.length > 0) {
                    errorMsg = errData.errors.join(', ');
                }
            } catch (e) {}
            throw new Error(errorMsg);
        }
        return await res.json();
    },

    async register(name, email, password, role = 'cliente', phone = null) {
        const parts = (name || '').trim().split(/\s+/);
        let nombre = 'Cliente';
        let apellido_1 = '';

        if (parts.length === 1) {
            nombre = parts[0];
        } else if (parts.length === 2) {
            nombre = parts[0];
            apellido_1 = parts[1];
        } else if (parts.length >= 3) {
            const mid = Math.ceil(parts.length / 2);
            nombre = parts.slice(0, mid).join(' ');
            apellido_1 = parts.slice(mid).join(' ');
        }

        const payload = {
            email: email,
            contraseña: password,
            rol: role,
            nombre: nombre,
            apellido_1: apellido_1
        };
        if (phone) payload.telefono = phone;

        const res = await fetch(`${BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) {
            let errorMsg = 'Error al registrar usuario';
            try {
                const errData = await res.json();
                errorMsg = errData.message || errorMsg;
                if (errData.errors && errData.errors.length > 0) {
                    errorMsg = errData.errors.join(', ');
                }
            } catch (e) {}
            throw new Error(errorMsg);
        }
        return await res.json();
    },

    async loginGoogle(token) {
        const res = await fetch(`${BASE_URL}/auth/google`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
        });
        
        if (!res.ok) {
            let errorMsg = 'Error al iniciar sesión con Google';
            try {
                const errData = await res.json();
                errorMsg = errData.message || errorMsg;
            } catch (e) {}
            throw new Error(errorMsg);
        }
        return await res.json();
    },

    async getMe(token) {
        const res = await fetch(`${BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Sesión expirada');
        return await res.json();
    },

    setToken(token) {
        if (token) {
            try { localStorage.setItem('fm_token', token); } catch(e) {}
            try { sessionStorage.setItem('fm_token', token); } catch(e) {}
        } else {
            try { localStorage.removeItem('fm_token'); } catch(e) {}
            try { sessionStorage.removeItem('fm_token'); } catch(e) {}
        }
    },

    getToken() {
        return localStorage.getItem('fm_token') || sessionStorage.getItem('fm_token');
    },

    logout() {
        try {
            localStorage.removeItem('fm_token');
            localStorage.removeItem('fm_user');
            localStorage.removeItem('fm_role');
        } catch(e) {}
        try { sessionStorage.clear(); } catch(e) {}
        window.location.href = 'index.html';
    }
};
