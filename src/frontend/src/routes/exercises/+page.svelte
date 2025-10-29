<script lang="ts">
	import { onMount } from 'svelte';
	import ExerciseGrid from '$lib/components/exercises/ExerciseGrid.svelte';
	
	let allExercises: any[] = [];
	let filteredExercises: any[] = [];
	let loading = true;
	let searchQuery = '';
	let selectedCategory: string | null = null;
	
	const categories = [
		{ id: null, name: 'All', icon: '🏋️' },
		{ id: 'legs', name: 'Legs', icon: '🦵' },
		{ id: 'chest', name: 'Chest', icon: '💪' },
		{ id: 'back', name: 'Back', icon: '🔙' },
		{ id: 'shoulders', name: 'Shoulders', icon: '🤲' },
		{ id: 'arms', name: 'Arms', icon: '💪' },
		{ id: 'core', name: 'Core', icon: '🔥' }
	];
	
	onMount(async () => {
		try {
			const res = await fetch('/api/exercises');
			if (res.ok) {
				allExercises = await res.json();
				filteredExercises = allExercises;
			}
		} catch (err) {
			console.error('Failed to load exercises:', err);
		} finally {
			loading = false;
		}
	});
	
	function filterExercises() {
		let filtered = allExercises;
		
		// Filter by category
		if (selectedCategory) {
			filtered = filtered.filter(ex => ex.category === selectedCategory);
		}
		
		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(ex => 
				ex.name.toLowerCase().includes(query) ||
				ex.category.toLowerCase().includes(query) ||
				ex.difficulty.toLowerCase().includes(query)
			);
		}
		
		filteredExercises = filtered;
	}
	
	function selectCategory(categoryId: string | null) {
		selectedCategory = categoryId;
		filterExercises();
	}
	
	$: {
		filterExercises();
	}
</script>

<div class="exercises-container">
	<header class="page-header">
		<h1>Exercise Library</h1>
		<p class="subtitle">Choose your next challenge</p>
	</header>
	
	<!-- Search Bar -->
	<div class="search-section">
		<div class="search-bar">
			<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
			</svg>
			<input
				type="text"
				placeholder="Search exercises..."
				bind:value={searchQuery}
				class="search-input"
			/>
			{#if searchQuery}
				<button class="clear-btn" on:click={() => searchQuery = ''}>
					<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			{/if}
		</div>
	</div>
	
	<!-- Filter Chips -->
	<div class="filters-section">
		<div class="filter-chips">
			{#each categories as category}
				<button
					class="filter-chip"
					class:active={selectedCategory === category.id}
					on:click={() => selectCategory(category.id)}
				>
					<span class="chip-icon">{category.icon}</span>
					<span class="chip-label">{category.name}</span>
				</button>
			{/each}
		</div>
	</div>
	
	<!-- Exercise Grid -->
	{#if loading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Loading exercises...</p>
		</div>
	{:else}
		<ExerciseGrid exercises={filteredExercises} />
		{#if filteredExercises.length === 0 && !loading}
			<div class="empty-state">
				<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="48" height="48">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
				</svg>
				<p>No exercises found. Try a different search or filter.</p>
			</div>
		{/if}
	{/if}
</div>

<style>
	.exercises-container {
		padding: 2rem 1.5rem;
		max-width: 800px;
		margin: 0 auto;
		animation: fadeIn 0.3s ease-in;
	}
	
	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	
	.page-header {
		margin-bottom: 2rem;
	}
	
	.page-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
		color: var(--text-primary);
	}
	
	.subtitle {
		color: var(--text-secondary);
		font-size: 1rem;
	}
	
	.search-section {
		margin-bottom: 1.5rem;
	}
	
	.search-bar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		padding: 0.75rem 1rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: border-color 0.2s;
	}
	
	.search-bar:focus-within {
		border-color: var(--primary);
	}
	
	.search-bar svg {
		color: var(--text-secondary);
		flex-shrink: 0;
	}
	
	.search-input {
		flex: 1;
		background: transparent;
		border: none;
		color: var(--text-primary);
		font-size: 1rem;
		outline: none;
	}
	
	.search-input::placeholder {
		color: var(--text-secondary);
	}
	
	.clear-btn {
		background: transparent;
		border: none;
		color: var(--text-secondary);
		cursor: pointer;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}
	
	.clear-btn:hover {
		color: var(--text-primary);
	}
	
	.filters-section {
		margin-bottom: 2rem;
	}
	
	.filter-chips {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
	}
	
	.filter-chip {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: var(--bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 9999px;
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.filter-chip:hover {
		background-color: var(--bg-card-hover);
		border-color: rgba(255, 255, 255, 0.2);
	}
	
	.filter-chip.active {
		background-color: var(--primary);
		border-color: var(--primary);
		color: white;
	}
	
	.chip-icon {
		font-size: 1rem;
	}
	
	.chip-label {
		white-space: nowrap;
	}
	
	.loading {
		text-align: center;
		padding: 3rem;
		color: var(--text-secondary);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}
	
	.spinner {
		width: 48px;
		height: 48px;
		border: 4px solid rgba(255, 255, 255, 0.1);
		border-top-color: var(--primary);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	
	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--text-secondary);
	}
	
	.empty-state svg {
		margin: 0 auto 1rem;
		opacity: 0.5;
	}
	
	.empty-state p {
		font-size: 1rem;
		margin-top: 0.5rem;
	}
	
	@media (max-width: 640px) {
		.exercises-container {
			padding: 1.5rem 1rem;
		}
		
		.filter-chips {
			overflow-x: auto;
			padding-bottom: 0.5rem;
			-webkit-overflow-scrolling: touch;
		}
		
		.filter-chip {
			flex-shrink: 0;
		}
	}
</style>

