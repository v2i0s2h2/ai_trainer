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
	
	<section class="device-notice">
		<div class="notice-content">
			<div class="notice-icon">🖥️</div>
			<div class="notice-text">
				<h3>Best experience on laptop or external webcam</h3>
				<p>
					Full-body tracking needs a wide camera angle. Mobile phones usually can’t capture the entire pose, so rep counting might be unreliable. 
					Use a laptop (or USB webcam) placed a few meters away for best results.
				</p>
			</div>
		</div>
	</section>
	
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
	
	.device-notice {
		background: rgba(59, 130, 246, 0.15);
		border: 1px solid rgba(59, 130, 246, 0.4);
		border-radius: 1rem;
		padding: 1rem 1.25rem;
		margin: 1.5rem 0;
		color: var(--text-primary);
	}
	
	.notice-content {
		display: flex;
		gap: 1rem;
		align-items: flex-start;
	}
	
	.notice-icon {
		font-size: 1.75rem;
	}
	
	.notice-text h3 {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
	}
	
	.notice-text p {
		margin: 0.35rem 0 0;
		font-size: 0.9rem;
		color: var(--text-secondary);
		line-height: 1.4;
	}
	
	@media (max-width: 640px) {
		.notice-content {
			flex-direction: column;
		}
	}
</style>

