/**
 * Maps equipment names to local image files
 */
export function getEquipmentImage(equipmentName: string): string | null {
	const name = equipmentName.toLowerCase();
	
	// Map equipment names to image files (7 unique equipment types matching 7 images)
	const equipmentMap: Record<string, string> = {
		// 1. Ankle Weights
		'ankle weights': '/images/equipments/ankle-weights.jpg',
		'ankle weight': '/images/equipments/ankle-weights.jpg',
		
		// 2. Dumbbells
		'dumbbells': '/images/equipments/dumbbells.jpg',
		'dumbbell': '/images/equipments/dumbbells.jpg',
		
		// 3. Pad or Towel (using gel-pad image)
		'pad or towel': '/images/equipments/gel-pad.jpg',
		'pad': '/images/equipments/gel-pad.jpg',
		'towel': '/images/equipments/gel-pad.jpg',
		'2-inch pad': '/images/equipments/gel-pad.jpg',
		
		// 4. Yoga Block
		'yoga block': '/images/equipments/yoga-block.jpg',
		
		// 5. Exercise Mat (using yoga-block, NOT exercise-ball)
		'exercise mat': '/images/equipments/yoga-block.jpg',
		'mat': '/images/equipments/yoga-block.jpg',
		'soft surface': '/images/equipments/yoga-block.jpg',
		
		// 6. Medicine Ball (ONLY one using exercise-ball - no duplicates!)
		'medicine ball': '/images/equipments/exercise-ball.jpg',
		'football': '/images/equipments/exercise-ball.jpg',
		
		// 7. Exercise Bands
		'exercise bands': '/images/equipments/exercise-bands.jpg',
		'resistance bands': '/images/equipments/exercise-bands.jpg',
		'resistance band': '/images/equipments/exercise-bands.jpg',
		
		// 8. Bench
		'bench': '/images/equipments/bench.jpg',
		'exercise bench': '/images/equipments/bench.jpg',
		'weight bench': '/images/equipments/bench.jpg',
		'workout bench': '/images/equipments/bench.jpg',
		'bench or chair': '/images/equipments/bench.jpg',
		'chair': '/images/equipments/bench.jpg',
	};
	
	// Try exact match first
	if (equipmentMap[name]) {
		return equipmentMap[name];
	}
	
	// Try partial matches (check bench first to avoid conflicts)
	if (name.includes('bench')) {
		return '/images/equipments/bench.jpg';
	}
	
	// Try other partial matches
	for (const [key, value] of Object.entries(equipmentMap)) {
		if (name.includes(key) || key.includes(name)) {
			return value;
		}
	}
	
	// Default fallback
	return '/images/equipments/dumbbells.jpg';
}

/**
 * Get fake purchase link for equipment (temporary)
 */
export function getEquipmentLink(equipmentName: string): string {
	// Return fake links for now - will be replaced with real links later
	return `https://example.com/buy/${encodeURIComponent(equipmentName.toLowerCase().replace(/\s+/g, '-'))}`;
}

