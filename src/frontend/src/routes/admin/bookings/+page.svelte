<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE_URL } from '$lib/constants';
	import { goto } from '$app/navigation';

	interface Booking {
		id: number;
		name: string;
		day: string;
		time: string;
		booking_date: string;
		status: string;
		created_at: string;
	}

	let bookings: Booking[] = [];
	let loading = true;
	let error = '';
	let filter = 'all'; // all, confirmed, cancelled

	onMount(async () => {
		await loadBookings();
	});

	async function loadBookings() {
		loading = true;
		error = '';

		try {
			const token = localStorage.getItem('token');
			if (!token) {
				goto('/login');
				return;
			}

			const response = await fetch(`${API_BASE_URL}/api/bookings/`, {
				headers: {
					'Authorization': `Bearer ${token}`
				}
			});

			if (!response.ok) {
				throw new Error('Failed to load bookings');
			}

			bookings = await response.json();
		} catch (err: any) {
			error = err.message || 'Failed to load bookings';
		} finally {
			loading = false;
		}
	}

	$: filteredBookings = bookings.filter(b => {
		if (filter === 'all') return true;
		return b.status === filter;
	});

	function formatDate(isoDate: string): string {
		return new Date(isoDate).toLocaleDateString('en-US', {
			weekday: 'short',
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}
</script>

<div class="admin-container">
	<header class="page-header">
		<h1>📅 Consultation Bookings</h1>
		<p class="subtitle">Manage all consultation appointments</p>
	</header>

	<!-- Filters -->
	<div class="filters">
		<button class:active={filter === 'all'} on:click={() => filter = 'all'}>
			All ({bookings.length})
		</button>
		<button class:active={filter === 'confirmed'} on:click={() => filter = 'confirmed'}>
			Confirmed ({bookings.filter(b => b.status === 'confirmed').length})
		</button>
		<button class:active={filter === 'cancelled'} on:click={() => filter = 'cancelled'}>
			Cancelled ({bookings.filter(b => b.status === 'cancelled').length})
		</button>
	</div>

	{#if loading}
		<div class="loading">Loading bookings...</div>
	{:else if error}
		<div class="error-message">{error}</div>
	{:else if filteredBookings.length === 0}
		<div class="empty-state">
			<p>No bookings found</p>
		</div>
	{:else}
		<div class="bookings-table">
			<table>
				<thead>
					<tr>
						<th>Name</th>
						<th>Day</th>
						<th>Time</th>
						<th>Date</th>
						<th>Status</th>
						<th>Booked On</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredBookings as booking}
						<tr class={booking.status}>
							<td class="name">{booking.name}</td>
							<td>{booking.day}</td>
							<td>{booking.time}</td>
							<td>{formatDate(booking.booking_date)}</td>
							<td>
								<span class="status-badge {booking.status}">
									{booking.status}
								</span>
							</td>
							<td class="created">{formatDate(booking.created_at)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<style>
	.admin-container {
		padding: 2rem;
		max-width: 1200px;
		margin: 0 auto;
		color: white;
	}

	.page-header {
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 2rem;
		margin-bottom: 0.5rem;
		color: #e2e8f0;
	}

	.subtitle {
		color: #94a3b8;
		font-size: 1rem;
	}

	.filters {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
		flex-wrap: wrap;
	}

	.filters button {
		padding: 0.5rem 1rem;
		background: #1e293b;
		border: 1px solid rgba(255, 255, 255, 0.1);
		color: #cbd5e1;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.filters button:hover {
		background: #334155;
	}

	.filters button.active {
		background: #2563eb;
		border-color: #2563eb;
		color: white;
	}

	.loading, .empty-state {
		text-align: center;
		padding: 3rem;
		color: #94a3b8;
	}

	.error-message {
		background: rgba(220, 38, 38, 0.1);
		border: 1px solid #dc2626;
		color: #fca5a5;
		padding: 1rem;
		border-radius: 0.5rem;
	}

	.bookings-table {
		background: #1e293b;
		border-radius: 1rem;
		overflow: hidden;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	thead {
		background: #0f172a;
	}

	th {
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		color: #e2e8f0;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	td {
		padding: 1rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		color: #cbd5e1;
	}

	tr:last-child td {
		border-bottom: none;
	}

	tr.cancelled {
		opacity: 0.6;
	}

	.name {
		font-weight: 600;
		color: #e2e8f0;
	}

	.created {
		font-size: 0.9rem;
		color: #94a3b8;
	}

	.status-badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		font-size: 0.85rem;
		font-weight: 600;
		text-transform: capitalize;
	}

	.status-badge.confirmed {
		background: rgba(34, 197, 94, 0.15);
		color: #86efac;
		border: 1px solid #22c55e;
	}

	.status-badge.cancelled {
		background: rgba(220, 38, 38, 0.15);
		color: #fca5a5;
		border: 1px solid #dc2626;
	}

	@media (max-width: 768px) {
		.bookings-table {
			overflow-x: auto;
		}

		table {
			min-width: 600px;
		}
	}
</style>
