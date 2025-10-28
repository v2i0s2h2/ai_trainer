<div class="page-container">
	<header class="page-header">
		<h1>Profile</h1>
		<p class="subtitle">Manage your account</p>
	</header>
	
	<div class="profile-card">
		<div class="avatar">
			<svg fill="currentColor" viewBox="0 0 24 24">
				<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path>
			</svg>
		</div>
		<h2>John Doe</h2>
		<p class="email">john.doe@example.com</p>
		
		<div class="stats-row">
			<div class="stat">
				<div class="stat-value">247</div>
				<div class="stat-label">Workouts</div>
			</div>
			<div class="stat">
				<div class="stat-value">12</div>
				<div class="stat-label">Streak</div>
			</div>
			<div class="stat">
				<div class="stat-value">45</div>
				<div class="stat-label">Days Active</div>
			</div>
		</div>
	</div>
	
	<div class="coming-soon">
		<p>Settings, achievements, and more features coming soon!</p>
	</div>
</div>

<style>
	.page-container {
		padding: 2rem 1.5rem;
		max-width: 600px;
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
	}
	
	.profile-card {
		background-color: var(--bg-card);
		border-radius: 1rem;
		padding: 2rem;
		text-align: center;
		margin-bottom: 1rem;
	}
	
	.avatar {
		width: 80px;
		height: 80px;
		margin: 0 auto 1rem;
		background: linear-gradient(135deg, var(--primary) 0%, #2563EB 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
	}
	
	.avatar svg {
		width: 48px;
		height: 48px;
	}
	
	.profile-card h2 {
		font-size: 1.5rem;
		margin-bottom: 0.25rem;
	}
	
	.email {
		color: var(--text-secondary);
		margin-bottom: 1.5rem;
	}
	
	.stats-row {
		display: flex;
		justify-content: space-around;
		gap: 1rem;
		padding-top: 1.5rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.stat {
		text-align: center;
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
	
	.coming-soon {
		text-align: center;
		padding: 1.5rem;
		background-color: var(--bg-card);
		border-radius: 1rem;
		color: var(--text-secondary);
	}
</style>

