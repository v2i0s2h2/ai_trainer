<script lang="ts">
	export let userName: string = 'Champion';
</script>

<div class="welcome-section">
	<div class="user-avatar">
		<svg fill="currentColor" viewBox="0 0 24 24">
			<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path>
		</svg>
	</div>
	<h1 class="welcome-text">Welcome back,</h1>
	<h2 class="champion-text">{userName}! 💪</h2>
	<p class="tagline">Time to crush your goals today!</p>
</div>

<style>
	.welcome-section {
		text-align: center;
		margin-bottom: 2rem;
	}
	
	.user-avatar {
		width: 64px;
		height: 64px;
		margin: 0 auto 1rem;
		background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
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
		margin-top: 0.5rem;
	}
</style>

