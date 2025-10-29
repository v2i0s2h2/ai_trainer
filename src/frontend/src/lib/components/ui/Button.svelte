<script lang="ts">
	export let variant: 'primary' | 'secondary' | 'danger' | 'ghost' = 'primary';
	export let size: 'sm' | 'md' | 'lg' = 'md';
	export let fullWidth: boolean = false;
	export let disabled: boolean = false;
	
	$: classes = `
		btn btn-${variant} btn-${size}
		${fullWidth ? 'btn-full' : ''}
		${disabled ? 'btn-disabled' : ''}
	`;
</script>

<button class={classes} {disabled} {...$$restProps}>
	<slot />
</button>

<style>
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		border: none;
		border-radius: 0.75rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		text-decoration: none;
	}
	
	/* Variants */
	.btn-primary {
		background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
		color: white;
		box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
	}
	
	.btn-primary:hover:not(.btn-disabled) {
		background: linear-gradient(135deg, var(--primary-hover) 0%, var(--primary) 100%);
		box-shadow: 0 6px 30px rgba(59, 130, 246, 0.4);
		transform: translateY(-2px);
	}
	
	.btn-secondary {
		background-color: var(--bg-card);
		color: var(--text-primary);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.btn-secondary:hover:not(.btn-disabled) {
		background-color: var(--bg-card-hover);
		transform: translateY(-1px);
	}
	
	.btn-danger {
		background: rgba(239, 68, 68, 0.2);
		color: #EF4444;
		border: 1px solid rgba(239, 68, 68, 0.3);
	}
	
	.btn-danger:hover:not(.btn-disabled) {
		background: rgba(239, 68, 68, 0.3);
		transform: translateY(-1px);
	}
	
	.btn-ghost {
		background: transparent;
		color: var(--text-secondary);
	}
	
	.btn-ghost:hover:not(.btn-disabled) {
		background-color: rgba(255, 255, 255, 0.05);
		color: var(--text-primary);
	}
	
	/* Sizes */
	.btn-sm {
		padding: 0.5rem 1rem;
		font-size: 0.875rem;
	}
	
	.btn-md {
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
	}
	
	.btn-lg {
		padding: 1rem 2rem;
		font-size: 1.125rem;
	}
	
	.btn-full {
		width: 100%;
	}
	
	.btn-disabled {
		opacity: 0.5;
		cursor: not-allowed;
		pointer-events: none;
	}
</style>

