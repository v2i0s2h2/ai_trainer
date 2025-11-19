<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { workoutStore } from '$lib/stores/workout';
	import LiveVideoFeed from '$lib/components/workout/LiveVideoFeed.svelte';
	import RepCounter from '$lib/components/workout/RepCounter.svelte';
	import WorkoutControls from '$lib/components/workout/WorkoutControls.svelte';
	
	$: exercise = $page.params.exercise;
	$: error = $workoutStore.error;
	
	let exerciseName = '';
	let exerciseData: any = null;
	let loading = true;
	let cameras: any[] = [];
	let selectedCamera = "auto"; // "auto" means auto-detect external webcam
	let showCameraSetup = true; // Show camera setup guidance before workout starts
	
	onMount(async () => {
		try {
			// Fetch exercise details
			const res = await fetch(`/api/exercises/${exercise}`);
			if (res.ok) {
				exerciseData = await res.json();
				exerciseName = exerciseData.name;
			} else {
				exerciseName = exercise.charAt(0).toUpperCase() + exercise.slice(1);
			}
			
			// Fetch available cameras
			const camRes = await fetch('/api/cameras');
			if (camRes.ok) {
				const camData = await camRes.json();
				cameras = camData.cameras || [];
				console.log('Available cameras:', cameras);
			}
		} catch (err) {
			console.error('Failed to load exercise:', err);
			exerciseName = exercise.charAt(0).toUpperCase() + exercise.slice(1);
		}
		
		// Don't auto-connect if camera setup is showing
		// User will start workout after reading camera setup
		loading = false;
	});
	
	function changeCamera(cameraId: string) {
		selectedCamera = cameraId;
		if (!showCameraSetup) {
			workoutStore.disconnect();
			setTimeout(() => {
				workoutStore.connect(exercise, selectedCamera);
			}, 300);
		}
	}
	
	function startWorkout() {
		showCameraSetup = false;
		setTimeout(() => {
			workoutStore.connect(exercise, selectedCamera);
		}, 300);
	}
	
	onDestroy(() => {
		workoutStore.disconnect();
	});
</script>

<svelte:head>
	<title>{exerciseName} Workout - AI Trainer</title>
</svelte:head>

<div class="workout-page">
	{#if error}
		<div class="error-banner">
			<div class="error-content">
				<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
				</svg>
				<span>{error}</span>
			</div>
			<button class="retry-btn" on:click={() => workoutStore.connect(exercise)}>
				Retry
			</button>
		</div>
	{/if}
	
	{#if exerciseData}
		<div class="exercise-info-banner">
			<div class="info-content">
				<div class="info-section">
					<h3>{exerciseData.name}</h3>
					{#if exerciseData.target_muscles && exerciseData.target_muscles.length > 0}
						<div class="target-muscles">
							<span class="label">Target Muscles:</span>
							<span class="muscles">{exerciseData.target_muscles.join(', ')}</span>
						</div>
					{/if}
				</div>
				<div class="action-buttons">
					{#if cameras.length > 1}
						<div class="camera-selector">
							<label for="camera-select">📹 Camera:</label>
							<select 
								id="camera-select"
								bind:value={selectedCamera}
								on:change={() => changeCamera(selectedCamera)}
								class="camera-select"
							>
								<option value="auto">Auto (External Webcam)</option>
								{#each cameras as cam}
									<option value={cam.index.toString()}>
										Camera {cam.index} {cam.index === 0 ? '(Laptop)' : '(External)'}
									</option>
								{/each}
							</select>
						</div>
					{/if}
					{#if exerciseData.youtube_link}
						<a 
							href={exerciseData.youtube_link} 
							target="_blank" 
							rel="noopener noreferrer"
							class="youtube-link-btn"
						>
							<svg fill="currentColor" viewBox="0 0 24 24" width="20" height="20">
								<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
							</svg>
							Watch Tutorial
						</a>
					{/if}
				</div>
			</div>
		</div>
	{/if}
	
	{#if showCameraSetup && exerciseData?.camera_position}
		<div class="camera-setup-overlay">
			<div class="camera-setup-card">
				<div class="setup-header">
					<h2>📹 Camera Setup Guide</h2>
					<p class="setup-subtitle">Position your camera correctly for best results</p>
				</div>
				
				<div class="setup-content">
					<!-- Visual Diagram -->
					<div class="camera-diagram">
						<div class="diagram-container">
							<div class="person-icon">🧍</div>
							<div class="angle-indicator">
								{#if exerciseData.camera_position.angle.includes('Side')}
									<div class="camera-icon-large side-camera">📹</div>
									<span class="angle-text">90°</span>
									<div class="angle-line side-view"></div>
								{:else if exerciseData.camera_position.angle.includes('Front')}
									<div class="camera-icon-large front-camera">📹</div>
									<span class="angle-text">0°</span>
									<div class="angle-line front-view"></div>
								{:else if exerciseData.camera_position.angle.includes('45')}
									<div class="camera-icon-large angle-45-camera">📹</div>
									<span class="angle-text">45°</span>
									<div class="angle-line angle-45"></div>
								{/if}
							</div>
							<div class="distance-label">{exerciseData.camera_position.distance}</div>
							<div class="height-label">{exerciseData.camera_position.height}</div>
						</div>
					</div>
					
					<!-- Instructions -->
					<div class="setup-instructions">
						<div class="instruction-item">
							<span class="instruction-icon">📏</span>
							<div class="instruction-content">
								<strong>Distance:</strong> {exerciseData.camera_position.distance}
							</div>
						</div>
						<div class="instruction-item">
							<span class="instruction-icon">📐</span>
							<div class="instruction-content">
								<strong>Angle:</strong> {exerciseData.camera_position.angle}
							</div>
						</div>
						<div class="instruction-item">
							<span class="instruction-icon">⬆️</span>
							<div class="instruction-content">
								<strong>Height:</strong> {exerciseData.camera_position.height}
							</div>
						</div>
					</div>
					
					<!-- Tips -->
					{#if exerciseData.camera_position.tips && exerciseData.camera_position.tips.length > 0}
						<div class="setup-tips">
							<h4>💡 Tips:</h4>
							<ul>
								{#each exerciseData.camera_position.tips as tip}
									<li>{tip}</li>
								{/each}
							</ul>
						</div>
					{/if}
					
					<!-- Required Equipment -->
					{#if exerciseData.equipment && exerciseData.equipment.length > 0}
						<div class="equipment-section">
							<h4>🛒 Required Equipment:</h4>
							<div class="equipment-list">
								{#each exerciseData.equipment as item}
									<div class="equipment-item" class:optional={!item.required}>
										<div class="equipment-content">
											{#if item.image}
												<div class="equipment-image-wrapper">
													<img src={item.image} alt={item.name} class="equipment-image" />
												</div>
											{/if}
											<div class="equipment-details">
												<div class="equipment-header">
													<span class="equipment-icon">{item.required ? '✅' : '⚪'}</span>
													<span class="equipment-name">{item.name}</span>
													{#if !item.required}
														<span class="optional-badge">Optional</span>
													{/if}
												</div>
												{#if item.description}
													<div class="equipment-description">{item.description}</div>
												{/if}
											</div>
										</div>
									</div>
								{/each}
							</div>
							<div class="equipment-note">
								💡 <strong>Need equipment?</strong> Check out the Equipment Library for recommended suppliers.
							</div>
						</div>
					{/if}
				</div>
				
				<div class="setup-actions">
					<button class="start-workout-btn" on:click={startWorkout}>
						Got it! Start Workout
					</button>
				</div>
			</div>
		</div>
	{/if}
	
	<div class="video-section">
		<div class="video-wrapper">
			<LiveVideoFeed />
			<RepCounter />
		</div>
	</div>
	
	<WorkoutControls {exerciseName} />
</div>

<style>
	.workout-page {
		min-height: 100vh;
		background-color: var(--bg-primary);
		padding: 0;
		padding-bottom: 120px; /* Space for controls */
	}
	
	.error-banner {
		background: rgba(239, 68, 68, 0.2);
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: 0;
		padding: 1rem 1.5rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}
	
	.error-content {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: #EF4444;
		flex: 1;
	}
	
	.error-content svg {
		flex-shrink: 0;
	}
	
	.error-content span {
		font-size: 0.875rem;
		font-weight: 500;
	}
	
	.retry-btn {
		background: rgba(239, 68, 68, 0.2);
		color: #EF4444;
		border: 1px solid rgba(239, 68, 68, 0.3);
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.retry-btn:hover {
		background: rgba(239, 68, 68, 0.3);
	}
	
	.exercise-info-banner {
		background: var(--bg-card);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding: 1rem 1.5rem;
	}
	
	.info-content {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
	}
	
	.action-buttons {
		display: flex;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
	}
	
	.camera-selector {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	
	.camera-selector label {
		font-size: 0.875rem;
		color: var(--text-secondary);
		font-weight: 500;
	}
	
	.camera-select {
		padding: 0.5rem 0.75rem;
		background-color: var(--bg-card);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: var(--text-primary);
		font-size: 0.875rem;
		cursor: pointer;
		transition: border-color 0.2s;
	}
	
	.camera-select:hover {
		border-color: rgba(255, 255, 255, 0.2);
	}
	
	.camera-select:focus {
		outline: none;
		border-color: var(--primary);
	}
	
	.info-section h3 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: var(--text-primary);
	}
	
	.target-muscles {
		font-size: 0.875rem;
		color: var(--text-secondary);
		display: flex;
		gap: 0.5rem;
		align-items: center;
	}
	
	.target-muscles .label {
		font-weight: 500;
		opacity: 0.8;
	}
	
	.target-muscles .muscles {
		opacity: 0.9;
	}
	
	.youtube-link-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: #ff0000;
		color: white;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		text-decoration: none;
		transition: background-color 0.2s, transform 0.2s;
		white-space: nowrap;
	}
	
	.youtube-link-btn:hover {
		background-color: #cc0000;
		transform: scale(1.05);
	}
	
	.youtube-link-btn svg {
		flex-shrink: 0;
	}
	
	.video-section {
		padding: 1rem;
		max-width: 1200px;
		margin: 0 auto;
	}
	
	.video-wrapper {
		position: relative;
		width: 100%;
		max-width: 900px;
		margin: 0 auto;
	}
	
	.camera-setup-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.85);
		backdrop-filter: blur(4px);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
		padding: 1rem;
	}
	
	.camera-setup-card {
		background: var(--bg-card);
		border-radius: 1.5rem;
		padding: 2rem;
		max-width: 600px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.setup-header {
		text-align: center;
		margin-bottom: 2rem;
	}
	
	.setup-header h2 {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--text-primary);
		margin-bottom: 0.5rem;
	}
	
	.setup-subtitle {
		color: var(--text-secondary);
		font-size: 0.875rem;
	}
	
	.setup-content {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}
	
	.camera-diagram {
		background: rgba(255, 255, 255, 0.03);
		border-radius: 1rem;
		padding: 2rem;
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 250px;
	}
	
	.diagram-container {
		position: relative;
		width: 100%;
		max-width: 400px;
		height: 250px;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	
	.person-icon {
		font-size: 4rem;
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		z-index: 2;
	}
	
	.camera-icon-large {
		font-size: 3rem;
		position: absolute;
		z-index: 3;
		animation: pulse-camera 2s infinite;
	}
	
	.camera-icon-large.side-camera {
		left: 10%;
		top: 50%;
		transform: translateY(-50%);
	}
	
	.camera-icon-large.front-camera {
		left: 50%;
		top: 10%;
		transform: translateX(-50%);
	}
	
	.camera-icon-large.angle-45-camera {
		left: 15%;
		top: 15%;
	}
	
	.angle-indicator {
		position: absolute;
		width: 100%;
		height: 100%;
		z-index: 1;
	}
	
	.angle-text {
		position: absolute;
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--primary);
		background: rgba(0, 0, 0, 0.5);
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
	}
	
	.angle-line {
		position: absolute;
		background: var(--primary);
		opacity: 0.6;
	}
	
	.angle-line.side-view {
		width: 2px;
		height: 80%;
		left: 20%;
		top: 10%;
	}
	
	.angle-line.front-view {
		width: 80%;
		height: 2px;
		left: 10%;
		top: 20%;
	}
	
	.angle-line.angle-45 {
		width: 2px;
		height: 60%;
		left: 25%;
		top: 20%;
		transform: rotate(45deg);
		transform-origin: top left;
	}
	
	.distance-label {
		position: absolute;
		bottom: 1rem;
		left: 50%;
		transform: translateX(-50%);
		font-size: 0.75rem;
		color: var(--text-secondary);
		background: rgba(0, 0, 0, 0.5);
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
	}
	
	.height-label {
		position: absolute;
		right: 1rem;
		top: 50%;
		transform: translateY(-50%);
		font-size: 0.75rem;
		color: var(--text-secondary);
		background: rgba(0, 0, 0, 0.5);
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
		writing-mode: vertical-rl;
		text-orientation: mixed;
	}
	
	.setup-instructions {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	
	.instruction-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 0.75rem;
		border-left: 3px solid var(--primary);
	}
	
	.instruction-icon {
		font-size: 1.5rem;
		flex-shrink: 0;
	}
	
	.instruction-content {
		flex: 1;
		color: var(--text-primary);
		font-size: 0.875rem;
		line-height: 1.5;
	}
	
	.instruction-content strong {
		color: var(--primary);
		margin-right: 0.5rem;
	}
	
	.setup-tips {
		background: rgba(255, 255, 255, 0.03);
		border-radius: 0.75rem;
		padding: 1.25rem;
	}
	
	.setup-tips h4 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.75rem;
	}
	
	.setup-tips ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	
	.setup-tips li {
		font-size: 0.875rem;
		color: var(--text-secondary);
		line-height: 1.6;
		padding-left: 1.5rem;
		position: relative;
	}
	
	.setup-tips li::before {
		content: "•";
		position: absolute;
		left: 0;
		color: var(--primary);
		font-weight: bold;
	}
	
	.equipment-section {
		background: rgba(255, 255, 255, 0.03);
		border-radius: 0.75rem;
		padding: 1.25rem;
		margin-top: 1rem;
		border-left: 3px solid var(--accent-orange);
	}
	
	.equipment-section h4 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 1rem;
	}
	
	.equipment-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}
	
	.equipment-item {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		padding: 0.75rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.equipment-item.optional {
		opacity: 0.8;
		border-color: rgba(255, 255, 255, 0.05);
	}
	
	.equipment-content {
		display: flex;
		gap: 0.75rem;
		align-items: flex-start;
	}
	
	.equipment-image-wrapper {
		flex-shrink: 0;
		width: 80px;
		height: 80px;
		border-radius: 0.5rem;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.equipment-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	
	.equipment-details {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	
	.equipment-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	
	.equipment-icon {
		font-size: 1rem;
		flex-shrink: 0;
	}
	
	.equipment-name {
		font-weight: 600;
		color: var(--text-primary);
		font-size: 0.875rem;
		flex: 1;
	}
	
	.optional-badge {
		font-size: 0.7rem;
		padding: 0.125rem 0.5rem;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 0.25rem;
		color: var(--text-secondary);
	}
	
	.equipment-description {
		font-size: 0.75rem;
		color: var(--text-secondary);
		line-height: 1.4;
	}
	
	.equipment-link {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		font-size: 0.75rem;
		color: var(--primary);
		text-decoration: none;
		padding: 0.375rem 0.75rem;
		background: rgba(255, 100, 50, 0.1);
		border: 1px solid rgba(255, 100, 50, 0.2);
		border-radius: 0.375rem;
		transition: all 0.2s;
		width: fit-content;
	}
	
	.equipment-link:hover {
		background: rgba(255, 100, 50, 0.2);
		border-color: rgba(255, 100, 50, 0.3);
		color: var(--primary-hover, #ff6b35);
	}
	
	.equipment-link svg {
		flex-shrink: 0;
	}
	
	.equipment-note {
		font-size: 0.75rem;
		color: var(--text-secondary);
		line-height: 1.5;
		padding-top: 0.75rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.equipment-note strong {
		color: var(--text-primary);
	}
	
	.setup-actions {
		margin-top: 2rem;
		display: flex;
		justify-content: center;
	}
	
	.start-workout-btn {
		background: var(--primary);
		color: white;
		border: none;
		padding: 1rem 2rem;
		border-radius: 0.75rem;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 4px 12px rgba(255, 100, 50, 0.3);
	}
	
	.start-workout-btn:hover {
		background: var(--primary-hover, #ff6b35);
		transform: translateY(-2px);
		box-shadow: 0 6px 16px rgba(255, 100, 50, 0.4);
	}
	
	.start-workout-btn:active {
		transform: translateY(0);
	}
	
	@keyframes pulse-camera {
		0%, 100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.7;
			transform: scale(1.1);
		}
	}
	
	@media (max-width: 640px) {
		.video-section {
			padding: 0.5rem;
		}
		
		.workout-page {
			padding-bottom: 140px;
		}
		
		.camera-setup-card {
			padding: 1.5rem;
			max-height: 95vh;
		}
		
		.setup-header h2 {
			font-size: 1.5rem;
		}
		
		.camera-diagram {
			padding: 1.5rem;
			min-height: 200px;
		}
		
		.person-icon {
			font-size: 3rem;
		}
		
		.camera-icon-large {
			font-size: 2.5rem;
		}
	}
</style>

