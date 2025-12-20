<script lang="ts">
	import { onMount } from 'svelte';
	import WelcomeHero from '$lib/components/home/WelcomeHero.svelte';
	import StartWorkoutCTA from '$lib/components/home/StartWorkoutCTA.svelte';
	import TodayProgress from '$lib/components/home/TodayProgress.svelte';
	import { progressStore } from '$lib/stores/progress';

	$: stats = $progressStore.todayStats || {
		reps_today: 0,
		streak: 0,
		calories: 0
	};

	onMount(async () => {
		await progressStore.loadTodayStats();
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
					Full-body tracking needs a wide camera angle. Mobile phones usually can’t capture the entire pose,
					Use a laptop and placed a few meters away for best results.
				</p>
			</div>
		</div>
	</section>

	<section class="safety-notice">
		<div class="notice-content">
			<div class="notice-icon">⚠️</div>
			<div class="notice-text">
				<h3>Fitness Safety First</h3>
				<p>
					Do not perform any exercise before <strong>completely understanding</strong> the technique and 
					<strong>consulting</strong> with a professional.
				</p>
				<p class="sub-tip">
					Please watch all tutorials and read the <strong>Learn</strong> section before starting.
				</p>
			</div>
		</div>
	</section>

	<a href="/schedule" class="schedule-cta">
		<div class="schedule-icon">📅</div>
		<div class="schedule-content">
			<h3>Book a Consultation</h3>
			<p>Get personalized guidance on form and nutrition</p>
		</div>
		<div class="schedule-arrow">→</div>
	</a>

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
		margin: 1rem 0;
		color: var(--text-primary);
	}

	.safety-notice {
		background: rgba(217, 119, 6, 0.15);
		border: 1px solid rgba(245, 158, 11, 0.4);
		border-radius: 1rem;
		padding: 1rem 1.25rem;
		margin: 1rem 0;
		color: var(--text-primary);
	}

	.sub-tip {
		font-size: 0.85rem !important;
		opacity: 0.9;
		background: rgba(0, 0, 0, 0.2);
		padding: 0.5rem;
		border-radius: 0.5rem;
		margin-top: 0.75rem !important;
	}

	.safety-notice strong {
		color: #fbbf24;
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

	.schedule-cta {
		display: flex;
		align-items: center;
		gap: 1rem;
		background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
		border: 1px solid rgba(139, 92, 246, 0.3);
		border-radius: 1rem;
		padding: 1.25rem;
		margin: 1.5rem 0;
		text-decoration: none;
		transition: all 0.3s ease;
	}

	.schedule-cta:hover {
		transform: translateY(-2px);
		border-color: rgba(139, 92, 246, 0.6);
		box-shadow: 0 8px 20px rgba(139, 92, 246, 0.2);
	}

	.schedule-icon {
		font-size: 2rem;
		flex-shrink: 0;
	}

	.schedule-content {
		flex: 1;
	}

	.schedule-content h3 {
		margin: 0;
		font-size: 1.1rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.schedule-content p {
		margin: 0.25rem 0 0;
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	.schedule-arrow {
		font-size: 1.5rem;
		color: var(--primary);
		flex-shrink: 0;
	}

	@media (max-width: 640px) {
		.notice-content {
			flex-direction: column;
		}
	}
</style>
