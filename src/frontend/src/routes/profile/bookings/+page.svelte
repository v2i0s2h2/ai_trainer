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
    let cancelLoadingId: number | null = null;

    onMount(async () => {
        await loadMyBookings();
    });

    async function loadMyBookings() {
        loading = true;
        error = '';
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                goto('/login');
                return;
            }

            const response = await fetch(`${API_BASE_URL}/api/bookings/my`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load your bookings');
            }

            bookings = await response.json();
        } catch (err: any) {
            error = err.message || 'Something went wrong';
        } finally {
            loading = false;
        }
    }

    async function cancelBooking(id: number) {
        if (!confirm('Are you sure you want to cancel this booking?')) return;

        cancelLoadingId = id;
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/bookings/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to cancel booking');
            }

            // Refresh list
            await loadMyBookings();
            alert('Booking cancelled successfully');
        } catch (err: any) {
            alert(err.message);
        } finally {
            cancelLoadingId = null;
        }
    }

    function isPast(dateStr: string): boolean {
        return new Date(dateStr) < new Date();
    }

    function canCancel(bookingDate: string): boolean {
        const appointmentDate = new Date(bookingDate);
        const now = new Date();
        const diffInHours = (appointmentDate.getTime() - now.getTime()) / (1000 * 60 * 60);
        return diffInHours > 24;
    }
</script>

<div class="my-bookings-container">
    <header class="page-header">
        <button class="back-link" on:click={() => goto('/profile')}>← Back to Profile</button>
        <h1>My Consultations</h1>
        <p class="subtitle">View and manage your scheduled sessions</p>
    </header>

    {#if loading}
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Fetching your bookings...</p>
        </div>
    {:else if error}
        <div class="error-state">
            <p>❌ {error}</p>
            <button class="retry-btn" on:click={loadMyBookings}>Retry</button>
        </div>
    {:else if bookings.length === 0}
        <div class="empty-state">
            <div class="empty-icon">🗓️</div>
            <h3>No bookings yet</h3>
            <p>Your scheduled consultations will appear here.</p>
            <button class="book-now-btn" on:click={() => goto('/schedule')}>Book a Session</button>
        </div>
    {:else}
        <div class="bookings-list">
            {#each bookings as booking}
                <div class="booking-card {booking.status === 'cancelled' ? 'cancelled' : ''}">
                    <div class="booking-info">
                        <div class="date-time">
                            <span class="day">{booking.day}</span>
                            <span class="time">{booking.time}</span>
                        </div>
                        <div class="date-full">
                            {new Date(booking.booking_date).toLocaleDateString('en-US', { 
                                weekday: 'long', 
                                year: 'numeric', 
                                month: 'long', 
                                day: 'numeric' 
                            })}
                        </div>
                        <div class="status-badge {booking.status}">
                            {booking.status.toUpperCase()}
                        </div>
                    </div>

                    {#if booking.status !== 'cancelled' && !isPast(booking.booking_date)}
                        <div class="actions">
                            {#if canCancel(booking.booking_date)}
                                <button 
                                    class="cancel-btn" 
                                    on:click={() => cancelBooking(booking.id)}
                                    disabled={cancelLoadingId === booking.id}
                                >
                                    {cancelLoadingId === booking.id ? 'Cancelling...' : 'Cancel Session'}
                                </button>
                            {:else}
                                <span class="cancel-deadline">Cancellation closed (&lt; 24h)</span>
                            {/if}
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .my-bookings-container {
        padding: 2rem 1rem;
        max-width: 800px;
        margin: 0 auto;
        color: white;
    }

    .page-header {
        margin-bottom: 2rem;
    }

    .back-link {
        background: none;
        border: none;
        color: #60a5fa;
        cursor: pointer;
        font-size: 0.9rem;
        padding: 0;
        margin-bottom: 1rem;
    }

    h1 {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #94a3b8;
    }

    .loading-state, .error-state, .empty-state {
        background: #1e293b;
        padding: 3rem;
        border-radius: 1rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top-color: #3b82f6;
        border-radius: 50%;
        margin: 0 auto 1rem;
        animation: spin 1s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .book-now-btn {
        margin-top: 1.5rem;
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        cursor: pointer;
    }

    .bookings-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .booking-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s;
    }

    .booking-card.cancelled {
        opacity: 0.6;
        border-style: dashed;
    }

    .date-time {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }

    .day {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
    }

    .time {
        background: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        padding: 0.25rem 0.75rem;
        border-radius: 99px;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .date-full {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }

    .status-badge {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }

    .status-badge.confirmed { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
    .status-badge.cancelled { background: rgba(239, 68, 68, 0.2); color: #f87171; }

    .cancel-btn {
        background: rgba(239, 68, 68, 0.1);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .cancel-btn:hover:not(:disabled) {
        background: rgba(239, 68, 68, 0.2);
    }

    .cancel-deadline {
        font-size: 0.8rem;
        color: #64748b;
        font-style: italic;
    }

    @media (max-width: 640px) {
        .booking-card {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }
        .actions {
            width: 100%;
        }
        .cancel-btn {
            width: 100%;
        }
    }
</style>
