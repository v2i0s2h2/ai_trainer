<script lang="ts">
    import { onMount } from 'svelte';
    import { API_BASE_URL } from '$lib/constants';
    import { authStore } from '$lib/stores/auth';
    import BookingModal from '$lib/components/schedule/BookingModal.svelte';
    
    // Status codes: 0=Unavailable, 1=Available, 2=Booked by Others, 3=Booked by ME
    let schedule = [
        // ... (same static structure)
        { day: 'Monday', slots: [
            { time: '09:00 AM', status: 1 },
            { time: '10:00 AM', status: 0 },
            { time: '11:00 AM', status: 1 },
            { time: '04:00 PM', status: 1 },
            { time: '05:00 PM', status: 1 }
        ]},
        { day: 'Tuesday', slots: [
            { time: '09:00 AM', status: 1 },
            { time: '10:00 AM', status: 1 },
            { time: '11:00 AM', status: 1 },
            { time: '04:00 PM', status: 0 },
            { time: '05:00 PM', status: 1 }
        ]},
        { day: 'Wednesday', slots: [
            { time: '09:00 AM', status: 1 },
            { time: '10:00 AM', status: 1 },
            { time: '11:00 AM', status: 1 },
            { time: '04:00 PM', status: 1 },
            { time: '05:00 PM', status: 1 }
        ]},
        { day: 'Thursday', slots: [
            { time: '09:00 AM', status: 0 },
            { time: '10:00 AM', status: 0 },
            { time: '11:00 AM', status: 1 },
            { time: '04:00 PM', status: 1 },
            { time: '05:00 PM', status: 1 }
        ]},
        { day: 'Friday', slots: [
            { time: '09:00 AM', status: 1 },
            { time: '10:00 AM', status: 1 },
            { time: '11:00 AM', status: 1 },
            { time: '04:00 PM', status: 0 },
            { time: '05:00 PM', status: 0 }
        ]},
        { day: 'Saturday', slots: [
            { time: '10:00 AM', status: 1 },
            { time: '11:00 AM', status: 1 },
            { time: '12:00 PM', status: 1 }
        ]},
        { day: 'Sunday', slots: [] }
    ];

    let showBookingModal = false;
    let selectedDay = '';
    let selectedTime = '';
    let selectedDate = '';
    let successMessage = '';
    let isLoading = false;

    onMount(async () => {
        await syncScheduleWithBookings();
    });

    async function syncScheduleWithBookings() {
        isLoading = true;
        try {
            const token = localStorage.getItem('token');
            const currentUserId = $authStore.user?.id;
            
            const response = await fetch(`${API_BASE_URL}/api/bookings/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const realBookings = await response.json();
                
                schedule = schedule.map(dayData => ({
                    ...dayData,
                    slots: dayData.slots.map(slot => {
                        const booking = realBookings.find(b => 
                            b.day === dayData.day && 
                            b.time === slot.time && 
                            b.status === 'confirmed'
                        );
                        
                        if (booking) {
                            // Status 3 if mine, Status 2 if others
                            return { ...slot, status: booking.user_id === currentUserId ? 3 : 2 };
                        }
                        return slot;
                    })
                }));
            }
        } catch (err) {
            console.error('Failed to sync schedule:', err);
        } finally {
            isLoading = false;
        }
    }

    function getNextDate(dayName: string): string {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const today = new Date();
        const targetDay = days.indexOf(dayName);
        const currentDay = today.getDay();
        
        let daysUntilTarget = targetDay - currentDay;
        if (daysUntilTarget <= 0) {
            daysUntilTarget += 7; // Next week
        }
        
        const targetDate = new Date(today);
        targetDate.setDate(today.getDate() + daysUntilTarget);
        return targetDate.toISOString().split('T')[0];
    }

    function handleBook(day: string, time: string) {
        selectedDay = day;
        selectedTime = time;
        selectedDate = getNextDate(day);
        showBookingModal = true;
        successMessage = '';
    }

    async function handleBookingSuccess() {
        showBookingModal = false;
        successMessage = `Booking confirmed for ${selectedDay} at ${selectedTime}!`;
        await syncScheduleWithBookings(); // Re-sync to show new booking
        setTimeout(() => {
            successMessage = '';
        }, 5000);
    }

    function handleBookingCancel() {
        showBookingModal = false;
    }
</script>

<div class="schedule-container">
    <!-- Header Section -->
    <header class="page-header">
        <h1>Consultation & Scheduling</h1>
        <p class="subtitle">Book a 1-on-1 session to perfect your form and nutrition plan.</p>
    </header>

    <!-- Success Message -->
    {#if successMessage}
        <div class="success-banner">
            ✅ {successMessage}
        </div>
    {/if}

    <!-- Contact Info Cards -->
    <div class="contact-grid">
        <div class="contact-card">
            <span class="icon">📧</span>
            <h3>Email</h3>
            <p>vvo83150@gmail.com</p>
        </div>
        <div class="contact-card">
            <span class="icon">📞</span>
            <h3>Phone</h3>
            <p>+91 7389345065</p>
        </div>
        <div class="contact-card highlight">
            <span class="icon">📹</span>
            <h3>Zoom Meeting</h3>
            <a href="https://us05web.zoom.us/j/7519517112?pwd=r3b59xWVLhOVvfhh7vZg0CDkbrbPKJ.1" target="_blank" class="meet-link">Join Personal Room</a>
        </div>
    </div>

    <!-- Weekly Schedule -->
    <div class="schedule-grid">
                <div class="schedule-header">
            <h2>Weekly Availability</h2>
            <div class="legend">
                <span class="status available">Available</span>
                <span class="status mine">Your Session</span>
                <span class="status unavailable">Unavailable</span>
            </div>
        </div>

        <div class="timetable">
            {#each schedule as dayData}
                <div class="day-column">
                    <h3 class="day-name">{dayData.day}</h3>
                    <div class="slots">
                        {#if dayData.slots.length === 0}
                            <div class="slot closed">Closed</div>
                        {:else}
                            {#each dayData.slots as slot}
                                <div class="slot {slot.status === 1 ? 'available' : slot.status === 2 ? 'booked' : slot.status === 3 ? 'mine' : 'unavailable'}">
                                    <span class="time">{slot.time}</span>
                                    {#if slot.status === 1}
                                        <button class="book-btn" on:click={() => handleBook(dayData.day, slot.time)}>Book</button>
                                    {:else if slot.status === 2}
                                        <span class="status-text">Unavailable</span>
                                    {:else if slot.status === 3}
                                        <span class="status-text mine-text">Your Session</span>
                                    {:else}
                                        <span class="status-text">--</span>
                                    {/if}
                                </div>
                            {/each}
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    </div>
</div>

<!-- Booking Modal -->
{#if showBookingModal}
    <BookingModal
        day={selectedDay}
        time={selectedTime}
        bookingDate={selectedDate}
        on:success={handleBookingSuccess}
        on:cancel={handleBookingCancel}
    />
{/if}

<style>
    .schedule-container {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
        color: white;
    }

    .page-header {
        text-align: center;
        margin-bottom: 3rem;
    }

    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
    }

    .success-banner {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid #22c55e;
        color: #86efac;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 600;
    }

    /* Contact Cards */
    .contact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 3rem;
    }

    .contact-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s;
    }

    .contact-card:hover {
        transform: translateY(-5px);
        border-color: #60a5fa;
    }

    .contact-card.highlight {
        background: linear-gradient(to bottom right, #1e293b, #1e1b4b);
        border-color: #818cf8;
    }

    .icon {
        font-size: 2rem;
        display: block;
        margin-bottom: 1rem;
    }

    .contact-card h3 {
        margin: 0 0 0.5rem 0;
        color: #e2e8f0;
    }

    .contact-card p {
        color: #94a3b8;
        margin: 0;
    }

    .meet-link {
        display: inline-block;
        margin-top: 0.5rem;
        color: #60a5fa;
        text-decoration: none;
        font-weight: 600;
    }

    /* Schedule Grid */
    .schedule-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .legend {
        display: flex;
        gap: 1rem;
    }

    .status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: #cbd5e1;
    }

    .status::before {
        content: '';
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }

    .status.available::before { background: #2563eb; }
    .status.mine::before { background: #10b981; }
    .status.unavailable::before { background: #475569; }

    .timetable {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        overflow-x: auto;
    }

    .day-column {
        background: #0f172a;
        border-radius: 0.5rem;
        overflow: hidden;
    }

    .day-name {
        background: #1e293b;
        color: #e2e8f0;
        padding: 1rem;
        margin: 0;
        text-align: center;
        font-size: 1rem;
        border-bottom: 1px solid #334155;
    }

    .slots {
        padding: 0.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .slot {
        padding: 0.75rem;
        border-radius: 0.25rem;
        text-align: center;
        font-size: 0.9rem;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        transition: all 0.2s;
    }

    .slot.available {
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.3);
    }
    
    .slot.available:hover {
        background: rgba(37, 99, 235, 0.2);
    }

    .slot.mine {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
    }

    .mine-text {
        color: #34d399 !important;
        font-weight: 700;
    }

    .slot.booked {
        background: rgba(47, 55, 105, 0.1);
        border: 1px solid #475569;
        opacity: 0.5;
    }

    .slot.unavailable {
        background: #1e293b;
        color: #64748b;
    }

    .slot.closed {
        padding: 2rem 0;
        color: #64748b;
        font-style: italic;
    }

    .book-btn {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 0.2rem;
        cursor: pointer;
        font-size: 0.8rem;
        font-weight: 600;
        width: 100%;
    }

    .book-btn:hover {
        background: #1d4ed8;
    }

    .time {
        font-weight: 600;
        color: #e2e8f0;
    }

    .status-text {
        font-size: 0.8rem;
        color: #94a3b8;
    }

    @media (max-width: 768px) {
        .timetable {
            grid-template-columns: repeat(2, 1fr); /* 2 columns on mobile */
        }
    }
</style>
