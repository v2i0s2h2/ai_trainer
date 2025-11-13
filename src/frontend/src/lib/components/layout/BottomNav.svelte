<script lang="ts">
	import { page } from '$app/stores';
	
	const navItems = [
		{ name: 'Home', path: '/', icon: 'home' },
		{ name: 'Exercises', path: '/exercises', icon: 'dumbbell' },
		{ name: 'Diet', path: '/diet', icon: 'apple' },
		{ name: 'Progress', path: '/progress', icon: 'chart' },
		{ name: 'Profile', path: '/profile', icon: 'user' }
	];
	
	$: currentPath = $page.url.pathname;
	
	function isActive(path: string): boolean {
		if (path === '/') {
			return currentPath === '/';
		}
		return currentPath.startsWith(path);
	}
</script>

<nav class="bottom-nav">
	<div class="nav-container">
		{#each navItems as item}
			<a 
				href={item.path} 
				class="nav-item"
				class:active={isActive(item.path)}
			>
				<div class="icon-wrapper">
					{#if item.icon === 'home'}
						<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
						</svg>
					{:else if item.icon === 'dumbbell'}
						<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"></path>
						</svg>
					{:else if item.icon === 'chart'}
						<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
						</svg>
					{:else if item.icon === 'apple'}
						<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
						</svg>
					{:else if item.icon === 'user'}
						<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
						</svg>
					{/if}
				</div>
				<span class="nav-text">{item.name}</span>
			</a>
		{/each}
	</div>
</nav>

<style>
	.bottom-nav {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		background-color: var(--bg-card);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		padding: 0.5rem 0;
		padding-bottom: max(0.5rem, env(safe-area-inset-bottom));
		z-index: 100;
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
	}
	
	.nav-container {
		display: flex;
		justify-content: space-around;
		align-items: center;
		max-width: 600px;
		margin: 0 auto;
		padding: 0 1rem;
	}
	
	.nav-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
		padding: 0.5rem 1rem;
		color: var(--text-secondary);
		text-decoration: none;
		transition: all 0.2s;
		cursor: pointer;
		border-radius: 0.5rem;
		position: relative;
	}
	
	.nav-item:hover {
		background-color: rgba(255, 255, 255, 0.05);
	}
	
	.nav-item.active {
		color: var(--primary);
	}
	
	.nav-item.active .icon-wrapper {
		transform: scale(1.1);
	}
	
	.icon-wrapper {
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: transform 0.2s;
	}
	
	.icon {
		width: 100%;
		height: 100%;
		stroke-width: 2;
	}
	
	.nav-text {
		font-size: 0.75rem;
		font-weight: 500;
		white-space: nowrap;
	}
</style>

