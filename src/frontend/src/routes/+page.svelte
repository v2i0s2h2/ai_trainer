<script lang="ts">
	import { onMount } from 'svelte';
	import WelcomeHero from '$lib/components/home/WelcomeHero.svelte';
	import StartWorkoutCTA from '$lib/components/home/StartWorkoutCTA.svelte';
	import TodayProgress from '$lib/components/home/TodayProgress.svelte';
	
	let stats = {
		reps_today: 0,
		streak: 0,
		calories: 0
	};
	
	onMount(async () => {
		try {
			const res = await fetch('/api/stats/today');
			if (res.ok) {
				stats = await res.json();
			}
		} catch (err) {
			console.error('Failed to load stats:', err);
		}
	});
</script>

<div class="home-container">
	<WelcomeHero userName="Champion" />
	<StartWorkoutCTA />
	<TodayProgress 
		repsToday={stats.reps_today}
		streak={stats.streak}
		calories={stats.calories}
	/>
</div>

<style>
	.home-container {
		padding: 2rem 1.5rem;
		max-width: 600px;
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
</style>

