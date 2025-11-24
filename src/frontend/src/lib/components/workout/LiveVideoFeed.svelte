<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { workoutStore } from '$lib/stores/workout';

	export let cameraMode = 'auto'; // 'auto' (server) or 'client' (mobile)

	$: frame = $workoutStore.currentFrame;
	$: isConnected = $workoutStore.isConnected;

	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let stream: MediaStream | null = null;
	let captureInterval: number | null = null;

	async function startClientCamera() {
		if (cameraMode !== 'client') return;

		try {
			console.log('Starting client camera...');
			stream = await navigator.mediaDevices.getUserMedia({
				video: {
					facingMode: 'user',
					width: { ideal: 640 },
					height: { ideal: 480 }
				}
			});
			
			if (videoElement) {
				videoElement.srcObject = stream;
				await videoElement.play();
			}

			// Start capturing and sending frames
			if (captureInterval) clearInterval(captureInterval);
			
			captureInterval = window.setInterval(() => {
				if (!isConnected) return;
				
				if (canvasElement && videoElement && videoElement.readyState === 4) {
					canvasElement.width = videoElement.videoWidth;
					canvasElement.height = videoElement.videoHeight;
					
					const ctx = canvasElement.getContext('2d');
					if (ctx) {
						// Mirror the local video
						ctx.translate(canvasElement.width, 0);
						ctx.scale(-1, 1);
						ctx.drawImage(videoElement, 0, 0);
						
						// Convert to base64 and send
						// Use lower quality (0.6) to reduce latency over WebSocket
						const imageData = canvasElement.toDataURL('image/jpeg', 0.6);
						workoutStore.sendFrame(imageData);
					}
				}
			}, 100); // 10fps
		} catch (err) {
			console.error("Error accessing camera:", err);
			alert("Could not access camera. Please allow camera permissions.");
		}
	}

	function stopClientCamera() {
		if (stream) {
			stream.getTracks().forEach(track => track.stop());
			stream = null;
		}
		if (captureInterval) {
			clearInterval(captureInterval);
			captureInterval = null;
		}
	}

	// React to connection state and camera mode
	$: if (isConnected && cameraMode === 'client') {
		startClientCamera();
	} else {
		stopClientCamera();
	}

	onDestroy(() => {
		stopClientCamera();
	});
</script>

<div class="video-container">
	{#if !isConnected}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Connecting to {cameraMode === 'client' ? 'server' : 'camera'}...</p>
		</div>
	{:else}
		<!-- Display processed frame from server (has skeleton overlay) -->
		{#if frame?.image}
			<img 
				src={frame.image} 
				alt="Workout feed" 
				class="video-frame"
			/>
		{:else}
			<div class="loading-state">
				<div class="spinner"></div>
				<p>Waiting for video stream...</p>
			</div>
		{/if}
		
		<!-- Hidden video element for capture -->
		<video 
			bind:this={videoElement}
			playsinline
			muted
			style="display: none;"
		></video>
		
		<!-- Hidden canvas for processing -->
		<canvas 
			bind:this={canvasElement}
			style="display: none;"
		></canvas>
	{/if}
</div>

<style>
	.video-container {
		position: relative;
		width: 100%;
		aspect-ratio: 16 / 9;
		background-color: #000;
		border-radius: 1rem;
		overflow: hidden;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.video-frame {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		color: white;
	}
	
	.loading-state p {
		font-size: 1rem;
		opacity: 0.8;
	}
	
	.spinner {
		width: 48px;
		height: 48px;
		border: 4px solid rgba(255, 255, 255, 0.1);
		border-top-color: var(--primary);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>

