<script lang="ts">
	export let hover: boolean = false;
	export let padding: 'sm' | 'md' | 'lg' = 'md';
	
	$: classes = `
		card card-${padding}
		${hover ? 'card-hover' : ''}
	`;
</script>

<div class={classes} {...$$restProps}>
	<slot />
</div>

<style>
	.card {
		background-color: var(--bg-card);
		border-radius: 1rem;
		transition: all 0.2s;
	}
	
	.card-sm {
		padding: 0.75rem;
	}
	
	.card-md {
		padding: 1.25rem;
	}
	
	.card-lg {
		padding: 1.5rem;
	}
	
	.card-hover:hover {
		transform: translateY(-2px);
		background-color: var(--bg-card-hover);
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
	}
</style>

