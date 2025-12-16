import { writable } from 'svelte/store';
import { speak, initSpeech } from '$lib/utils/speech';
import { WS_BASE_URL } from '$lib/constants';

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

		connect: (exercise: string, cameraDevice: string = "client") => {
			if (ws) {
				ws.close();
			}

			update(state => ({
				...state,
				exercise,
				error: null,
				isConnected: false
			}));

			// WebSocket URL - connect to backend server, not frontend
			const wsUrl = `${WS_BASE_URL}/ws/workout?exercise=${exercise}&camera=${cameraDevice}`;

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
							// Expanded keyword list to cover more feedback types (calibration, stability, etc.)
							const importantKeywords = [
								'Chest', 'knees', 'Adjust', 'Keep', 'Don\'t', 'Stop', 'Lower', 'Raise', 'Hips', 'Back',
								'pelvis', 'roll', 'stable', 'Calibration', 'Calibrating', 'Complete', 'Hold', 'Lift', 'Ankle'
							];

							if (importantKeywords.some(keyword => feedback.includes(keyword))) {
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
		},

		sendFrame: (imageData: string) => {
			if (ws && ws.readyState === WebSocket.OPEN) {
				ws.send(JSON.stringify({
					type: 'frame',
					image: imageData
				}));
			}
		}
	};
}

export const workoutStore = createWorkoutStore();

