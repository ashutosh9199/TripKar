export class AuthService {
    async createAccount({email, password, name}) {
        try {
            const response = await fetch('http://localhost:5000/api/users/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, name })
            });
            if (!response.ok) throw new Error('Registration failed');
            return await response.json();
        } catch (error) {
            console.log("Create Account Error", error);
        }
    }

    async login({email, password}) {
        try {
            const response = await fetch('http://localhost:5000/api/users/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            if (!response.ok) throw new Error('Login failed');
            const user = await response.json();
            localStorage.setItem('userSession', JSON.stringify(user));
            return user;
        } catch(error) {
            console.log("Login Error", error);
        }
    }

    async getCurrentUser() {
        try {
            const user = localStorage.getItem('userSession');
            return user ? JSON.parse(user) : null;
        } catch(error) {
            throw error;
        }
    }

    async logout() {
        try {
            localStorage.removeItem('userSession');
            return true;
        } catch (error) {
            throw error;
        }
    }
}

const authService = new AuthService();

export default authService;