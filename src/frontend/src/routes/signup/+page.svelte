<script lang="ts">
	import { authStore } from '$lib/stores/auth';

	let name = '';
	let email = '';
	let password = '';

	$: loading = $authStore.loading;
	$: error = $authStore.error;

	async function handleSubmit() {
		if (!name || !email || !password) return;
		await authStore.register(name, email, password);
	}
</script>

<svelte:head>
	<title>Sign Up - AI Trainer</title>
</svelte:head>

<div class="auth-container">
	<div class="auth-card">
		<div class="logo">
			<h1>AI Trainer</h1>
			<p>Start your fitness journey</p>
		</div>

		{#if error}
			<div class="error-alert">
				{error}
			</div>
		{/if}

		<form on:submit|preventDefault={handleSubmit} class="auth-form">
			<div class="form-group">
				<label for="name">Full Name</label>
				<input
					type="text"
					id="name"
					bind:value={name}
					placeholder="Enter your name"
					required
				/>
			</div>

			<div class="form-group">
				<label for="email">Email</label>
				<input
					type="email"
					id="email"
					bind:value={email}
					placeholder="Enter your email"
					required
				/>
			</div>

			<div class="form-group">
				<label for="password">Password</label>
				<input
					type="password"
					id="password"
					bind:value={password}
					placeholder="Create a password"
					required
					minlength="6"
				/>
			</div>

			<button type="submit" class="submit-btn" disabled={loading}>
				{#if loading}
					<span class="spinner"></span> Creating Account...
				{:else}
					Sign Up
				{/if}
			</button>
		</form>

		<div class="auth-footer">
			<p>Already have an account? <a href="/login">Login</a></p>
		</div>
	</div>
</div>

<style>
	.auth-container {
		min-height: 80vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
	}

	.auth-card {
		background-color: var(--bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 1rem;
		padding: 2rem;
		width: 100%;
		max-width: 400px;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
	}

	.logo {
		text-align: center;
		margin-bottom: 2rem;
	}

	.logo h1 {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--primary);
		margin: 0;
	}

	.logo p {
		color: var(--text-secondary);
		margin-top: 0.5rem;
	}

	.error-alert {
		background-color: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #ef4444;
		padding: 0.75rem;
		border-radius: 0.5rem;
		margin-bottom: 1.5rem;
		font-size: 0.875rem;
		text-align: center;
	}

	.auth-form {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-secondary);
	}

	.form-group input {
		padding: 0.75rem;
		border-radius: 0.5rem;
		background-color: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
		color: var(--text-primary);
		font-size: 1rem;
		transition: border-color 0.2s;
	}

	.form-group input:focus {
		outline: none;
		border-color: var(--primary);
	}

	.submit-btn {
		margin-top: 1rem;
		padding: 0.875rem;
		background-color: var(--primary);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		font-size: 1rem;
		cursor: pointer;
		transition: background-color 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
	}

	.submit-btn:hover:not(:disabled) {
		background-color: var(--primary-hover);
	}

	.submit-btn:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.auth-footer {
		margin-top: 2rem;
		text-align: center;
		font-size: 0.875rem;
		color: var(--text-secondary);
	}

	.auth-footer a {
		color: var(--primary);
		text-decoration: none;
		font-weight: 600;
	}

	.auth-footer a:hover {
		text-decoration: underline;
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
