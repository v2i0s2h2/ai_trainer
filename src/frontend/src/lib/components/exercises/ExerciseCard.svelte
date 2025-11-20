<script lang="ts">
	import Badge from '$lib/components/ui/Badge.svelte';
	import { getEquipmentImage } from '$lib/utils/equipment';
	
	export let exercise: {
		id: string;
		name: string;
		category: string;
		exercise_type?: string;
		duration: number;
		sets: number;
		reps: number;
		difficulty: 'beginner' | 'intermediate' | 'advanced';
		target_muscles?: string[];
		youtube_link?: string;
		equipment?: Array<{
			name: string;
			required: boolean;
			description?: string;
			image?: string;
		}>;
		camera_position?: {
			distance: string;
			angle: string;
			height: string;
			tips: string[];
		};
	};
	
	const categoryColors: Record<string, string> = {
		legs: 'var(--accent-orange)',
		chest: 'var(--primary)',
		back: 'var(--accent-purple)',
		shoulders: 'var(--accent-green)',
		arms: 'var(--accent-pink)',
		core: 'var(--accent-yellow)'
	};
	
	$: categoryColor = categoryColors[exercise.category] || 'var(--primary)';
</script>

<a href="/workout/{exercise.id}" class="exercise-card" style="--category-color: {categoryColor}">
	<div class="card-content">
		<div class="exercise-info">
			<h3 class="exercise-name">{exercise.name}</h3>
			<div class="exercise-meta">
				<span class="meta-item">⏱️ {exercise.duration} min</span>
				<span class="meta-item">{exercise.sets} × {exercise.reps}</span>
			</div>
			{#if exercise.target_muscles && exercise.target_muscles.length > 0}
				<div class="target-muscles">
					<span class="muscles-label">Target: </span>
					<span class="muscles-list">{exercise.target_muscles.slice(0, 2).join(', ')}{#if exercise.target_muscles.length > 2}...{/if}</span>
				</div>
			{/if}
			{#if exercise.camera_position}
				<div class="camera-position-hint">
					<span class="camera-icon">📹</span>
					<span class="camera-text">{exercise.camera_position.angle} • {exercise.camera_position.distance}</span>
				</div>
			{/if}
			{#if exercise.equipment && exercise.equipment.length > 0 && exercise.exercise_type !== 'advanced'}
				<div class="equipment-preview">
					<div class="equipment-items">
						{#each exercise.equipment.slice(0, 3) as item}
							<div class="equipment-item-mini" title={item.name}>
								<img 
									src={item.image || getEquipmentImage(item.name)} 
									alt={item.name}
									on:error={(e) => {
										e.currentTarget.src = '/images/equipments/dumbbells.jpg';
									}}
								/>
							</div>
						{/each}
						{#if exercise.equipment.length > 3}
							<div class="equipment-more">+{exercise.equipment.length - 3}</div>
						{/if}
					</div>
				</div>
			{/if}
		</div>
		<div class="card-actions">
			<Badge variant={exercise.difficulty === 'beginner' ? 'success' : exercise.difficulty === 'intermediate' ? 'warning' : 'error'} size="sm">
				{exercise.difficulty}
			</Badge>
			{#if exercise.youtube_link}
				<a 
					href={exercise.youtube_link} 
					target="_blank" 
					rel="noopener noreferrer"
					class="youtube-btn"
					on:click|stopPropagation
					on:click|preventDefault
				>
					<svg fill="currentColor" viewBox="0 0 24 24" width="16" height="16">
						<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
					</svg>
					Tutorial
				</a>
			{/if}
		</div>
	</div>
</a>

<style>
	.exercise-card {
		background-color: var(--bg-card);
		border-radius: 1rem;
		padding: 1.5rem;
		text-decoration: none;
		color: inherit;
		transition: transform 0.2s, box-shadow 0.2s;
		border-left: 4px solid var(--category-color);
		display: block;
	}
	
	.exercise-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
		background-color: var(--bg-card-hover);
	}
	
	.card-content {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
	}
	
	.exercise-info {
		flex: 1;
	}
	
	.exercise-name {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: var(--text-primary);
	}
	
	.exercise-meta {
		display: flex;
		gap: 1rem;
		font-size: 0.875rem;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
	}
	
	.meta-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}
	
	.target-muscles {
		font-size: 0.75rem;
		color: var(--text-secondary);
		margin-top: 0.5rem;
		opacity: 0.8;
	}
	
	.muscles-label {
		font-weight: 500;
	}
	
	.muscles-list {
		opacity: 0.9;
	}
	
	.camera-position-hint {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		font-size: 0.7rem;
		color: var(--text-secondary);
		margin-top: 0.5rem;
		opacity: 0.85;
	}
	
	.camera-icon {
		font-size: 0.875rem;
	}
	
	.camera-text {
		font-weight: 500;
	}
	
	.equipment-preview {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.75rem;
		padding-top: 0.75rem;
		border-top: 1px solid rgba(255, 255, 255, 0.05);
	}
	
	.equipment-icon {
		font-size: 0.875rem;
		flex-shrink: 0;
	}
	
	.equipment-items {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		flex: 1;
	}
	
	.equipment-item-mini {
		width: 28px;
		height: 28px;
		border-radius: 0.375rem;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
		flex-shrink: 0;
	}
	
	.equipment-item-mini img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	
	.equipment-more {
		font-size: 0.7rem;
		color: var(--text-secondary);
		font-weight: 600;
		padding: 0.25rem 0.5rem;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.25rem;
	}
	
	.card-actions {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.5rem;
	}
	
	.youtube-btn {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem 0.75rem;
		background-color: #ff0000;
		color: white;
		border-radius: 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		text-decoration: none;
		transition: background-color 0.2s, transform 0.2s;
	}
	
	.youtube-btn:hover {
		background-color: #cc0000;
		transform: scale(1.05);
	}
	
	.youtube-btn svg {
		flex-shrink: 0;
	}
</style>

