<script lang="ts">
	import { onMount } from 'svelte';
	
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
	<div class="welcome-section">
		<div class="user-avatar">
			<svg fill="currentColor" viewBox="0 0 24 24">
				<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path>
			</svg>
		</div>
		<h1 class="welcome-text">Welcome back,</h1>
		<h2 class="champion-text">Champion! 💪</h2>
		<p class="tagline">Time to crush your goals today!</p>
	</div>
	
	<a href="/exercises" class="start-workout-btn">
		<div class="btn-content">
			<div class="btn-text-group">
				<span class="btn-label">Ready to train?</span>
				<span class="btn-title">Start Workout</span>
			</div>
			<div class="play-icon">
				<svg fill="currentColor" viewBox="0 0 24 24">
					<path d="M8 5v14l11-7z"></path>
				</svg>
			</div>
		</div>
	</a>
	
	<section class="progress-section">
		<h3 class="section-title">Today's Progress</h3>
		<div class="stats-grid">
			<div class="stat-card reps">
				<div class="stat-icon">
					<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<circle cx="12" cy="12" r="10" stroke-width="2"></circle>
						<circle cx="12" cy="12" r="3" fill="currentColor"></circle>
					</svg>
				</div>
				<div class="stat-value">{stats.reps_today}</div>
				<div class="stat-label">Reps Today</div>
			</div>
			
			<div class="stat-card streak">
				<div class="stat-icon">
					<span class="emoji">🔥</span>
				</div>
				<div class="stat-value">{stats.streak} <span class="emoji-inline">🔥</span></div>
				<div class="stat-label">Streak</div>
			</div>
			
			<div class="stat-card calories">
				<div class="stat-icon">
					<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
					</svg>
				</div>
				<div class="stat-value">{stats.calories.toLocaleString()}</div>
				<div class="stat-label">Calories</div>
			</div>
		</div>
	</section>
</div>

<style>
	.home-container {
		padding: 2rem 1.5rem;
		max-width: 600px;
		margin: 0 auto;
	}
	
	.welcome-section {
		text-align: center;
		margin-bottom: 2rem;
	}
	
	.user-avatar {
		width: 64px;
		height: 64px;
		margin: 0 auto 1rem;
		background: linear-gradient(135deg, var(--primary) 0%, #2563EB 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
	}
	
	.user-avatar svg {
		width: 36px;
		height: 36px;
	}
	
	.welcome-text {
		font-size: 1.25rem;
		color: var(--text-secondary);
		font-weight: 400;
		margin-bottom: 0.5rem;
	}
	
	.champion-text {
		font-size: 2.5rem;
		font-weight: 700;
		background: linear-gradient(135deg, var(--primary) 0%, #60A5FA 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		margin-bottom: 0.5rem;
	}
	
	.tagline {
		color: var(--text-secondary);
		font-size: 1rem;
	}
	
	.start-workout-btn {
		display: block;
		background: linear-gradient(135deg, var(--primary) 0%, #2563EB 100%);
		border-radius: 1rem;
		padding: 1.5rem;
		margin-bottom: 2rem;
		text-decoration: none;
		color: white;
		box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);
		transition: transform 0.2s, box-shadow 0.2s;
	}
	
	.start-workout-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 15px 50px rgba(59, 130, 246, 0.4);
	}
	
	.btn-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	
	.btn-text-group {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	
	.btn-label {
		font-size: 0.875rem;
		opacity: 0.9;
	}
	
	.btn-title {
		font-size: 1.5rem;
		font-weight: 700;
	}
	
	.play-icon {
		width: 48px;
		height: 48px;
		background: rgba(255, 255, 255, 0.2);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.play-icon svg {
		width: 24px;
		height: 24px;
		margin-left: 2px;
	}
	
	.progress-section {
		margin-top: 2rem;
	}
	
	.section-title {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 1rem;
	}
	
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
	}
	
	.stat-card {
		background-color: var(--bg-card);
		border-radius: 1rem;
		padding: 1.25rem 0.75rem;
		text-align: center;
		transition: transform 0.2s;
	}
	
	.stat-card:hover {
		transform: translateY(-2px);
	}
	
	.stat-icon {
		width: 32px;
		height: 32px;
		margin: 0 auto 0.75rem;
		color: var(--primary);
	}
	
	.stat-icon svg {
		width: 100%;
		height: 100%;
	}
	
	.streak .stat-icon {
		color: var(--accent-orange);
	}
	
	.calories .stat-icon {
		color: var(--accent-green);
	}
	
	.emoji {
		font-size: 32px;
	}
	
	.emoji-inline {
		font-size: 1rem;
		margin-left: 0.25rem;
	}
	
	.stat-value {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: 0.25rem;
	}
	
	.stat-label {
		font-size: 0.875rem;
		color: var(--text-secondary);
	}
	
	@media (max-width: 400px) {
		.stats-grid {
			grid-template-columns: 1fr;
			gap: 0.75rem;
		}
		
		.stat-card {
			display: flex;
			align-items: center;
			gap: 1rem;
			text-align: left;
		}
		
		.stat-icon {
			margin: 0;
		}
	}
</style>

