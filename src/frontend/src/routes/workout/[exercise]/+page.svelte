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
	let loading = true;
	
	onMount(async () => {
		try {
			// Fetch exercise details
			const res = await fetch(`/api/exercises/${exercise}`);
			if (res.ok) {
				const data = await res.json();
				exerciseName = data.name;
			} else {
				exerciseName = exercise.charAt(0).toUpperCase() + exercise.slice(1);
			}
		} catch (err) {
			console.error('Failed to load exercise:', err);
			exerciseName = exercise.charAt(0).toUpperCase() + exercise.slice(1);
		}
		
		// Connect to WebSocket
		setTimeout(() => {
			workoutStore.connect(exercise);
			loading = false;
		}, 500);
	});
	
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

