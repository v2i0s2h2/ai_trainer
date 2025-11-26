import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import { browser } from '$app/environment';

export interface User {
	id: number;
	name: string;
	email: string;
}

export interface AuthState {
	isAuthenticated: boolean;
	user: User | null;
	token: string | null;
	loading: boolean;
	error: string | null;
}

const initialState: AuthState = {
	isAuthenticated: false,
	user: null,
	token: null,
	loading: false,
	error: null
};

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>(initialState);

	return {
		subscribe,

		async login(email: string, password: string) {
			update(state => ({ ...state, loading: true, error: null }));

			try {
				const res = await fetch('/api/auth/login', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ email, password })
				});

				const data = await res.json();

				if (!res.ok) {
					throw new Error(data.detail || 'Login failed');
				}

				// Save to local storage
				if (browser) {
					localStorage.setItem('token', data.access_token);
					localStorage.setItem('user', JSON.stringify(data.user));
				}

				update(state => ({
					...state,
					isAuthenticated: true,
					token: data.access_token,
					user: data.user,
					loading: false,
					error: null
				}));

				goto('/profile');
				return true;
			} catch (err: any) {
				update(state => ({
					...state,
					loading: false,
					error: err.message || 'An error occurred during login'
				}));
				return false;
			}
		},

		async register(name: string, email: string, password: string) {
			update(state => ({ ...state, loading: true, error: null }));

			try {
				const res = await fetch('/api/auth/register', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ name, email, password })
				});

				const data = await res.json();

				if (!res.ok) {
					throw new Error(data.detail || 'Registration failed');
				}

				// Save to local storage
				if (browser) {
					localStorage.setItem('token', data.access_token);
					localStorage.setItem('user', JSON.stringify(data.user));
				}

				update(state => ({
					...state,
					isAuthenticated: true,
					token: data.access_token,
					user: data.user,
					loading: false,
					error: null
				}));

				goto('/profile');
				return true;
			} catch (err: any) {
				update(state => ({
					...state,
					loading: false,
					error: err.message || 'An error occurred during registration'
				}));
				return false;
			}
		},

		logout() {
			if (browser) {
				localStorage.removeItem('token');
				localStorage.removeItem('user');
			}
			set(initialState);
			goto('/login');
		},

		init() {
			if (browser) {
				const token = localStorage.getItem('token');
				const userStr = localStorage.getItem('user');

				if (token && userStr) {
					try {
						const user = JSON.parse(userStr);
						set({
							isAuthenticated: true,
							token,
							user,
							loading: false,
							error: null
						});
					} catch (e) {
						// Invalid data
						this.logout();
					}
				}
			}
		}
	};
}

export const authStore = createAuthStore();
