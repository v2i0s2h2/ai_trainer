import { writable } from 'svelte/store';
import { speak, initSpeech } from '$lib/utils/speech';

export interface WorkoutFrame {
	image: string;
	reps: number;
	feedback: string;
	angles: {
		knee?: number;
		torso?: number;
		hip?: number;
	};
	progress: number;
}

export interface WorkoutState {
	isConnected: boolean;
	isActive: boolean;
	currentFrame: WorkoutFrame | null;
	error: string | null;
	exercise: string;
	startTime: number | null;
	duration: number; // seconds
}

const initialState: WorkoutState = {
	isConnected: false,
	isActive: false,
	currentFrame: null,
	error: null,
	exercise: '',
	startTime: null,
	duration: 0
};

function createWorkoutStore() {
	const { subscribe, set, update } = writable<WorkoutState>(initialState);
	
	let ws: WebSocket | null = null;
	let durationInterval: number | null = null;
	let lastFeedback = '';
	let lastReps = 0;
	
	// Initialize speech on first use
	initSpeech();
	
	return {
		subscribe,
		
		connect: (exercise: string, cameraDevice: string = "auto") => {
			if (ws) {
				ws.close();
			}
			
			update(state => ({
				...state,
				exercise,
				error: null,
				isConnected: false
			}));
			
			// WebSocket URL with camera device parameter
			const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/workout?exercise=${exercise}&camera=${cameraDevice}`;
			
			console.log('[Workout Store] Connecting to:', wsUrl, 'with camera:', cameraDevice);
			
			ws = new WebSocket(wsUrl);
			
			ws.onopen = () => {
				console.log('[Workout Store] WebSocket connected');
				update(state => ({
					...state,
					isConnected: true,
					isActive: true,
					startTime: Date.now(),
					error: null
				}));
				
				// Start duration timer
				durationInterval = window.setInterval(() => {
					update(state => ({
						...state,
						duration: state.startTime ? Math.floor((Date.now() - state.startTime) / 1000) : 0
					}));
				}, 1000);
			};
			
			ws.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					console.log('[Workout Store] Message:', data.type);
					
					if (data.type === 'frame') {
						const reps = data.reps || 0;
						const feedback = data.feedback || '';
						
						// Voice feedback for rep completion
						if (reps > lastReps) {
							speak(`Rep ${reps} complete!`, 'high');
							lastReps = reps;
						}
						
						// Voice feedback for form corrections
						if (feedback && feedback !== lastFeedback && feedback !== 'Good form - keep going!') {
							// Only speak corrections, not the default good message
							if (feedback.includes('Chest up') || 
							    feedback.includes('knees') || 
							    feedback.includes('Adjust') ||
							    feedback.includes('Keep')) {
								speak(feedback, 'normal');
								lastFeedback = feedback;
							}
						}
						
						update(state => ({
							...state,
							currentFrame: {
								image: data.image,
								reps: reps,
								feedback: feedback,
								angles: data.angles || {},
								progress: data.progress || 0
							}
						}));
					} else if (data.type === 'error') {
						update(state => ({
							...state,
							error: data.message
						}));
					} else if (data.type === 'connected') {
						// Speak welcome message
						speak('Workout started. Begin when ready.', 'normal');
					}
				} catch (err) {
					console.error('[Workout Store] Parse error:', err);
				}
			};
			
			ws.onerror = (error) => {
				console.error('[Workout Store] WebSocket error:', error);
				update(state => ({
					...state,
					error: 'Connection error. Check if backend is running.',
					isConnected: false
				}));
			};
			
			ws.onclose = () => {
				console.log('[Workout Store] WebSocket closed');
				update(state => ({
					...state,
					isConnected: false,
					isActive: false
				}));
				
				if (durationInterval) {
					clearInterval(durationInterval);
					durationInterval = null;
				}
			};
		},
		
		disconnect: () => {
			if (ws) {
				ws.close();
				ws = null;
			}
			
			if (durationInterval) {
				clearInterval(durationInterval);
				durationInterval = null;
			}
			
			set(initialState);
		},
		
		reset: () => {
			set(initialState);
		}
	};
}

export const workoutStore = createWorkoutStore();

