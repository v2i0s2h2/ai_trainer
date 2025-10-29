<script lang="ts">
	import { goto } from '$app/navigation';
	
	function handleClick() {
		goto('/exercises');
	}
</script>

<a href="/exercises" class="start-workout-btn" on:click={handleClick}>
	<div class="btn-content">
		<div class="btn-text-group">
			<span class="btn-label">Ready to train?</span>
			<span class="btn-title">Start Workout</span>
		</div>
		<div class="play-icon">
			<svg fill="currentColor" viewBox="0 0 24 24">
				<path d="M8 5v14l11-7z"></path>
			</svg>
		</div>
	</div>
</a>

<style>
	.start-workout-btn {
		display: block;
		background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
		border-radius: 1rem;
		padding: 1.5rem;
		margin-bottom: 2rem;
		text-decoration: none;
		color: white;
		box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);
		transition: transform 0.2s, box-shadow 0.2s;
		cursor: pointer;
	}
	
	.start-workout-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 15px 50px rgba(59, 130, 246, 0.4);
	}
	
	.btn-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	
	.btn-text-group {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	
	.btn-label {
		font-size: 0.875rem;
		opacity: 0.9;
	}
	
	.btn-title {
		font-size: 1.5rem;
		font-weight: 700;
	}
	
	.play-icon {
		width: 48px;
		height: 48px;
		background: rgba(255, 255, 255, 0.2);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		backdrop-filter: blur(10px);
	}
	
	.play-icon svg {
		width: 24px;
		height: 24px;
		margin-left: 2px;
	}
</style>

