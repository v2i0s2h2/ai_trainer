<script lang="ts">
	export let variant: 'default' | 'success' | 'warning' | 'error' | 'info' = 'default';
	export let size: 'sm' | 'md' = 'md';
	
	const variantColors: Record<string, string> = {
		default: 'var(--primary)',
		success: 'var(--accent-green)',
		warning: 'var(--accent-orange)',
		error: 'var(--error)',
		info: 'var(--accent-purple)'
	};
	
	$: bgColor = variantColors[variant] || variantColors.default;
</script>

<span class="badge badge-{size}" style="background-color: {bgColor}">
	<slot />
</span>

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		color: white;
		font-weight: 600;
		text-transform: capitalize;
		border-radius: 9999px;
	}
	
	.badge-sm {
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
	}
	
	.badge-md {
		padding: 0.25rem 0.75rem;
		font-size: 0.75rem;
	}
</style>

