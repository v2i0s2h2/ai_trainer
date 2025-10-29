<script lang="ts">
	import StatCard from '$lib/components/ui/StatCard.svelte';
	
	export let repsToday: number = 0;
	export let streak: number = 0;
	export let calories: number = 0;
</script>

<section class="progress-section">
	<h3 class="section-title">Today's Progress</h3>
	<div class="stats-grid">
		<StatCard value={repsToday} label="Reps Today">
			<svelte:fragment slot="icon">
				<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<circle cx="12" cy="12" r="10" stroke-width="2"></circle>
					<circle cx="12" cy="12" r="3" fill="currentColor"></circle>
				</svg>
			</svelte:fragment>
		</StatCard>
		
		<StatCard value={`${streak} 🔥`} label="Streak" color="var(--accent-orange)">
			<svelte:fragment slot="icon">
				<span style="font-size: 32px;">🔥</span>
			</svelte:fragment>
		</StatCard>
		
		<StatCard value={calories.toLocaleString()} label="Calories" color="var(--accent-green)">
			<svelte:fragment slot="icon">
				<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
				</svg>
			</svelte:fragment>
		</StatCard>
	</div>
</section>

<style>
	.progress-section {
		margin-top: 2rem;
	}
	
	.section-title {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 1rem;
		color: var(--text-primary);
	}
	
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
	}
	
	@media (max-width: 400px) {
		.stats-grid {
			grid-template-columns: 1fr;
			gap: 0.75rem;
		}
	}
</style>

