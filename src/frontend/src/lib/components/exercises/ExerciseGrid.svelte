<script lang="ts">
	import ExerciseCard from './ExerciseCard.svelte';
	
	export let exercises: any[] = [];
</script>

<div class="exercises-grid">
	{#each exercises as exercise (exercise.id)}
		<ExerciseCard {exercise} />
	{/each}
</div>

{#if exercises.length === 0}
	<div class="empty-state">
		<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="48" height="48">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
		</svg>
		<p>No exercises found</p>
	</div>
{/if}

<style>
	.exercises-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 1rem;
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
		.exercises-grid {
			grid-template-columns: 1fr;
		}
	}
</style>

