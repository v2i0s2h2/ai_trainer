<script lang="ts">
	import { workoutStore } from '$lib/stores/workout';
	
	$: frame = $workoutStore.currentFrame;
	$: reps = frame?.reps || 0;
	$: progress = frame?.progress || 0;
	$: feedback = frame?.feedback || 'Get ready...';
</script>

<div class="rep-counter-overlay">
	<!-- Big Rep Count -->
	<div class="rep-display">
		<div class="rep-number">{reps}</div>
		<div class="rep-label">REPS</div>
	</div>
	
	<!-- Progress Bar -->
	<div class="progress-container">
		<div class="progress-bar">
			<div class="progress-fill" style="width: {progress * 100}%"></div>
		</div>
		<div class="progress-text">{Math.round(progress * 100)}%</div>
	</div>
	
	<!-- Feedback Message -->
	<div class="feedback-box" class:warning={feedback.includes('Keep') || feedback.includes('Adjust')}>
		<div class="feedback-text">{feedback}</div>
	</div>
	
	<!-- Angle Display (Optional) -->
	{#if frame?.angles}
		<div class="angles-display">
			{#if frame.angles.knee}
				<div class="angle-item">
					<span class="angle-label">Knee</span>
					<span class="angle-value">{Math.round(frame.angles.knee)}°</span>
				</div>
			{/if}
			{#if frame.angles.torso}
				<div class="angle-item">
					<span class="angle-label">Torso</span>
					<span class="angle-value">{Math.round(frame.angles.torso)}°</span>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.rep-counter-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		pointer-events: none;
		display: flex;
		flex-direction: column;
		padding: 1.5rem;
	}
	
	.rep-display {
		position: absolute;
		top: 1.5rem;
		right: 1.5rem;
		text-align: center;
		background: rgba(0, 0, 0, 0.7);
		backdrop-filter: blur(10px);
		border-radius: 1rem;
		padding: 1rem 1.5rem;
		border: 2px solid var(--primary);
	}
	
	.rep-number {
		font-size: 3rem;
		font-weight: 900;
		color: var(--primary);
		line-height: 1;
		text-shadow: 0 2px 10px rgba(59, 130, 246, 0.5);
	}
	
	.rep-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: white;
		margin-top: 0.25rem;
		letter-spacing: 2px;
	}
	
	.progress-container {
		position: absolute;
		bottom: 8rem;
		left: 1.5rem;
		right: 1.5rem;
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}
	
	.progress-bar {
		flex: 1;
		height: 12px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 999px;
		overflow: hidden;
		backdrop-filter: blur(10px);
	}
	
	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, var(--accent-green) 0%, var(--primary) 100%);
		transition: width 0.2s ease;
		border-radius: 999px;
	}
	
	.progress-text {
		font-size: 0.875rem;
		font-weight: 700;
		color: white;
		min-width: 45px;
		text-align: right;
		text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
	}
	
	.feedback-box {
		position: absolute;
		bottom: 5rem;
		left: 1.5rem;
		right: 1.5rem;
		background: rgba(16, 185, 129, 0.9);
		backdrop-filter: blur(10px);
		border-radius: 0.75rem;
		padding: 0.75rem 1rem;
		transition: background 0.3s;
	}
	
	.feedback-box.warning {
		background: rgba(249, 115, 22, 0.9);
	}
	
	.feedback-text {
		color: white;
		font-size: 0.875rem;
		font-weight: 600;
		text-align: center;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
	}
	
	.angles-display {
		position: absolute;
		top: 1.5rem;
		left: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	
	.angle-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: rgba(0, 0, 0, 0.7);
		backdrop-filter: blur(10px);
		border-radius: 0.5rem;
		padding: 0.5rem 0.75rem;
	}
	
	.angle-label {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.7);
		font-weight: 500;
	}
	
	.angle-value {
		font-size: 0.875rem;
		color: white;
		font-weight: 700;
	}
	
	@media (max-width: 640px) {
		.rep-number {
			font-size: 2.5rem;
		}
		
		.rep-display {
			padding: 0.75rem 1.25rem;
		}
		
		.feedback-box {
			bottom: 4rem;
		}
		
		.progress-container {
			bottom: 6.5rem;
		}
	}
</style>

