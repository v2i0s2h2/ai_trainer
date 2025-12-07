<script lang="ts">
	import { onMount } from 'svelte';
	import ExerciseGrid from '$lib/components/exercises/ExerciseGrid.svelte';
	import { API_BASE_URL } from '$lib/constants';

	let allExercises: any[] = [];
	let loading = true;
	let searchQuery = '';
	let selectedExerciseType: 'rehab' | 'basic' | 'advanced' | 'lifting' = 'basic';

	const exerciseTypes = [
		{ id: 'rehab', name: 'Rehab', icon: '🏥' },
		{ id: 'basic', name: 'Basic', icon: '💪' },
		{ id: 'advanced', name: 'Advanced', icon: '🔥' },
		{ id: 'lifting', name: 'Lifting', icon: '🏋️' }
	];

	onMount(async () => {
		try {
			const res = await fetch(`${API_BASE_URL}/api/exercises`);
			if (res.ok) {
				allExercises = await res.json();
			}
		} catch (err) {
			console.error('Failed to load exercises:', err);
		} finally {
			loading = false;
		}
	});

	function getExercisesByTypeAndCategory(type: string, category: 'upper' | 'lower') {
		let filtered = allExercises.filter(ex =>
			ex.exercise_type === type && ex.category === category
		);

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(ex =>
				ex.name.toLowerCase().includes(query) ||
				ex.difficulty.toLowerCase().includes(query) ||
				ex.target_muscles.some((m: string) => m.toLowerCase().includes(query))
			);
		}

		return filtered;
	}

	function getUpperExercises(type: string) {
		return getExercisesByTypeAndCategory(type, 'upper');
	}

	function getLowerExercises(type: string) {
		return getExercisesByTypeAndCategory(type, 'lower');
	}

	// For advanced section: split upper body into Back/Triceps and Chest/Biceps
	function getBackAndTricepsExercises() {
		const backTricepsIds = [
			'weighted-pull-ups',
			'close-grip-pull-down',
			'wide-grip-row',
			'single-arm-row',
			'weighted-dips',
			'incline-skull-crushers'
		];
		return getUpperExercises('advanced').filter(ex => backTricepsIds.includes(ex.id));
	}

	function getChestAndBicepsExercises() {
		const chestBicepsIds = [
			'incline-bench-press',
			'flat-dumbbell-bench-press',
			'cable-crossovers',
			'hammer-curls',
			'barbell-curls',
			'cable-crunch'
		];
		return getUpperExercises('advanced').filter(ex => chestBicepsIds.includes(ex.id));
	}

	function getShoulderDayExercises() {
		const shoulderDayIds = [
			'incline-dumbbell-shoulder-press',
			'lateral-raises-advanced',
			'lateral-raises-weak-spot',
			'dips-parallel-bars',
			'traps-shrugs',
			'forearm-extension-fix',
			'forearm-flexion-fix'
		];
		return getUpperExercises('advanced').filter(ex => shoulderDayIds.includes(ex.id));
	}
</script>

<div class="exercises-container">
	<header class="page-header">
		<div class="header-top">
			<h1>Exercise Library</h1>
			<a href="/equipment" class="equipment-link-btn">
				<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
				</svg>
				Equipment
			</a>
		</div>
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

	<!-- Exercise Type Tabs -->
	<div class="tabs-section">
		<div class="tabs">
			{#each exerciseTypes as type}
				<button
					class="tab-btn"
					class:active={selectedExerciseType === type.id}
					on:click={() => selectedExerciseType = type.id as any}
				>
					<span class="tab-icon">{type.icon}</span>
					<span class="tab-label">{type.name}</span>
				</button>
			{/each}
		</div>
	</div>

	<!-- Exercise Content -->
	{#if loading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Loading exercises...</p>
		</div>
	{:else}
		<div class="exercises-content">
			{#if selectedExerciseType === 'advanced'}
				<!-- Back and Triceps Section -->
				<div class="section">
					<h2 class="section-title">
						<span class="section-icon">⬆️</span>
						Back and Triceps
					</h2>
					{#if getBackAndTricepsExercises().length > 0}
						<ExerciseGrid exercises={getBackAndTricepsExercises()} />
					{:else}
						<div class="empty-section">
							<p>No back and triceps exercises available yet.</p>
							<p class="coming-soon">More exercises coming soon! 🚀</p>
						</div>
					{/if}
				</div>

				<!-- Chest and Biceps Section -->
				<div class="section">
					<h2 class="section-title">
						<span class="section-icon">💪</span>
						Chest and Biceps
					</h2>
					{#if getChestAndBicepsExercises().length > 0}
						<ExerciseGrid exercises={getChestAndBicepsExercises()} />
					{:else}
						<div class="empty-section">
							<p>No chest and biceps exercises available yet.</p>
							<p class="coming-soon">More exercises coming soon! 🚀</p>
						</div>
					{/if}
				</div>

				<!-- Shoulder Day + Bi and Tri Section -->
				<div class="section">
					<h2 class="section-title">
						<span class="section-icon">🏋️</span>
						Shoulder Day + Bi and Tri
					</h2>
					{#if getShoulderDayExercises().length > 0}
						<ExerciseGrid exercises={getShoulderDayExercises()} />
					{:else}
						<div class="empty-section">
							<p>No shoulder day exercises available yet.</p>
							<p class="coming-soon">More exercises coming soon! 🚀</p>
						</div>
					{/if}
				</div>
			{:else}
				<!-- Upper Body Section (for non-advanced) -->
				<div class="section">
					<h2 class="section-title">
						<span class="section-icon">⬆️</span>
						Upper Body
					</h2>
					{#if getUpperExercises(selectedExerciseType).length > 0}
						<ExerciseGrid exercises={getUpperExercises(selectedExerciseType)} />
					{:else}
						<div class="empty-section">
							<p>No upper body exercises available yet.</p>
							<p class="coming-soon">More exercises coming soon! 🚀</p>
						</div>
					{/if}
				</div>
			{/if}

			<!-- Lower Body Section -->
			<div class="section">
				<h2 class="section-title">
					<span class="section-icon">⬇️</span>
					Lower Body
				</h2>
				{#if getLowerExercises(selectedExerciseType).length > 0}
					<ExerciseGrid exercises={getLowerExercises(selectedExerciseType)} />
				{:else}
					<div class="empty-section">
						<p>No lower body exercises available yet.</p>
						<p class="coming-soon">More exercises coming soon! 🚀</p>
					</div>
				{/if}
			</div>
		</div>
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

	.header-top {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
		gap: 1rem;
	}

	.page-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin: 0;
		color: var(--text-primary);
	}

	.equipment-link-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1rem;
		background-color: var(--bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: var(--text-primary);
		text-decoration: none;
		font-size: 0.875rem;
		font-weight: 500;
		transition: all 0.2s;
		white-space: nowrap;
	}

	.equipment-link-btn:hover {
		background-color: var(--bg-card-hover);
		border-color: var(--primary);
		color: var(--primary);
		transform: translateY(-2px);
	}

	.equipment-link-btn svg {
		flex-shrink: 0;
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

	.tabs-section {
		margin-bottom: 2rem;
	}

	.tabs {
		display: flex;
		gap: 0.75rem;
		overflow-x: auto;
		padding-bottom: 0.5rem;
		-webkit-overflow-scrolling: touch;
	}

	.tab-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.5rem;
		background-color: var(--bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.75rem;
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
		white-space: nowrap;
		flex-shrink: 0;
	}

	.tab-btn:hover {
		background-color: var(--bg-card-hover);
		border-color: rgba(255, 255, 255, 0.2);
	}

	.tab-btn.active {
		background-color: var(--primary);
		border-color: var(--primary);
		color: white;
	}

	.tab-icon {
		font-size: 1.125rem;
	}

	.tab-label {
		font-weight: 600;
	}

	.exercises-content {
		display: flex;
		flex-direction: column;
		gap: 3rem;
	}

	.section {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.section-title {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary);
		margin-bottom: 0.5rem;
	}

	.section-icon {
		font-size: 1.5rem;
	}

	.empty-section {
		text-align: center;
		padding: 3rem 1rem;
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		color: var(--text-secondary);
	}

	.empty-section p {
		margin-bottom: 0.5rem;
	}

	.coming-soon {
		font-size: 0.875rem;
		opacity: 0.7;
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

	@media (max-width: 640px) {
		.exercises-container {
			padding: 1.5rem 1rem;
		}

		.tabs {
			gap: 0.5rem;
		}

		.tab-btn {
			padding: 0.625rem 1.25rem;
			font-size: 0.8125rem;
		}

		.section-title {
			font-size: 1.25rem;
		}

		.exercises-content {
			gap: 2rem;
		}
	}
</style>
