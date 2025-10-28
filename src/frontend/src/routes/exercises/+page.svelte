<script lang="ts">
	import { onMount } from 'svelte';
	
	let exercises: any[] = [];
	let loading = true;
	
	onMount(async () => {
		try {
			const res = await fetch('/api/exercises');
			if (res.ok) {
				exercises = await res.json();
			}
		} catch (err) {
			console.error('Failed to load exercises:', err);
		} finally {
			loading = false;
		}
	});
	
	const categoryColors: Record<string, string> = {
		legs: '#F97316',
		chest: '#3B82F6',
		back: '#A855F7',
		shoulders: '#10B981',
		arms: '#EC4899',
		core: '#FBBF24'
	};
</script>

<div class="exercises-container">
	<header class="page-header">
		<h1>Exercise Library</h1>
		<p class="subtitle">Choose your next challenge</p>
	</header>
	
	{#if loading}
		<div class="loading">Loading exercises...</div>
	{:else}
		<div class="exercises-grid">
			{#each exercises as exercise}
				<a href="/workout/{exercise.id}" class="exercise-card" style="--category-color: {categoryColors[exercise.category] || '#3B82F6'}">
					<div class="card-content">
						<div class="exercise-info">
							<h3 class="exercise-name">{exercise.name}</h3>
							<div class="exercise-meta">
								<span class="duration">⏱️ {exercise.duration} min</span>
								<span class="sets">{exercise.sets} × {exercise.reps}</span>
							</div>
						</div>
						<span class="difficulty-badge {exercise.difficulty}">
							{exercise.difficulty}
						</span>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>

<style>
	.exercises-container {
		padding: 2rem 1.5rem;
		max-width: 800px;
		margin: 0 auto;
	}
	
	.page-header {
		margin-bottom: 2rem;
	}
	
	.page-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}
	
	.subtitle {
		color: var(--text-secondary);
		font-size: 1rem;
	}
	
	.loading {
		text-align: center;
		padding: 3rem;
		color: var(--text-secondary);
	}
	
	.exercises-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 1rem;
	}
	
	.exercise-card {
		background-color: var(--bg-card);
		border-radius: 1rem;
		padding: 1.5rem;
		text-decoration: none;
		color: inherit;
		transition: transform 0.2s, box-shadow 0.2s;
		border-left: 4px solid var(--category-color);
	}
	
	.exercise-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
	}
	
	.card-content {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
	}
	
	.exercise-info {
		flex: 1;
	}
	
	.exercise-name {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
	}
	
	.exercise-meta {
		display: flex;
		gap: 1rem;
		font-size: 0.875rem;
		color: var(--text-secondary);
	}
	
	.difficulty-badge {
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: capitalize;
	}
	
	.difficulty-badge.beginner {
		background-color: var(--accent-green);
		color: white;
	}
	
	.difficulty-badge.intermediate {
		background-color: var(--accent-orange);
		color: white;
	}
	
	.difficulty-badge.advanced {
		background-color: var(--accent-purple);
		color: white;
	}
</style>

