<script lang="ts">
	import { onMount } from 'svelte';
	import { progressStore } from '$lib/stores/progress';
	
	$: weeklyStats = $progressStore.weeklyStats;
	$: workoutHistory = $progressStore.workoutHistory;
	$: achievements = $progressStore.achievements;
	$: todayStats = $progressStore.todayStats;
	$: loading = $progressStore.loading;
	$: error = $progressStore.error;
	
	onMount(async () => {
		await progressStore.loadAll();
	});
	
	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		const today = new Date();
		const yesterday = new Date(today);
		yesterday.setDate(yesterday.getDate() - 1);
		
		if (date.toDateString() === today.toDateString()) {
			return 'Today';
		} else if (date.toDateString() === yesterday.toDateString()) {
			return 'Yesterday';
		} else {
			return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
		}
	}
	
	function formatDuration(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		if (secs === 0) {
			return `${mins}m`;
		}
		return `${mins}m ${secs}s`;
	}
	
	function getMaxReps(repsPerDay: number[]): number {
		return Math.max(...repsPerDay, 1);
	}
	
	function getBarHeight(reps: number, maxReps: number): number {
		return (reps / maxReps) * 100;
	}
</script>

<svelte:head>
	<title>Progress - AI Trainer</title>
</svelte:head>

<div class="progress-page">
	<header class="page-header">
		<h1>Your Progress</h1>
		<p class="subtitle">Track your fitness journey</p>
	</header>
	
	{#if loading && !weeklyStats && !workoutHistory.length && !achievements}
		<div class="loading">
			<div class="spinner"></div>
			<p>Loading your progress...</p>
		</div>
	{:else if error}
		<div class="error-state">
			<p>⚠️ {error}</p>
			<button class="retry-btn" on:click={() => progressStore.loadAll()}>
				Retry
			</button>
		</div>
	{:else}
		<!-- Recommended Workout Schedule -->
		<div class="schedule-card">
			<h2 class="section-title">📅 Recommended Weekly Schedule</h2>
			<p class="schedule-intro">4-day workout plan for optimal muscle growth and recovery</p>
			
			<div class="schedule-grid">
				<div class="schedule-day">
					<div class="day-number">Day 1</div>
					<div class="day-type lower">Lower Body</div>
				</div>
				
				<div class="schedule-day">
					<div class="day-number">Day 2</div>
					<div class="day-type upper">Upper Body</div>
				</div>
				
				<div class="schedule-day rest">
					<div class="day-number">Day 3</div>
					<div class="day-type">Rest</div>
				</div>
				
				<div class="schedule-day rest">
					<div class="day-number">Day 4</div>
					<div class="day-type">Rest</div>
				</div>
				
				<div class="schedule-day">
					<div class="day-number">Day 5</div>
					<div class="day-type lower">Lower Body</div>
				</div>
				
				<div class="schedule-day">
					<div class="day-number">Day 6</div>
					<div class="day-type upper">Upper Body</div>
				</div>
				
				<div class="schedule-day rest">
					<div class="day-number">Day 7</div>
					<div class="day-type">Rest</div>
				</div>
			</div>
			
			<div class="schedule-tips">
				<p class="tip-title">💡 Tips:</p>
				<ul class="tip-list">
					<li>Focus on <strong>form and quality</strong> over quantity</li>
					<li>Allow <strong>48 hours</strong> between same muscle group workouts</li>
					<li>Use rest days for <strong>light stretching</strong> or <strong>active recovery</strong></li>
					<li>Combine with <strong>proper protein intake</strong> for maximum muscle gain</li>
				</ul>
			</div>
		</div>
		
		<!-- Summary Stats Cards -->
		{#if todayStats || weeklyStats}
			<div class="summary-cards">
				{#if todayStats}
					<div class="stat-card">
						<div class="stat-icon">🔥</div>
						<div class="stat-content">
							<div class="stat-value">{todayStats.streak}</div>
							<div class="stat-label">Day Streak</div>
						</div>
					</div>
					<div class="stat-card">
						<div class="stat-icon">💪</div>
						<div class="stat-content">
							<div class="stat-value">{todayStats.reps_today}</div>
							<div class="stat-label">Reps Today</div>
						</div>
					</div>
					<div class="stat-card">
						<div class="stat-icon">💪</div>
						<div class="stat-content">
							<div class="stat-value">{Math.round(todayStats.reps_today * 0.06)}g</div>
							<div class="stat-label">Muscle Gain*</div>
						</div>
					</div>
				{/if}
				{#if weeklyStats}
					<div class="stat-card">
						<div class="stat-icon">📊</div>
						<div class="stat-content">
							<div class="stat-value">{weeklyStats.total_reps}</div>
							<div class="stat-label">Total Reps</div>
						</div>
					</div>
					<div class="stat-card">
						<div class="stat-icon">🏋️</div>
						<div class="stat-content">
							<div class="stat-value">{weeklyStats.workouts_completed}</div>
							<div class="stat-label">Workouts</div>
						</div>
					</div>
				{/if}
			</div>
		{/if}
		
		<!-- Weekly Stats Chart -->
		{#if weeklyStats}
			<div class="chart-card">
				<h2 class="section-title">Weekly Activity</h2>
				<div class="chart-container">
					<div class="chart-bars">
						{#each weeklyStats.days as day, index}
							{@const reps = weeklyStats.reps_per_day[index]}
							{@const maxReps = getMaxReps(weeklyStats.reps_per_day)}
							{@const height = getBarHeight(reps, maxReps)}
							<div class="bar-wrapper">
								<div class="bar" style="height: {height}%">
									<span class="bar-value">{reps}</span>
								</div>
								<div class="bar-label">{day}</div>
							</div>
						{/each}
					</div>
				</div>
				<div class="chart-footer">
					<div class="chart-stat">
						<span class="chart-stat-label">Total Reps</span>
						<span class="chart-stat-value">{weeklyStats.total_reps}</span>
					</div>
					<div class="chart-stat">
						<span class="chart-stat-label">Muscle Gain*</span>
						<span class="chart-stat-value">{Math.round(weeklyStats.total_reps * 0.06)}g</span>
					</div>
				</div>
				<p class="muscle-note">
					* Estimated muscle gain based on 3-5g per day with proper training + protein + sleep
				</p>
			</div>
		{/if}
		
		<!-- Workout History -->
		<div class="history-card">
			<h2 class="section-title">Recent Workouts</h2>
			{#if workoutHistory.length > 0}
				<div class="workout-list">
					{#each workoutHistory as workout}
						<div class="workout-item">
							<div class="workout-icon">💪</div>
							<div class="workout-details">
								<div class="workout-name">{workout.exercise_name}</div>
								<div class="workout-meta">
									<span>{formatDate(workout.date)}</span>
									<span>•</span>
									<span>{workout.reps} reps</span>
									<span>•</span>
									<span>{formatDuration(workout.duration)}</span>
									<span>•</span>
									<span>~{Math.round(workout.reps * 0.06)}g muscle*</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="empty-state">
					<p>No workouts yet. Start your first workout to see your history!</p>
				</div>
			{/if}
		</div>
		
		<!-- Achievements -->
		{#if achievements}
			<div class="achievements-card">
				<h2 class="section-title">
					Achievements
					<span class="achievement-count">
						{achievements.unlocked_count} / {achievements.total}
					</span>
				</h2>
				
				{#if achievements.unlocked.length > 0}
					<div class="achievements-section">
						<h3 class="achievements-subtitle">Unlocked 🎉</h3>
						<div class="achievements-grid">
							{#each achievements.unlocked as achievement}
								<div class="achievement-badge unlocked">
									<div class="achievement-icon">{achievement.icon}</div>
									<div class="achievement-name">{achievement.name}</div>
									{#if achievement.date}
										<div class="achievement-date">{achievement.date}</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}
				
				{#if achievements.locked.length > 0}
					<div class="achievements-section">
						<h3 class="achievements-subtitle">Locked 🔒</h3>
						<div class="achievements-grid">
							{#each achievements.locked as achievement}
								<div class="achievement-badge locked">
									<div class="achievement-icon">{achievement.icon}</div>
									<div class="achievement-name">{achievement.name}</div>
									{#if achievement.requirement}
										<div class="achievement-requirement">{achievement.requirement}</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{/if}
	{/if}
</div>

<style>
	.progress-page {
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
	
	/* Recommended Schedule */
	.schedule-card {
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		padding: 1.5rem;
		margin-bottom: 2rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.schedule-intro {
		color: var(--text-secondary);
		margin-bottom: 1.5rem;
		font-size: 0.875rem;
	}
	
	.schedule-grid {
		display: grid;
		grid-template-columns: repeat(7, 1fr);
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}
	
	.schedule-day {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		padding: 1rem 0.5rem;
		text-align: center;
		border: 2px solid transparent;
		transition: all 0.2s;
	}
	
	.schedule-day.rest {
		opacity: 0.6;
		background: rgba(255, 255, 255, 0.02);
	}
	
	.day-number {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
	}
	
	.day-type {
		font-size: 0.75rem;
		font-weight: 600;
		padding: 0.5rem;
		border-radius: 0.375rem;
		color: var(--text-primary);
	}
	
	.day-type.lower {
		background: linear-gradient(135deg, var(--accent-orange), var(--accent-purple));
		color: white;
	}
	
	.day-type.upper {
		background: linear-gradient(135deg, var(--primary), var(--accent-green));
		color: white;
	}
	
	.schedule-tips {
		background: rgba(255, 255, 255, 0.03);
		border-radius: 0.5rem;
		padding: 1rem;
		border-left: 3px solid var(--primary);
	}
	
	.tip-title {
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: var(--text-primary);
	}
	
	.tip-list {
		list-style: none;
		padding-left: 0;
		margin: 0;
	}
	
	.tip-list li {
		padding: 0.375rem 0;
		padding-left: 1.5rem;
		position: relative;
		color: var(--text-secondary);
		font-size: 0.875rem;
		line-height: 1.5;
	}
	
	.tip-list li::before {
		content: "✓";
		position: absolute;
		left: 0;
		color: var(--accent-green);
		font-weight: 600;
	}
	
	/* Summary Stats Cards */
	.summary-cards {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}
	
	.stat-card {
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		padding: 1.25rem;
		display: flex;
		align-items: center;
		gap: 1rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.stat-icon {
		font-size: 2rem;
	}
	
	.stat-content {
		flex: 1;
	}
	
	.stat-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary);
		line-height: 1.2;
	}
	
	.stat-label {
		font-size: 0.875rem;
		color: var(--text-secondary);
		margin-top: 0.25rem;
	}
	
	/* Chart Card */
	.chart-card {
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		padding: 1.5rem;
		margin-bottom: 2rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.section-title {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--text-primary);
		margin-bottom: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	
	.chart-container {
		margin-bottom: 1.5rem;
	}
	
	.chart-bars {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: 0.5rem;
		height: 200px;
		padding: 0 0.5rem;
	}
	
	.bar-wrapper {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		height: 100%;
		justify-content: flex-end;
	}
	
	.bar {
		width: 100%;
		background: linear-gradient(to top, var(--primary), var(--accent-purple));
		border-radius: 0.5rem 0.5rem 0 0;
		position: relative;
		min-height: 20px;
		transition: all 0.3s ease;
		display: flex;
		align-items: flex-start;
		justify-content: center;
		padding-top: 0.5rem;
	}
	
	.bar:hover {
		opacity: 0.9;
		transform: scaleY(1.05);
	}
	
	.bar-value {
		font-size: 0.75rem;
		font-weight: 600;
		color: white;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
	}
	
	.bar-label {
		margin-top: 0.5rem;
		font-size: 0.75rem;
		color: var(--text-secondary);
		font-weight: 500;
	}
	
	.chart-footer {
		display: flex;
		justify-content: space-around;
		padding-top: 1rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.chart-stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
	}
	
	.chart-stat-label {
		font-size: 0.75rem;
		color: var(--text-secondary);
	}
	
	.chart-stat-value {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--text-primary);
	}
	
	.muscle-note {
		font-size: 0.75rem;
		color: var(--text-secondary);
		text-align: center;
		margin-top: 0.75rem;
		font-style: italic;
		opacity: 0.8;
	}
	
	/* Workout History */
	.history-card {
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		padding: 1.5rem;
		margin-bottom: 2rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.workout-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	
	.workout-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background-color: rgba(255, 255, 255, 0.03);
		border-radius: 0.5rem;
		transition: background-color 0.2s;
	}
	
	.workout-item:hover {
		background-color: rgba(255, 255, 255, 0.05);
	}
	
	.workout-icon {
		font-size: 2rem;
		flex-shrink: 0;
	}
	
	.workout-details {
		flex: 1;
	}
	
	.workout-name {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.25rem;
	}
	
	.workout-meta {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		color: var(--text-secondary);
		flex-wrap: wrap;
	}
	
	/* Achievements */
	.achievements-card {
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		padding: 1.5rem;
		margin-bottom: 2rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.achievement-count {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-secondary);
		margin-left: 0.5rem;
	}
	
	.achievements-section {
		margin-bottom: 2rem;
	}
	
	.achievements-section:last-child {
		margin-bottom: 0;
	}
	
	.achievements-subtitle {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 1rem;
	}
	
	.achievements-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
		gap: 1rem;
	}
	
	.achievement-badge {
		background-color: rgba(255, 255, 255, 0.03);
		border-radius: 0.75rem;
		padding: 1rem;
		text-align: center;
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: all 0.2s;
	}
	
	.achievement-badge.unlocked {
		border-color: var(--accent-green);
		background-color: rgba(16, 185, 129, 0.1);
	}
	
	.achievement-badge.locked {
		opacity: 0.6;
		filter: grayscale(0.5);
	}
	
	.achievement-badge:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
	}
	
	.achievement-icon {
		font-size: 2rem;
		margin-bottom: 0.5rem;
	}
	
	.achievement-name {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.25rem;
	}
	
	.achievement-date {
		font-size: 0.75rem;
		color: var(--text-secondary);
	}
	
	.achievement-requirement {
		font-size: 0.75rem;
		color: var(--text-secondary);
		font-style: italic;
	}
	
	/* Loading & Error States */
	.loading {
		text-align: center;
		padding: 4rem 2rem;
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
	
	.error-state {
		text-align: center;
		padding: 3rem 2rem;
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		color: var(--text-secondary);
	}
	
	.retry-btn {
		margin-top: 1rem;
		padding: 0.75rem 1.5rem;
		background-color: var(--primary);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.2s;
	}
	
	.retry-btn:hover {
		opacity: 0.9;
	}
	
	.empty-state {
		text-align: center;
		padding: 3rem 2rem;
		color: var(--text-secondary);
	}
	
	@media (max-width: 640px) {
		.progress-page {
			padding: 1.5rem 1rem;
		}
		
		.schedule-grid {
			grid-template-columns: repeat(4, 1fr);
			gap: 0.5rem;
		}
		
		.schedule-day {
			padding: 0.75rem 0.25rem;
		}
		
		.day-number {
			font-size: 0.75rem;
		}
		
		.day-type {
			font-size: 0.625rem;
			padding: 0.375rem;
		}
		
		.summary-cards {
			grid-template-columns: repeat(2, 1fr);
		}
		
		.chart-bars {
			height: 150px;
			gap: 0.25rem;
		}
		
		.bar-value {
			font-size: 0.625rem;
		}
		
		.bar-label {
			font-size: 0.625rem;
		}
		
		.achievements-grid {
			grid-template-columns: repeat(2, 1fr);
		}
		
		.workout-meta {
			font-size: 0.75rem;
		}
	}
</style>
