<script lang="ts">
	export let title: string = '';
	export let showBack: boolean = false;
	
	import { goto } from '$app/navigation';
	
	function goBack() {
		history.length > 1 ? history.back() : goto('/');
	}
</script>

<header class="header">
	{#if showBack}
		<button class="back-btn" on:click={goBack}>
			<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
			</svg>
		</button>
	{/if}
	<h1 class="header-title">{title}</h1>
	<div class="header-spacer"></div>
</header>

<style>
	.header {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem 1.5rem;
		background-color: var(--bg-primary);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		position: sticky;
		top: 0;
		z-index: 50;
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
	}
	
	.back-btn {
		background: transparent;
		border: none;
		color: var(--text-primary);
		cursor: pointer;
		padding: 0.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 0.5rem;
		transition: background-color 0.2s;
	}
	
	.back-btn:hover {
		background-color: rgba(255, 255, 255, 0.05);
	}
	
	.header-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary);
		flex: 1;
	}
	
	.header-spacer {
		width: 36px; /* Match back button width */
	}
	
	@media (max-width: 640px) {
		.header {
			padding: 1rem;
		}
		
		.header-title {
			font-size: 1.25rem;
		}
	}
</style>

