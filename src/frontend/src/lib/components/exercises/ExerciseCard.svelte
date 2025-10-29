<script lang="ts">
	import Badge from '$lib/components/ui/Badge.svelte';
	
	export let exercise: {
		id: string;
		name: string;
		category: string;
		duration: number;
		sets: number;
		reps: number;
		difficulty: 'beginner' | 'intermediate' | 'advanced';
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
		</div>
		<Badge variant={exercise.difficulty === 'beginner' ? 'success' : exercise.difficulty === 'intermediate' ? 'warning' : 'error'} size="sm">
			{exercise.difficulty}
		</Badge>
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
	}
	
	.meta-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}
</style>

