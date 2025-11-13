<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { workoutStore } from '$lib/stores/workout';
	import LiveVideoFeed from '$lib/components/workout/LiveVideoFeed.svelte';
	import RepCounter from '$lib/components/workout/RepCounter.svelte';
	import WorkoutControls from '$lib/components/workout/WorkoutControls.svelte';
	
	$: exercise = $page.params.exercise;
	$: error = $workoutStore.error;
	
	let exerciseName = '';
	let exerciseData: any = null;
	let loading = true;
	let cameras: any[] = [];
	let selectedCamera = "auto"; // "auto" means auto-detect external webcam
	
	onMount(async () => {
		try {
			// Fetch exercise details
			const res = await fetch(`/api/exercises/${exercise}`);
			if (res.ok) {
				exerciseData = await res.json();
				exerciseName = exerciseData.name;
			} else {
				exerciseName = exercise.charAt(0).toUpperCase() + exercise.slice(1);
			}
			
			// Fetch available cameras
			const camRes = await fetch('/api/cameras');
			if (camRes.ok) {
				const camData = await camRes.json();
				cameras = camData.cameras || [];
				console.log('Available cameras:', cameras);
			}
		} catch (err) {
			console.error('Failed to load exercise:', err);
			exerciseName = exercise.charAt(0).toUpperCase() + exercise.slice(1);
		}
		
		// Connect to WebSocket with camera selection
		setTimeout(() => {
			workoutStore.connect(exercise, selectedCamera);
			loading = false;
		}, 500);
	});
	
	function changeCamera(cameraId: string) {
		selectedCamera = cameraId;
		workoutStore.disconnect();
		setTimeout(() => {
			workoutStore.connect(exercise, selectedCamera);
		}, 300);
	}
	
	onDestroy(() => {
		workoutStore.disconnect();
	});
</script>

<svelte:head>
	<title>{exerciseName} Workout - AI Trainer</title>
</svelte:head>

<div class="workout-page">
	{#if error}
		<div class="error-banner">
			<div class="error-content">
				<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
				</svg>
				<span>{error}</span>
			</div>
			<button class="retry-btn" on:click={() => workoutStore.connect(exercise)}>
				Retry
			</button>
		</div>
	{/if}
	
	{#if exerciseData}
		<div class="exercise-info-banner">
			<div class="info-content">
				<div class="info-section">
					<h3>{exerciseData.name}</h3>
					{#if exerciseData.target_muscles && exerciseData.target_muscles.length > 0}
						<div class="target-muscles">
							<span class="label">Target Muscles:</span>
							<span class="muscles">{exerciseData.target_muscles.join(', ')}</span>
						</div>
					{/if}
				</div>
				<div class="action-buttons">
					{#if cameras.length > 1}
						<div class="camera-selector">
							<label for="camera-select">📹 Camera:</label>
							<select 
								id="camera-select"
								bind:value={selectedCamera}
								on:change={() => changeCamera(selectedCamera)}
								class="camera-select"
							>
								<option value="auto">Auto (External Webcam)</option>
								{#each cameras as cam}
									<option value={cam.index.toString()}>
										Camera {cam.index} {cam.index === 0 ? '(Laptop)' : '(External)'}
									</option>
								{/each}
							</select>
						</div>
					{/if}
					{#if exerciseData.youtube_link}
						<a 
							href={exerciseData.youtube_link} 
							target="_blank" 
							rel="noopener noreferrer"
							class="youtube-link-btn"
						>
							<svg fill="currentColor" viewBox="0 0 24 24" width="20" height="20">
								<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
							</svg>
							Watch Tutorial
						</a>
					{/if}
				</div>
			</div>
		</div>
	{/if}
	
	<div class="video-section">
		<div class="video-wrapper">
			<LiveVideoFeed />
			<RepCounter />
		</div>
	</div>
	
	<WorkoutControls {exerciseName} />
</div>

<style>
	.workout-page {
		min-height: 100vh;
		background-color: var(--bg-primary);
		padding: 0;
		padding-bottom: 120px; /* Space for controls */
	}
	
	.error-banner {
		background: rgba(239, 68, 68, 0.2);
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: 0;
		padding: 1rem 1.5rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}
	
	.error-content {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: #EF4444;
		flex: 1;
	}
	
	.error-content svg {
		flex-shrink: 0;
	}
	
	.error-content span {
		font-size: 0.875rem;
		font-weight: 500;
	}
	
	.retry-btn {
		background: rgba(239, 68, 68, 0.2);
		color: #EF4444;
		border: 1px solid rgba(239, 68, 68, 0.3);
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.retry-btn:hover {
		background: rgba(239, 68, 68, 0.3);
	}
	
	.exercise-info-banner {
		background: var(--bg-card);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding: 1rem 1.5rem;
	}
	
	.info-content {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
	}
	
	.action-buttons {
		display: flex;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
	}
	
	.camera-selector {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	
	.camera-selector label {
		font-size: 0.875rem;
		color: var(--text-secondary);
		font-weight: 500;
	}
	
	.camera-select {
		padding: 0.5rem 0.75rem;
		background-color: var(--bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: var(--text-primary);
		font-size: 0.875rem;
		cursor: pointer;
		transition: border-color 0.2s;
	}
	
	.camera-select:hover {
		border-color: rgba(255, 255, 255, 0.2);
	}
	
	.camera-select:focus {
		outline: none;
		border-color: var(--primary);
	}
	
	.info-section h3 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: var(--text-primary);
	}
	
	.target-muscles {
		font-size: 0.875rem;
		color: var(--text-secondary);
		display: flex;
		gap: 0.5rem;
		align-items: center;
	}
	
	.target-muscles .label {
		font-weight: 500;
		opacity: 0.8;
	}
	
	.target-muscles .muscles {
		opacity: 0.9;
	}
	
	.youtube-link-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: #ff0000;
		color: white;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		text-decoration: none;
		transition: background-color 0.2s, transform 0.2s;
		white-space: nowrap;
	}
	
	.youtube-link-btn:hover {
		background-color: #cc0000;
		transform: scale(1.05);
	}
	
	.youtube-link-btn svg {
		flex-shrink: 0;
	}
	
	.video-section {
		padding: 1rem;
		max-width: 1200px;
		margin: 0 auto;
	}
	
	.video-wrapper {
		position: relative;
		width: 100%;
		max-width: 900px;
		margin: 0 auto;
	}
	
	@media (max-width: 640px) {
		.video-section {
			padding: 0.5rem;
		}
		
		.workout-page {
			padding-bottom: 140px;
		}
	}
</style>

