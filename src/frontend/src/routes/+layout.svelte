<script lang="ts">
	import '../app.css';
	import BottomNav from '$lib/components/layout/BottomNav.svelte';
	import { page } from '$app/stores';
	
	// Hide bottom nav on workout page
	$: hideNav = $page.url.pathname.startsWith('/workout/');
</script>

<div class="app-container">
	<main class="main-content">
		<slot />
	</main>
	
	{#if !hideNav}
		<BottomNav />
	{/if}
</div>

<style>
	.app-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background-color: var(--bg-primary);
	}
	
	.main-content {
		flex: 1;
		padding-bottom: 80px; /* Space for bottom nav */
	}
</style>

