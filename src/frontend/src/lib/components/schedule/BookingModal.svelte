<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { API_BASE_URL } from '$lib/constants';

	export let day: string;
	export let time: string;
	export let bookingDate: string; // ISO format

	const dispatch = createEventDispatcher();

	let name = '';
	let loading = false;
	let error = '';

	async function handleSubmit() {
		if (!name.trim()) {
			error = 'Please enter your name';
			return;
		}

		loading = true;
		error = '';

		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`${API_BASE_URL}/api/bookings/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${token}`
				},
				body: JSON.stringify({
					name: name.trim(),
					day,
					time,
					booking_date: bookingDate
				})
			});

			if (!response.ok) {
				const data = await response.json();
				throw new Error(data.detail || 'Failed to create booking');
			}

			// Success
			dispatch('success');
		} catch (err: any) {
			error = err.message || 'Something went wrong';
		} finally {
			loading = false;
		}
	}

	function handleCancel() {
		dispatch('cancel');
	}
</script>

<div class="modal-overlay" on:click={handleCancel}>
	<div class="modal-content" on:click|stopPropagation>
		<h2>Book Consultation</h2>
		<div class="booking-details">
			<p><strong>Day:</strong> {day}</p>
			<p><strong>Time:</strong> {time}</p>
			<p><strong>Date:</strong> {new Date(bookingDate).toLocaleDateString()}</p>
		</div>

		<form on:submit|preventDefault={handleSubmit}>
			<div class="form-group">
				<label for="name">Your Name *</label>
				<input
					id="name"
					type="text"
					bind:value={name}
					placeholder="Enter your full name"
					disabled={loading}
					required
				/>
			</div>

			{#if error}
				<div class="error-message">{error}</div>
			{/if}

			<div class="button-group">
				<button type="button" class="btn-cancel" on:click={handleCancel} disabled={loading}>
					Cancel
				</button>
				<button type="submit" class="btn-submit" disabled={loading}>
					{loading ? 'Booking...' : 'Confirm Booking'}
				</button>
			</div>
		</form>
	</div>
</div>

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 1rem;
	}

	.modal-content {
		background: #1e293b;
		border-radius: 1rem;
		padding: 2rem;
		max-width: 500px;
		width: 100%;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	h2 {
		margin: 0 0 1.5rem 0;
		color: #e2e8f0;
		font-size: 1.5rem;
	}

	.booking-details {
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid rgba(59, 130, 246, 0.3);
		border-radius: 0.5rem;
		padding: 1rem;
		margin-bottom: 1.5rem;
	}

	.booking-details p {
		margin: 0.5rem 0;
		color: #cbd5e1;
	}

	.booking-details strong {
		color: #e2e8f0;
	}

	.form-group {
		margin-bottom: 1.5rem;
	}

	label {
		display: block;
		margin-bottom: 0.5rem;
		color: #e2e8f0;
		font-weight: 500;
	}

	input {
		width: 100%;
		padding: 0.75rem;
		background: #0f172a;
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: #e2e8f0;
		font-size: 1rem;
	}

	input:focus {
		outline: none;
		border-color: #3b82f6;
	}

	input:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.error-message {
		background: rgba(220, 38, 38, 0.1);
		border: 1px solid #dc2626;
		color: #fca5a5;
		padding: 0.75rem;
		border-radius: 0.5rem;
		margin-bottom: 1rem;
	}

	.button-group {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
	}

	button {
		padding: 0.75rem 1.5rem;
		border-radius: 0.5rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		border: none;
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-cancel {
		background: transparent;
		border: 1px solid rgba(255, 255, 255, 0.2);
		color: #cbd5e1;
	}

	.btn-cancel:hover:not(:disabled) {
		background: rgba(255, 255, 255, 0.05);
	}

	.btn-submit {
		background: #2563eb;
		color: white;
	}

	.btn-submit:hover:not(:disabled) {
		background: #1d4ed8;
	}
</style>
