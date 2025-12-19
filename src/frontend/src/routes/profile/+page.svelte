<script lang="ts">
    import { onMount } from "svelte";
    import { profileStore } from "$lib/stores/profile";
    import { authStore } from "$lib/stores/auth";
    import { goto } from "$app/navigation";
    import { API_BASE_URL } from "$lib/constants";

    let editMode = false;
    let editName = "";
    let editEmail = "";
    let achievements: any = null;
    let loadingAchievements = false;

    $: profile = $profileStore.profile;
    $: loading = $profileStore.loading;
    $: error = $profileStore.error;

    onMount(async () => {
        await profileStore.loadProfile();
        await loadAchievements();
    });

    async function loadAchievements() {
        loadingAchievements = true;
        try {
            const res = await fetch(`${API_BASE_URL}/api/achievements`);
            if (res.ok) {
                achievements = await res.json();
            }
        } catch (err) {
            console.error("Failed to load achievements:", err);
        } finally {
            loadingAchievements = false;
        }
    }

    function startEdit() {
        if (profile) {
            editName = profile.name;
            editEmail = profile.email || "";
            editMode = true;
        }
    }

    function cancelEdit() {
        editMode = false;
        editName = "";
        editEmail = "";
    }

    async function saveProfile() {
        if (!profile) return;

        await profileStore.updateProfile({
            name: editName,
            email: editEmail || undefined,
        });

        editMode = false;
    }

    function getInitials(name: string): string {
        const words = name.trim().split(" ");
        if (words.length >= 2) {
            return (words[0][0] + words[words.length - 1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }

    async function updatePreferences(prefs: {
        notifications_enabled?: boolean;
        units?: "metric" | "imperial";
    }) {
        if (!profile) return;

        await profileStore.updateProfile({
            preferences: {
                ...profile.preferences,
                ...prefs,
            },
        });
    }

    function handleLogout() {
        authStore.logout();
    }
</script>

<svelte:head>
    <title>Profile - AI Trainer</title>
</svelte:head>

<div class="profile-page">
    <header class="page-header">
        <h1>Profile</h1>
        <p class="subtitle">Manage your account and preferences</p>
    </header>

    {#if loading && !profile}
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading profile...</p>
        </div>
    {:else if error}
        <div class="error-state">
            <p>❌ {error}</p>
            <button
                class="retry-btn"
                on:click={() => profileStore.loadProfile()}
            >
                Retry
            </button>
        </div>
    {:else if profile}
        <!-- Profile Header Card -->
        <div class="profile-card">
            <div class="avatar-section">
                <div class="avatar">
                    <span class="avatar-initials"
                        >{getInitials(profile.name)}</span
                    >
                </div>
                <div class="avatar-note">
                    <p class="coming-soon-badge">📸 Body Image - Coming Soon</p>
                </div>
            </div>

            {#if !editMode}
                <div class="profile-info">
                    <h2>{profile.name}</h2>
                    <p class="email">{profile.email || "No email set"}</p>
                    <button class="edit-btn" on:click={startEdit}>
                        ✏️ Edit Profile
                    </button>
                </div>
            {:else}
                <div class="profile-info edit-mode">
                    <div class="form-group">
                        <label>Name</label>
                        <input
                            type="text"
                            bind:value={editName}
                            placeholder="Your name"
                        />
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            bind:value={editEmail}
                            placeholder="your@email.com"
                        />
                    </div>
                    <div class="edit-actions">
                        <button class="save-btn" on:click={saveProfile}>
                            💾 Save
                        </button>
                        <button class="cancel-btn" on:click={cancelEdit}>
                            Cancel
                        </button>
                    </div>
                </div>
            {/if}

            <div class="stats-row">
                <div class="stat">
                    <div class="stat-value">{profile.stats.total_workouts}</div>
                    <div class="stat-label">Workouts</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{profile.stats.current_streak}</div>
                    <div class="stat-label">Streak</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{profile.stats.days_active}</div>
                    <div class="stat-label">Days Active</div>
                </div>
            </div>
        </div>

        <!-- Settings Section -->
        <div class="settings-card">
            <h2 class="section-title">⚙️ Settings</h2>

            <div class="setting-item">
                <div class="setting-info">
                    <h3>Notifications</h3>
                    <p>Get workout reminders and achievements</p>
                </div>
                <label class="toggle-switch">
                    <input
                        type="checkbox"
                        checked={profile.preferences.notifications_enabled}
                        on:change={(e) =>
                            updatePreferences({
                                notifications_enabled: e.currentTarget.checked,
                            })}
                    />
                    <span class="slider"></span>
                </label>
            </div>

            <div class="setting-item">
                <div class="setting-info">
                    <h3>Units</h3>
                    <p>Choose measurement system</p>
                </div>
                <div class="radio-group">
                    <label class="radio-option">
                        <input
                            type="radio"
                            name="units"
                            value="metric"
                            checked={profile.preferences.units === "metric"}
                            on:change={() =>
                                updatePreferences({ units: "metric" })}
                        />
                        <span>Metric (kg, cm)</span>
                    </label>
                    <label class="radio-option">
                        <input
                            type="radio"
                            name="units"
                            value="imperial"
                            checked={profile.preferences.units === "imperial"}
                            on:change={() =>
                                updatePreferences({ units: "imperial" })}
                        />
                        <span>Imperial (lbs, ft)</span>
                    </label>
                </div>
            </div>
        </div>

        <!-- Achievements Section -->
        <div class="achievements-card">
            <div class="achievements-header">
                <h2 class="section-title">🏆 Achievements</h2>
                <button class="view-all-btn" on:click={() => goto("/progress")}>
                    View All →
                </button>
            </div>

            {#if loadingAchievements}
                <p class="loading-text">Loading achievements...</p>
            {:else if achievements && achievements.unlocked && achievements.unlocked.length > 0}
                <div class="achievements-grid">
                    {#each achievements.unlocked.slice(0, 6) as achievement}
                        <div
                            class="achievement-badge unlocked"
                            title={achievement.name}
                        >
                            <span class="achievement-icon"
                                >{achievement.icon}</span
                            >
                            <span class="achievement-name"
                                >{achievement.name}</span
                            >
                        </div>
                    {/each}
                </div>
                {#if achievements.unlocked.length > 6}
                    <p class="achievement-count">
                        +{achievements.unlocked.length - 6} more achievements
                    </p>
                {/if}
            {:else}
                <p class="no-achievements">
                    No achievements yet. Start working out to unlock them!
                </p>
            {/if}
        </div>

        <!-- Account Actions -->
        <div class="account-card">
            <h2 class="section-title">Account</h2>
            
            <div class="account-links">
                <button class="menu-item-btn" on:click={() => goto('/profile/bookings')}>
                    <span class="icon">🗓️</span>
                    <span class="label">My Consultations</span>
                    <span class="arrow">→</span>
                </button>
                
                <button class="logout-btn" on:click={handleLogout}>
                    🚪 Logout
                </button>
            </div>
            <p class="coming-soon-text">More account features coming soon</p>
        </div>
    {/if}
</div>

<style>
    .profile-page {
        padding: 2rem 1.5rem;
        max-width: 600px;
        margin: 0 auto;
        padding-bottom: 6rem;
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
        font-size: 0.875rem;
    }

    /* Loading & Error States */
    .loading-state,
    .error-state {
        text-align: center;
        padding: 3rem 2rem;
        background-color: var(--bg-card);
        border-radius: 1rem;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top-color: var(--primary);
        border-radius: 50%;
        margin: 0 auto 1rem;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .retry-btn {
        margin-top: 1rem;
        padding: 0.5rem 1.5rem;
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 0.5rem;
        cursor: pointer;
        font-weight: 600;
    }

    /* Profile Card */
    .profile-card {
        background-color: var(--bg-card);
        border-radius: 1rem;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .avatar-section {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .avatar {
        width: 100px;
        height: 100px;
        margin: 0 auto 1rem;
        background: linear-gradient(135deg, var(--primary) 0%, #2563eb 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 2rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .avatar-initials {
        user-select: none;
    }

    .avatar-note {
        margin-top: 0.5rem;
    }

    .coming-soon-badge {
        font-size: 0.75rem;
        color: var(--text-secondary);
        opacity: 0.8;
        margin: 0;
    }

    .profile-info {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .profile-info h2 {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
        color: var(--text-primary);
    }

    .email {
        color: var(--text-secondary);
        margin-bottom: 1rem;
        font-size: 0.875rem;
    }

    .edit-btn {
        padding: 0.5rem 1.5rem;
        background-color: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 0.5rem;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .edit-btn:hover {
        background-color: rgba(255, 255, 255, 0.15);
    }

    /* Edit Mode */
    .edit-mode {
        text-align: left;
    }

    .form-group {
        margin-bottom: 1rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 600;
    }

    .form-group input {
        width: 100%;
        padding: 0.75rem;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        color: var(--text-primary);
        font-size: 1rem;
    }

    .form-group input:focus {
        outline: none;
        border-color: var(--primary);
    }

    .edit-actions {
        display: flex;
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .save-btn,
    .cancel-btn {
        flex: 1;
        padding: 0.75rem;
        border: none;
        border-radius: 0.5rem;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .save-btn {
        background-color: var(--primary);
        color: white;
    }

    .cancel-btn {
        background-color: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
    }

    /* Stats Row */
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
        color: var(--text-primary);
    }

    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
    }

    /* Settings Card */
    .settings-card {
        background-color: var(--bg-card);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: var(--text-primary);
    }

    .setting-item {
        margin-bottom: 2rem;
    }

    .setting-item:last-child {
        margin-bottom: 0;
    }

    .setting-info {
        margin-bottom: 1rem;
    }

    .setting-info h3 {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: var(--text-primary);
    }

    .setting-info p {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* Toggle Switch */
    .toggle-switch {
        position: relative;
        display: inline-block;
        width: 50px;
        height: 26px;
    }

    .toggle-switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(255, 255, 255, 0.2);
        transition: 0.3s;
        border-radius: 26px;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 20px;
        width: 20px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: 0.3s;
        border-radius: 50%;
    }

    input:checked + .slider {
        background-color: var(--primary);
    }

    input:checked + .slider:before {
        transform: translateX(24px);
    }

    /* Radio Group */
    .radio-group {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .radio-option {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .radio-option:hover {
        background-color: rgba(255, 255, 255, 0.08);
    }

    .radio-option input {
        margin-right: 0.75rem;
        cursor: pointer;
    }

    .radio-option input:checked + span {
        color: var(--primary);
        font-weight: 600;
    }

    /* Achievements Card */
    .achievements-card {
        background-color: var(--bg-card);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .achievements-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    .view-all-btn {
        padding: 0.5rem 1rem;
        background-color: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 0.5rem;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .view-all-btn:hover {
        background-color: rgba(255, 255, 255, 0.15);
    }

    .achievements-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }

    .achievement-badge {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s;
    }

    .achievement-badge.unlocked {
        border-color: var(--accent-green);
        background-color: rgba(16, 185, 129, 0.1);
    }

    .achievement-icon {
        font-size: 2rem;
        display: block;
        margin-bottom: 0.5rem;
    }

    .achievement-name {
        font-size: 0.75rem;
        color: var(--text-secondary);
        display: block;
    }

    .achievement-count {
        text-align: center;
        margin-top: 1rem;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    .no-achievements,
    .loading-text {
        text-align: center;
        color: var(--text-secondary);
        padding: 2rem 0;
    }

    /* Account Card */
    .account-card {
        background-color: var(--bg-card);
        border-radius: 1rem;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .logout-btn {
        width: 100%;
        padding: 0.75rem;
        background-color: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 0.5rem;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.2s;
    }

    .logout-btn:hover {
        background-color: rgba(239, 68, 68, 0.2);
    }

    .account-links {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .menu-item-btn {
        display: flex;
        align-items: center;
        width: 100%;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.75rem;
        color: white;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }

    .menu-item-btn:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: var(--primary);
    }

    .menu-item-btn .icon {
        font-size: 1.25rem;
        margin-right: 1rem;
    }

    .menu-item-btn .label {
        flex: 1;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .menu-item-btn .arrow {
        color: var(--text-secondary);
        opacity: 0.5;
    }

    .coming-soon-text {
        text-align: center;
        margin-top: 1rem;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    @media (max-width: 640px) {
        .profile-page {
            padding: 1.5rem 1rem;
        }

        .achievements-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
</style>
