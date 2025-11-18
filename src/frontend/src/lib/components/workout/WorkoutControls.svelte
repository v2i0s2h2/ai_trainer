<script lang="ts">
	import { workoutStore } from '$lib/stores/workout';
	import { goto } from '$app/navigation';
	
	export let exerciseName: string = '';
	
	$: isActive = $workoutStore.isActive;
	$: duration = $workoutStore.duration;
	$: reps = $workoutStore.currentFrame?.reps || 0;
	
	// Weight and sets/reps tracking
	let weightLbs: number | null = null;
	let setsCompleted = 2;
	let repsPerSet = 15;
	let showWeightInput = false;
	
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
				calories_burned: 0, // Not used
				weight_lbs: weightLbs,
				sets_completed: setsCompleted,
				reps_per_set: repsPerSet
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
			{#if weightLbs !== null}
				<div class="info-item">
					<span class="info-icon">⚖️</span>
					<span class="info-value">{weightLbs} lbs</span>
				</div>
			{/if}
		</div>
		<div class="sets-reps-info">
			<span class="sets-reps-text">{setsCompleted} sets × {repsPerSet} reps</span>
		</div>
	</div>
	
	<div class="button-group">
		<button 
			class="control-btn weight-btn" 
			on:click={() => showWeightInput = !showWeightInput}
			title="Set weight"
		>
			<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"></path>
			</svg>
			<span>{weightLbs !== null ? `${weightLbs} lbs` : 'Set Weight'}</span>
		</button>
		<button class="control-btn exit-btn" on:click={handleExit}>
			<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
			</svg>
			<span>End Workout</span>
		</button>
	</div>
</div>

{#if showWeightInput}
	<div class="weight-input-overlay" on:click={() => showWeightInput = false}>
		<div class="weight-input-card" on:click|stopPropagation>
			<h3>Set Workout Details</h3>
			<div class="input-group">
				<label for="weight-input">Weight (lbs)</label>
				<input 
					id="weight-input"
					type="number" 
					min="0" 
					step="0.5" 
					placeholder="e.g., 5"
					bind:value={weightLbs}
				/>
			</div>
			<div class="input-group">
				<label for="sets-input">Sets (2-3)</label>
				<input 
					id="sets-input"
					type="number" 
					min="2" 
					max="3" 
					bind:value={setsCompleted}
				/>
			</div>
			<div class="input-group">
				<label for="reps-input">Reps per Set (15-20)</label>
				<input 
					id="reps-input"
					type="number" 
					min="15" 
					max="20" 
					bind:value={repsPerSet}
				/>
			</div>
			<button class="save-btn" on:click={() => showWeightInput = false}>
				Done
			</button>
		</div>
	</div>
{/if}

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
	
	.sets-reps-info {
		margin-top: 0.25rem;
	}
	
	.sets-reps-text {
		font-size: 0.75rem;
		color: var(--text-secondary);
		opacity: 0.8;
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
	
	.weight-btn {
		background: rgba(59, 130, 246, 0.2);
		color: #3B82F6;
		border: 1px solid rgba(59, 130, 246, 0.3);
	}
	
	.weight-btn:hover {
		background: rgba(59, 130, 246, 0.3);
		transform: translateY(-1px);
	}
	
	.weight-input-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.7);
		backdrop-filter: blur(4px);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
		padding: 1rem;
	}
	
	.weight-input-card {
		background: var(--bg-card);
		border-radius: 1rem;
		padding: 2rem;
		max-width: 400px;
		width: 100%;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.weight-input-card h3 {
		font-size: 1.25rem;
		font-weight: 700;
		margin-bottom: 1.5rem;
		color: var(--text-primary);
	}
	
	.input-group {
		margin-bottom: 1.25rem;
	}
	
	.input-group label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
	}
	
	.input-group input {
		width: 100%;
		padding: 0.75rem;
		background: var(--bg-primary);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: var(--text-primary);
		font-size: 1rem;
	}
	
	.input-group input:focus {
		outline: none;
		border-color: var(--primary);
	}
	
	.save-btn {
		width: 100%;
		padding: 0.75rem;
		background: var(--primary);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		margin-top: 0.5rem;
	}
	
	.save-btn:hover {
		background: var(--primary-hover, #ff6b35);
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

