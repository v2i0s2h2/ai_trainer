<script lang="ts">
	import { workoutStore } from '$lib/stores/workout';
	import { goto } from '$app/navigation';
	
	export let exerciseName: string = '';
	
	$: isActive = $workoutStore.isActive;
	$: duration = $workoutStore.duration;
	$: reps = $workoutStore.currentFrame?.reps || 0;
	
	function formatTime(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}
	
	function handleExit() {
		if (confirm('Are you sure you want to end this workout?')) {
			// Save workout data
			saveWorkout();
			// Disconnect WebSocket
			workoutStore.disconnect();
			// Navigate back to exercises
			goto('/exercises');
		}
	}
	
	async function saveWorkout() {
		try {
			const workout = {
				exercise_id: $workoutStore.exercise,
				duration: $workoutStore.duration,
				reps_completed: reps,
				calories_burned: Math.round($workoutStore.duration * 0.15 * reps) // Rough estimate
			};
			
			const res = await fetch('/api/workouts', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(workout)
			});
			
			if (res.ok) {
				console.log('Workout saved successfully');
			}
		} catch (err) {
			console.error('Failed to save workout:', err);
		}
	}
</script>

<div class="controls-container">
	<div class="workout-info">
		<h2 class="exercise-name">{exerciseName}</h2>
		<div class="info-row">
			<div class="info-item">
				<span class="info-icon">⏱️</span>
				<span class="info-value">{formatTime(duration)}</span>
			</div>
			<div class="info-item">
				<span class="info-icon">🔥</span>
				<span class="info-value">{reps} reps</span>
			</div>
		</div>
	</div>
	
	<div class="button-group">
		<button class="control-btn exit-btn" on:click={handleExit}>
			<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
			</svg>
			<span>End Workout</span>
		</button>
	</div>
</div>

<style>
	.controls-container {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		background: var(--bg-card);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		padding: 1rem 1.5rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		z-index: 50;
	}
	
	.workout-info {
		flex: 1;
	}
	
	.exercise-name {
		font-size: 1.25rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}
	
	.info-row {
		display: flex;
		gap: 1.5rem;
	}
	
	.info-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		color: var(--text-secondary);
	}
	
	.info-icon {
		font-size: 1rem;
	}
	
	.info-value {
		font-weight: 600;
		color: var(--text-primary);
	}
	
	.button-group {
		display: flex;
		gap: 0.75rem;
	}
	
	.control-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.5rem;
		border-radius: 0.75rem;
		border: none;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.exit-btn {
		background: rgba(239, 68, 68, 0.2);
		color: #EF4444;
		border: 1px solid rgba(239, 68, 68, 0.3);
	}
	
	.exit-btn:hover {
		background: rgba(239, 68, 68, 0.3);
		transform: translateY(-1px);
	}
	
	@media (max-width: 640px) {
		.controls-container {
			flex-direction: column;
			align-items: stretch;
			padding: 1rem;
		}
		
		.button-group {
			width: 100%;
		}
		
		.control-btn {
			flex: 1;
			justify-content: center;
		}
	}
</style>

