import { writable } from 'svelte/store';

export interface UserStats {
	total_workouts: number;
	current_streak: number;
	days_active: number;
	total_reps: number;
	total_muscle_gain: number;
}

export interface UserPreferences {
	notifications_enabled: boolean;
	units: 'metric' | 'imperial';
	language: string;
}

export interface UserProfile {
	id: number;
	name: string;
	email: string | null;
	stats: UserStats;
	preferences: UserPreferences;
	created_at: string;
}

interface ProfileState {
	profile: UserProfile | null;
	loading: boolean;
	error: string | null;
}

const initialState: ProfileState = {
	profile: null,
	loading: false,
	error: null
};

function createProfileStore() {
	const { subscribe, set, update } = writable<ProfileState>(initialState);
	
	return {
		subscribe,
		
		async loadProfile() {
			update(state => ({ ...state, loading: true, error: null }));
			
			try {
				const res = await fetch('/api/user/profile');
				if (!res.ok) throw new Error('Failed to load profile');
				
				const profile = await res.json();
				update(state => ({ ...state, profile, loading: false }));
			} catch (err: any) {
				update(state => ({ ...state, error: err.message, loading: false }));
			}
		},
		
		async updateProfile(updates: {
			name?: string;
			email?: string;
			preferences?: Partial<UserPreferences>;
		}) {
			update(state => ({ ...state, loading: true, error: null }));
			
			try {
				const res = await fetch('/api/user/profile', {
					method: 'PUT',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(updates)
				});
				
				if (!res.ok) throw new Error('Failed to update profile');
				
				const updatedProfile = await res.json();
				update(state => ({
					...state,
					profile: updatedProfile,
					loading: false
				}));
			} catch (err: any) {
				update(state => ({ ...state, error: err.message, loading: false }));
			}
		},
		
		reset() {
			set(initialState);
		}
	};
}

export const profileStore = createProfileStore();


