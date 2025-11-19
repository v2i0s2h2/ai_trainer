<script lang="ts">
	import { onMount } from 'svelte';
	import { getEquipmentImage, getEquipmentLink } from '$lib/utils/equipment';
	
	interface EquipmentItem {
		name: string;
		required: boolean;
		description?: string;
		image?: string;
		link?: string;
	}
	
	interface Exercise {
		id: string;
		name: string;
		exercise_type: string;
		equipment?: EquipmentItem[];
	}
	
	let allExercises: Exercise[] = [];
	let loading = true;
	let searchQuery = '';
	
	// Consolidate equipment items to match available images (7 unique types)
	function consolidateEquipmentName(name: string): string {
		const lower = name.toLowerCase();
		
		// Group all dumbbell variations
		if (lower.includes('dumbbell')) {
			return 'Dumbbells';
		}
		
		// Group all ankle weight variations
		if (lower.includes('ankle weight')) {
			return 'Ankle Weights';
		}
		
		// Group pad/towel variations (using gel-pad image)
		if (lower.includes('pad') || lower.includes('towel')) {
			return 'Pad or Towel';
		}
		
		// Yoga Block (separate from pad)
		if (lower.includes('yoga block')) {
			return 'Yoga Block';
		}
		
		// Group exercise mat variations (using gel-pad as placeholder)
		if (lower.includes('mat') || lower.includes('soft surface')) {
			return 'Exercise Mat';
		}
		
		// Group medicine ball/football (only one using exercise-ball)
		if (lower.includes('medicine ball') || lower.includes('football')) {
			return 'Medicine Ball';
		}
		
		// Exercise Bands
		if (lower.includes('band')) {
			return 'Exercise Bands';
		}
		
		// Bench
		if (lower.includes('bench') || lower.includes('chair')) {
			return 'Bench';
		}
		
		// Keep others as is
		return name;
	}
	
	// Get unique equipment items from all exercises (consolidated to 7 types)
	$: uniqueEquipment = (() => {
		const equipmentMap = new Map<string, EquipmentItem>();
		
		allExercises.forEach(exercise => {
			if (exercise.equipment) {
				exercise.equipment.forEach(item => {
					// Skip "None (Bodyweight)" items
					if (item.name.toLowerCase().includes('none') || item.name.toLowerCase().includes('bodyweight')) {
						return;
					}
					
					// Consolidate equipment name
					const consolidatedName = consolidateEquipmentName(item.name);
					const key = consolidatedName.toLowerCase();
					
					if (!equipmentMap.has(key)) {
						equipmentMap.set(key, {
							name: consolidatedName,
							required: item.required,
							description: item.description || `Used in various exercises`,
							image: getEquipmentImage(consolidatedName),
							link: getEquipmentLink(consolidatedName)
						});
					} else {
						// If any instance is required, mark as required
						const existing = equipmentMap.get(key)!;
						if (item.required && !existing.required) {
							existing.required = true;
						}
					}
				});
			}
		});
		
		return Array.from(equipmentMap.values());
	})();
	
	$: filteredEquipment = uniqueEquipment.filter(item => {
		if (!searchQuery.trim()) return true;
		const query = searchQuery.toLowerCase();
		return item.name.toLowerCase().includes(query) ||
		       (item.description && item.description.toLowerCase().includes(query));
	});
	
	onMount(async () => {
		try {
			const res = await fetch('/api/exercises');
			if (res.ok) {
				allExercises = await res.json();
			}
		} catch (err) {
			console.error('Failed to load exercises:', err);
		} finally {
			loading = false;
		}
	});
	
	// Get exercises that use this equipment
	function getExercisesUsingEquipment(equipmentName: string): Exercise[] {
		return allExercises.filter(ex => 
			ex.equipment?.some(eq => eq.name.toLowerCase() === equipmentName.toLowerCase())
		);
	}
</script>

<div class="equipment-container">
	<header class="page-header">
		<h1>🛒 Equipment Store</h1>
		<p class="subtitle">All equipment needed for your workouts</p>
	</header>
	
	<!-- Search Bar -->
	<div class="search-section">
		<div class="search-bar">
			<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
			</svg>
			<input
				type="text"
				placeholder="Search equipment..."
				bind:value={searchQuery}
				class="search-input"
			/>
			{#if searchQuery}
				<button class="clear-btn" on:click={() => searchQuery = ''}>
					<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			{/if}
		</div>
	</div>
	
	<!-- Equipment List -->
	{#if loading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Loading equipment...</p>
		</div>
	{:else if filteredEquipment.length === 0}
		<div class="empty-state">
			<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="48" height="48">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
			</svg>
			<p>No equipment found</p>
		</div>
	{:else}
		<div class="equipment-grid">
			{#each filteredEquipment as item (item.name)}
				<div class="equipment-card" class:optional={!item.required}>
					<div class="equipment-image-wrapper">
						<img 
							src={item.image || getEquipmentImage(item.name)} 
							alt={item.name}
							class="equipment-image"
							on:error={(e) => {
								e.currentTarget.src = '/images/equipments/dumbbells.jpg';
							}}
						/>
						{#if !item.required}
							<div class="optional-badge-overlay">Optional</div>
						{/if}
					</div>
					
					<div class="equipment-content">
						<div class="equipment-header">
							<h3 class="equipment-name">{item.name}</h3>
							<div class="equipment-badges">
								{#if item.required}
									<span class="badge required">Required</span>
								{:else}
									<span class="badge optional">Optional</span>
								{/if}
							</div>
						</div>
						
						{#if item.description}
							<p class="equipment-description">{item.description}</p>
						{/if}
						
						<div class="equipment-usage">
							<span class="usage-label">Used in:</span>
							<span class="usage-count">
								{getExercisesUsingEquipment(item.name).length} 
								{getExercisesUsingEquipment(item.name).length === 1 ? 'exercise' : 'exercises'}
							</span>
						</div>
						
						<a 
							href={item.link || getEquipmentLink(item.name)}
							target="_blank"
							rel="noopener noreferrer"
							class="buy-button"
							on:click|stopPropagation
						>
							<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
							</svg>
							Buy Now
						</a>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.equipment-container {
		padding: 2rem 1.5rem;
		max-width: 1200px;
		margin: 0 auto;
		animation: fadeIn 0.3s ease-in;
	}
	
	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
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
		font-size: 1rem;
	}
	
	.search-section {
		margin-bottom: 2rem;
	}
	
	.search-bar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		padding: 0.75rem 1rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: border-color 0.2s;
	}
	
	.search-bar:focus-within {
		border-color: var(--primary);
	}
	
	.search-bar svg {
		color: var(--text-secondary);
		flex-shrink: 0;
	}
	
	.search-input {
		flex: 1;
		background: transparent;
		border: none;
		color: var(--text-primary);
		font-size: 1rem;
		outline: none;
	}
	
	.search-input::placeholder {
		color: var(--text-secondary);
	}
	
	.clear-btn {
		background: transparent;
		border: none;
		color: var(--text-secondary);
		cursor: pointer;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}
	
	.clear-btn:hover {
		color: var(--text-primary);
	}
	
	.equipment-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 1.5rem;
	}
	
	.equipment-card {
		background-color: var(--bg-card);
		border-radius: 1rem;
		overflow: hidden;
		transition: transform 0.2s, box-shadow 0.2s;
		border: 1px solid rgba(255, 255, 255, 0.1);
		display: flex;
		flex-direction: column;
	}
	
	.equipment-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
		background-color: var(--bg-card-hover);
	}
	
	.equipment-card.optional {
		opacity: 0.9;
	}
	
	.equipment-image-wrapper {
		position: relative;
		width: 100%;
		height: 200px;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.05);
	}
	
	.equipment-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	
	.optional-badge-overlay {
		position: absolute;
		top: 0.75rem;
		right: 0.75rem;
		background: rgba(0, 0, 0, 0.7);
		color: white;
		padding: 0.25rem 0.75rem;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 600;
		backdrop-filter: blur(4px);
	}
	
	.equipment-content {
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		flex: 1;
	}
	
	.equipment-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 0.75rem;
	}
	
	.equipment-name {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--text-primary);
		margin: 0;
		flex: 1;
	}
	
	.equipment-badges {
		display: flex;
		gap: 0.5rem;
	}
	
	.badge {
		font-size: 0.7rem;
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
		font-weight: 600;
		white-space: nowrap;
	}
	
	.badge.required {
		background: rgba(34, 197, 94, 0.2);
		color: #22c55e;
		border: 1px solid rgba(34, 197, 94, 0.3);
	}
	
	.badge.optional {
		background: rgba(255, 255, 255, 0.1);
		color: var(--text-secondary);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.equipment-description {
		font-size: 0.875rem;
		color: var(--text-secondary);
		line-height: 1.5;
		margin: 0;
	}
	
	.equipment-usage {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.75rem;
		color: var(--text-secondary);
		margin-top: auto;
	}
	
	.usage-label {
		opacity: 0.7;
	}
	
	.usage-count {
		font-weight: 600;
		color: var(--primary);
	}
	
	.buy-button {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: var(--primary);
		color: white;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		text-decoration: none;
		transition: all 0.2s;
		margin-top: 0.5rem;
	}
	
	.buy-button:hover {
		background: var(--primary-hover, #ff6b35);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(255, 100, 50, 0.3);
	}
	
	.buy-button svg {
		flex-shrink: 0;
	}
	
	.loading {
		text-align: center;
		padding: 3rem;
		color: var(--text-secondary);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
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
	
	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
		background-color: var(--bg-card);
		border-radius: 0.75rem;
		color: var(--text-secondary);
	}
	
	.empty-state svg {
		margin: 0 auto 1rem;
		opacity: 0.5;
	}
	
	@media (max-width: 640px) {
		.equipment-container {
			padding: 1.5rem 1rem;
		}
		
		.equipment-grid {
			grid-template-columns: 1fr;
		}
		
		.equipment-image-wrapper {
			height: 180px;
		}
	}
</style>

