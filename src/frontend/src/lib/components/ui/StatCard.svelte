<script lang="ts">
	export let icon: string | null = null;
	export let value: string | number;
	export let label: string;
	export let color: string = 'var(--primary)';
</script>

<div class="stat-card">
	{#if icon}
		<div class="stat-icon" style="color: {color}">
			<slot name="icon">
				{@html icon}
			</slot>
		</div>
	{/if}
	<div class="stat-value">{value}</div>
	<div class="stat-label">{label}</div>
</div>

<style>
	.stat-card {
		background-color: var(--bg-card);
		border-radius: 1rem;
		padding: 1.25rem 0.75rem;
		text-align: center;
		transition: transform 0.2s;
	}
	
	.stat-card:hover {
		transform: translateY(-2px);
	}
	
	.stat-icon {
		width: 32px;
		height: 32px;
		margin: 0 auto 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.stat-value {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: 0.25rem;
		color: var(--text-primary);
	}
	
	.stat-label {
		font-size: 0.875rem;
		color: var(--text-secondary);
	}
</style>

