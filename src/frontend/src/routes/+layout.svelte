<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import BottomNav from '$lib/components/layout/BottomNav.svelte';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth';

	// Hide bottom nav on workout page or auth pages
	$: hideNav = $page.url.pathname.startsWith('/workout/') ||
	             $page.url.pathname === '/login' ||
	             $page.url.pathname === '/signup';

	onMount(() => {
		authStore.init();
	});

	$: {
		// Route protection
		if (typeof window !== 'undefined') {
			const path = $page.url.pathname;
			const isAuthRoute = path === '/login' || path === '/signup';

			if (!$authStore.isAuthenticated && !isAuthRoute) {
				goto('/login');
			} else if ($authStore.isAuthenticated && isAuthRoute) {
				goto('/');
			}
		}
	}
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
