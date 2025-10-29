<script lang="ts">
	export let value: number = 0; // 0-100
	export let showLabel: boolean = true;
	export let color: string = 'var(--primary)';
	export let animated: boolean = true;
	
	$: clampedValue = Math.max(0, Math.min(100, value));
</script>

<div class="progress-container">
	<div class="progress-bar">
		<div 
			class="progress-fill" 
			class:animated={animated}
			style="width: {clampedValue}%; background: {color}"
		></div>
	</div>
	{#if showLabel}
		<span class="progress-label">{Math.round(clampedValue)}%</span>
	{/if}
</div>

<style>
	.progress-container {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		width: 100%;
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
		border-radius: 999px;
		transition: width 0.2s ease;
	}
	
	.progress-fill.animated {
		transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	.progress-label {
		font-size: 0.875rem;
		font-weight: 700;
		color: var(--text-primary);
		min-width: 45px;
		text-align: right;
	}
</style>

