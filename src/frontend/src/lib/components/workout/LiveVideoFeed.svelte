<script lang="ts">
	import { workoutStore } from '$lib/stores/workout';
	
	$: frame = $workoutStore.currentFrame;
	$: isConnected = $workoutStore.isConnected;
</script>

<div class="video-container">
	{#if !isConnected}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Connecting to camera...</p>
		</div>
	{:else if frame?.image}
		<img 
			src={frame.image} 
			alt="Workout feed" 
			class="video-frame"
		/>
	{:else}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Initializing pose detection...</p>
		</div>
	{/if}
</div>

<style>
	.video-container {
		position: relative;
		width: 100%;
		aspect-ratio: 16 / 9;
		background-color: #000;
		border-radius: 1rem;
		overflow: hidden;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.video-frame {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		color: white;
	}
	
	.loading-state p {
		font-size: 1rem;
		opacity: 0.8;
	}
	
	.spinner {
		width: 48px;
		height: 48px;
		border: 4px solid rgba(255, 255, 255, 0.1);
		border-top-color: var(--primary);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>

