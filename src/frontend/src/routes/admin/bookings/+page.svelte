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

	interface User {
		id: number;
		name: string;
		email: string;
		role: string;
		created_at: string;
	}

	let bookings: Booking[] = [];
	let users: User[] = [];
	let loading = true;
	let error = '';
	let currentTab = 'bookings'; // bookings, users
	let bookingFilter = 'all'; // all, confirmed, cancelled
	let userSearchQuery = '';

	onMount(async () => {
		await Promise.all([
			loadBookings(),
			loadUsers()
		]);
	});

	async function loadUsers() {
		try {
			const token = localStorage.getItem('token');
			if (!token) return;

			const response = await fetch(`${API_BASE_URL}/api/auth/admin/users`, {
				headers: {
					'Authorization': `Bearer ${token}`
				}
			});

			if (!response.ok) {
				throw new Error('Failed to load users');
			}

			users = await response.json();
		} catch (err: any) {
			console.error('Error loading users:', err);
		}
	}

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
		if (bookingFilter === 'all') return true;
		return b.status === bookingFilter;
	});

	$: filteredUsers = users.filter(u => {
		const query = userSearchQuery.toLowerCase();
		return u.name.toLowerCase().includes(query) || 
			   u.email.toLowerCase().includes(query);
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

	<!-- Tab Switcher -->
	<div class="tabs">
		<button class:active={currentTab === 'bookings'} on:click={() => currentTab = 'bookings'}>
			📅 Bookings
		</button>
		<button class:active={currentTab === 'users'} on:click={() => currentTab = 'users'}>
			👥 Users ({users.length})
		</button>
	</div>

	{#if currentTab === 'bookings'}
		<!-- Filters for Bookings -->
		<div class="filters">
			<button class:active={bookingFilter === 'all'} on:click={() => bookingFilter = 'all'}>
				All ({bookings.length})
			</button>
			<button class:active={bookingFilter === 'confirmed'} on:click={() => bookingFilter = 'confirmed'}>
				Confirmed ({bookings.filter(b => b.status === 'confirmed').length})
			</button>
			<button class:active={bookingFilter === 'cancelled'} on:click={() => bookingFilter = 'cancelled'}>
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
			<div class="list-table">
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
								<td class="primary-text">{booking.name}</td>
								<td>{booking.day}</td>
								<td>{booking.time}</td>
								<td>{formatDate(booking.booking_date)}</td>
								<td>
									<span class="status-badge {booking.status}">
										{booking.status}
									</span>
								</td>
								<td class="secondary-text">{formatDate(booking.created_at)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	{:else}
		<!-- Users View -->
		<div class="search-bar">
			<input 
				type="text" 
				placeholder="Search by name or email..." 
				bind:value={userSearchQuery}
			/>
		</div>

		{#if loading}
			<div class="loading">Loading users...</div>
		{:else if filteredUsers.length === 0}
			<div class="empty-state">
				<p>No users found matching your search</p>
			</div>
		{:else}
			<div class="list-table">
				<table>
					<thead>
						<tr>
							<th>Name</th>
							<th>Email</th>
							<th>Role</th>
							<th>Joined On</th>
						</tr>
					</thead>
					<tbody>
						{#each filteredUsers as user}
							<tr>
								<td class="primary-text">{user.name}</td>
								<td>{user.email || 'N/A'}</td>
								<td>
									<span class="role-badge {user.role}">
										{user.role}
									</span>
								</td>
								<td class="secondary-text">{formatDate(user.created_at)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
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

	.tabs {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 2rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding-bottom: 1rem;
	}

	.tabs button {
		background: transparent;
		border: none;
		color: #94a3b8;
		padding: 0.75rem 1.5rem;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		border-radius: 0.5rem;
		transition: all 0.2s;
	}

	.tabs button:hover {
		color: white;
		background: rgba(255, 255, 255, 0.05);
	}

	.tabs button.active {
		color: #3b82f6;
		background: rgba(59, 130, 246, 0.1);
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

	.search-bar {
		margin-bottom: 2rem;
	}

	.search-bar input {
		width: 100%;
		max-width: 400px;
		padding: 0.75rem 1rem;
		background: #1e293b;
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: white;
		font-size: 1rem;
	}

	.search-bar input:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
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

	.list-table {
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

	.primary-text {
		font-weight: 600;
		color: #e2e8f0;
	}

	.secondary-text {
		font-size: 0.9rem;
		color: #94a3b8;
	}

	.status-badge, .role-badge {
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

	.role-badge.admin {
		background: rgba(168, 85, 247, 0.15);
		color: #d8b4fe;
		border: 1px solid #a855f7;
	}

	.role-badge.user {
		background: rgba(71, 85, 105, 0.15);
		color: #cbd5e1;
		border: 1px solid #475569;
	}

	@media (max-width: 768px) {
		.list-table {
			overflow-x: auto;
		}

		table {
			min-width: 600px;
		}
	}
</style>
