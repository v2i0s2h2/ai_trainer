<script lang="ts">
	import { onMount } from 'svelte';
	import { dietStore } from '$lib/stores/diet';
	
	let showAddForm = false;
	let showEducation = true;
	let activeTab: 'tracking' | 'education' = 'tracking';
	
	// Form state
	let formData = {
		meal_name: 'Breakfast',
		food_item: '',
		protein: 0,
		carbs: 0,
		fats: 0,
		calories: 0,
		omega3: 0,
		magnesium: 0,
		vitamin_b1: 0,
		vitamin_d3: 0,
		zinc: 0,
		notes: ''
	};
	
	$: stats = $dietStore.stats;
	$: entries = $dietStore.entries;
	$: loading = $dietStore.loading;
	
	onMount(async () => {
		await dietStore.loadEntries();
		await dietStore.loadStats();
	});
	
	async function handleSubmit() {
		if (!formData.food_item.trim()) {
			alert('Please enter a food item');
			return;
		}
		
		await dietStore.addEntry(formData);
		
		// Reset form
		formData = {
			meal_name: 'Breakfast',
			food_item: '',
			protein: 0,
			carbs: 0,
			fats: 0,
			calories: 0,
			omega3: 0,
			magnesium: 0,
			vitamin_b1: 0,
			vitamin_d3: 0,
			zinc: 0,
			notes: ''
		};
		
		showAddForm = false;
	}
	
	async function deleteEntry(id: number) {
		if (confirm('Delete this entry?')) {
			await dietStore.deleteEntry(id);
		}
	}
	
	function getProteinProgress() {
		if (!stats || stats.protein_goal === 0) return 0;
		return Math.min((stats.total_protein / stats.protein_goal) * 100, 100);
	}
</script>

<svelte:head>
	<title>Diet & Nutrition - AI Trainer</title>
</svelte:head>

<div class="diet-page">
	<header class="page-header">
		<h1>🥗 Diet & Nutrition</h1>
		<p class="subtitle">Track your nutrition for lean, healthy aging</p>
	</header>
	
	<!-- Tabs -->
	<div class="tabs">
		<button 
			class="tab-btn"
			class:active={activeTab === 'tracking'}
			on:click={() => activeTab = 'tracking'}
		>
			📊 Tracking
		</button>
		<button 
			class="tab-btn"
			class:active={activeTab === 'education'}
			on:click={() => activeTab = 'education'}
		>
			📚 Learn
		</button>
	</div>
	
	{#if activeTab === 'tracking'}
		<!-- Daily Stats Card -->
		{#if stats}
			<div class="stats-card">
				<h3>Today's Nutrition</h3>
				
				<!-- Protein Progress -->
				<div class="progress-section">
					<div class="progress-header">
						<span>🥩 Protein</span>
						<span class="progress-value">
							{stats.total_protein.toFixed(1)}g / {stats.protein_goal.toFixed(0)}g
						</span>
					</div>
					<div class="progress-bar">
						<div 
							class="progress-fill"
							style="width: {getProteinProgress()}%"
						></div>
					</div>
				</div>
				
				<!-- Macros Grid -->
				<div class="macros-grid">
					<div class="macro-item">
						<span class="macro-label">🍞 Carbs</span>
						<span class="macro-value">{stats.total_carbs.toFixed(1)}g</span>
					</div>
					<div class="macro-item">
						<span class="macro-label">🧈 Fats</span>
						<span class="macro-value">{stats.total_fats.toFixed(1)}g</span>
					</div>
					<div class="macro-item">
						<span class="macro-label">🔥 Calories</span>
						<span class="macro-value">{stats.total_calories.toFixed(0)}</span>
					</div>
				</div>
				
				<!-- Micronutrients -->
				<div class="micro-section">
					<h4>Essential Micronutrients</h4>
					<div class="micro-grid">
						<div class="micro-item">
							<span>🐟 Omega-3</span>
							<span>{stats.total_omega3.toFixed(1)}mg</span>
						</div>
						<div class="micro-item">
							<span>⚡ Magnesium</span>
							<span>{stats.total_magnesium.toFixed(1)}mg</span>
						</div>
						<div class="micro-item">
							<span>🔋 B1 (Thiamine)</span>
							<span>{stats.total_vitamin_b1.toFixed(2)}mg</span>
						</div>
						<div class="micro-item">
							<span>☀️ Vitamin D3</span>
							<span>{stats.total_vitamin_d3.toFixed(0)}IU</span>
						</div>
						<div class="micro-item">
							<span>💪 Zinc</span>
							<span>{stats.total_zinc.toFixed(1)}mg</span>
						</div>
					</div>
				</div>
			</div>
		{/if}
		
		<!-- Add Entry Button -->
		<button class="add-btn" on:click={() => showAddForm = !showAddForm}>
			{showAddForm ? '✕ Cancel' : '+ Add Meal'}
		</button>
		
		<!-- Add Entry Form -->
		{#if showAddForm}
			<div class="form-card">
				<h3>Add Meal Entry</h3>
				
				<div class="form-group">
					<label>Meal</label>
					<select bind:value={formData.meal_name}>
						<option>Breakfast</option>
						<option>Lunch</option>
						<option>Dinner</option>
						<option>Snack</option>
					</select>
				</div>
				
				<div class="form-group">
					<label>Food Item</label>
					<input 
						type="text" 
						placeholder="e.g., 2 Eggs, Chicken Breast 200g"
						bind:value={formData.food_item}
					/>
				</div>
				
				<div class="form-row">
					<div class="form-group">
						<label>Protein (g)</label>
						<input type="number" step="0.1" bind:value={formData.protein} />
					</div>
					<div class="form-group">
						<label>Carbs (g)</label>
						<input type="number" step="0.1" bind:value={formData.carbs} />
					</div>
				</div>
				
				<div class="form-row">
					<div class="form-group">
						<label>Fats (g)</label>
						<input type="number" step="0.1" bind:value={formData.fats} />
					</div>
					<div class="form-group">
						<label>Calories</label>
						<input type="number" step="1" bind:value={formData.calories} />
					</div>
				</div>
				
				<div class="form-group">
					<label>Notes (optional)</label>
					<textarea 
						placeholder="Any additional notes..."
						bind:value={formData.notes}
						rows="2"
					></textarea>
				</div>
				
				<button class="submit-btn" on:click={handleSubmit}>
					Add Entry
				</button>
			</div>
		{/if}
		
		<!-- Entries List -->
		<div class="entries-section">
			<h3>Today's Meals ({entries.length})</h3>
			
			{#if entries.length === 0}
				<div class="empty-state">
					<p>No entries yet. Add your first meal!</p>
				</div>
			{:else}
				<div class="entries-list">
					{#each entries as entry}
						<div class="entry-card">
							<div class="entry-header">
								<span class="meal-badge">{entry.meal_name}</span>
								<button 
									class="delete-btn"
									on:click={() => deleteEntry(entry.id)}
								>
									✕
								</button>
							</div>
							<p class="food-item">{entry.food_item}</p>
							<div class="entry-macros">
								<span>🥩 {entry.protein}g</span>
								<span>🍞 {entry.carbs}g</span>
								<span>🧈 {entry.fats}g</span>
								<span>🔥 {entry.calories}cal</span>
							</div>
							{#if entry.notes}
								<p class="entry-notes">{entry.notes}</p>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{:else}
		<!-- Education Content -->
		<div class="education-content">
			<!-- Protein Section -->
			<section class="edu-section">
				<h2>🥩 Protein: The Foundation</h2>
				
				<div class="info-card">
					<h3>Age vs Protein Utilization</h3>
					<p>
						Jaise-jaise hum <strong>age</strong> karte hain, body ki ability to use protein for 
						<strong>recovery aur muscle building</strong> dheere-dheere <strong>kam hone lagti hai</strong>.
					</p>
					<p>
						Agar tum apni diet me <strong>enough protein nahi lete</strong>, to <strong>pepsin</strong> enzyme 
						(jo protein ko digest karta hai) <strong>kam active ho jaata hai</strong>. 
						Phir body protein ko effectively use nahi kar paati.
					</p>
				</div>
				
				<div class="info-card">
					<h3>Protein Goals by Age</h3>
					<div class="table-container">
						<table>
							<thead>
								<tr>
									<th>Age</th>
									<th>Target</th>
									<th>Reason</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td>20-30</td>
									<td>1.6g/kg</td>
									<td>Maintain muscle</td>
								</tr>
								<tr>
									<td>30-50</td>
									<td>1.8-2.0g/kg</td>
									<td>Preserve + build lean mass</td>
								</tr>
								<tr>
									<td>50+</td>
									<td>2.0-2.2g/kg</td>
									<td>Prevent muscle loss, stay anabolic</td>
								</tr>
							</tbody>
						</table>
					</div>
					<p class="tip">
						💡 <strong>Example:</strong> 70kg person → 126-154g protein daily
					</p>
				</div>
			</section>
			
			<!-- Anabolic vs Catabolic -->
			<section class="edu-section">
				<h2>⚡ Anabolic vs Catabolic</h2>
				
				<div class="info-card">
					<h3>Anabolic (Build-up Process)</h3>
					<p>
						<strong>Anabolic</strong> ka matlab hota hai <strong>body me kuch banana ya build karna</strong> — 
						jaise muscle banana, tissue repair karna.
					</p>
					<p>
						Jab tum <strong>protein-rich food</strong> lete ho (eggs, paneer, chicken) aur workout karte ho, 
						to <strong>leucine amino acid</strong> ek <strong>anabolic signal</strong> deta hai: 
						"Body! ab muscle build karne ka time hai 💪"
					</p>
				</div>
				
				<div class="info-card">
					<h3>Catabolic (Break-down Process)</h3>
					<p>
						Ye uska <strong>opposite</strong> hai — jab body tissues ya muscles ko todti hai energy ke liye.
					</p>
					<p>
						Ye hota hai jab tumhe <strong>protein kam mil raha ho</strong>, ya tum <strong>stress ya fasting</strong> me ho.
					</p>
				</div>
				
				<div class="info-card highlight">
					<h3>🎯 Goal: Stay Anabolic</h3>
					<p>
						Lean body weight banana ke liye, tumhe <strong>anabolic state</strong> me rehna chahiye — 
						matlab protein aur nutrients itne hone chahiye ke body muscle build kare, fat burn kare, 
						aur recover kare.
					</p>
				</div>
			</section>
			
			<!-- Protein to Muscle Gain -->
			<section class="edu-section">
				<h2>💪 Protein to Muscle: The Real Truth</h2>
				
				<div class="info-card highlight">
					<h3>🧪 How much muscle do you REALLY gain from 50g protein?</h3>
					<p>
						<strong>Direct and simple truth:</strong>
					</p>
					<ul class="truth-list">
						<li>👉 <strong>50 grams protein = NOT 50 grams muscle gain</strong></li>
						<li>👉 <strong>50g protein ⇒ approx 10–12g muscle potential</strong> (best-case)</li>
						<li>👉 <strong>Actual muscle added per day = 3–5 grams only</strong></li>
					</ul>
				</div>
				
				<div class="info-card">
					<h3>🧠 Why only 3–5 grams muscle?</h3>
					
					<h4>1️⃣ Protein does NOT convert 1:1 into muscle</h4>
					<p>
						Muscle = Water (~70%) + Protein (~20%) + Minerals + Glycogen
					</p>
					<p>
						Jab tum 50g protein khate ho, body <strong>digestion, repair, energy, enzymes, hormones</strong> me 
						bohot saara use kar leti hai. Muscle banane ke liye available protein <strong>kam hota hai</strong>.
					</p>
					
					<h4>2️⃣ Human body ki daily muscle-building LIMIT</h4>
					<p>
						Even if you eat 200g protein daily… Body ek din me <strong>3–5 grams hi new muscle fibers</strong> 
						bana sakti hai. Ye limit <strong>genetics, hormones, training intensity</strong> par depend karti hai.
					</p>
					
					<h4>3️⃣ Workout ke bina protein → muscle nahi banega</h4>
					<p>
						Protein sirf raw material hai. Muscle banane ke liye <strong>training stimulus</strong> zaroori hai.
					</p>
				</div>
				
				<div class="info-card">
					<h3>📊 Practical Calculation</h3>
					<p>
						Agar tum daily:
					</p>
					<ul>
						<li>✅ <strong>120g protein</strong></li>
						<li>✅ <strong>Good workout</strong></li>
						<li>✅ <strong>Good sleep</strong></li>
					</ul>
					<p>
						rakhte ho…
					</p>
					<ul>
						<li>👉 <strong>Monthly muscle gain</strong> ~ <strong>250–450 grams (¼ to ½ kg)</strong></li>
						<li>👉 <strong>Yearly</strong> ~ <strong>3–5 kg muscle</strong> (natural lifter ki maximum)</li>
					</ul>
				</div>
				
				<div class="info-card">
					<h3>🍳 Your Example: 50g Protein</h3>
					
					<div class="example-cases">
						<div class="case-item">
							<h4>Case A – No workout:</h4>
							<p>→ Muscle gain = <strong>almost zero</strong></p>
							<p>→ Body repair + basic functions = protein use ho jaata hai.</p>
						</div>
						
						<div class="case-item">
							<h4>Case B – Light workout:</h4>
							<p>→ Muscle gain = <strong>1–2 grams per day</strong></p>
						</div>
						
						<div class="case-item highlight">
							<h4>Case C – Strength Training (ideal):</h4>
							<p>→ Muscle gain = <strong>3–5 grams per day</strong></p>
						</div>
					</div>
				</div>
				
				<div class="info-card highlight">
					<h3>💪 Summary (Easy Hinglish)</h3>
					<ul class="summary-list">
						<li>✅ <strong>50g protein</strong> khane se <strong>50g muscle nahi</strong> banta</li>
						<li>✅ Body sirf <strong>3–5 grams muscle/day</strong> bana sakti hai</li>
						<li>✅ Baaki protein <strong>repair, digestion, enzymes</strong> me use hota hai</li>
						<li>✅ Muscle gain = <strong>training + protein + sleep</strong></li>
					</ul>
				</div>
			</section>
			
			<!-- Micronutrients -->
			<section class="edu-section">
				<h2>🧩 Essential Micronutrients</h2>
				
				<div class="nutrients-grid">
					<div class="nutrient-card">
						<h3>🐟 Omega-3 (EPA + DHA)</h3>
						<p><strong>1000-2000 mg/day</strong></p>
						<p>Fights inflammation, improves brain & heart health, joint lubrication</p>
						<p class="sources"><strong>Sources:</strong> Fish oil, flaxseed, chia seeds, walnuts</p>
					</div>
					
					<div class="nutrient-card">
						<h3>⚡ Magnesium</h3>
						<p><strong>300-400 mg/day</strong></p>
						<p>Muscle relaxation, sleep, nerve & heart function</p>
						<p class="sources"><strong>Sources:</strong> Bananas, dark chocolate, spinach, almonds</p>
					</div>
					
					<div class="nutrient-card">
						<h3>🔋 Vitamin B1 (Thiamine)</h3>
						<p><strong>1.2-1.5 mg/day</strong></p>
						<p>Energy production, focus, nervous system</p>
						<p class="sources"><strong>Sources:</strong> Whole grains, lentils, sunflower seeds</p>
					</div>
					
					<div class="nutrient-card">
						<h3>☀️ Vitamin D3</h3>
						<p><strong>2000 IU/day</strong></p>
						<p>Bone & immune health</p>
						<p class="sources"><strong>Sources:</strong> Sunlight ☀️, eggs, fish, supplements</p>
					</div>
					
					<div class="nutrient-card">
						<h3>💪 Zinc</h3>
						<p><strong>10-20 mg/day</strong></p>
						<p>Testosterone, immunity, wound healing</p>
						<p class="sources"><strong>Sources:</strong> Pumpkin seeds, meat, beans</p>
					</div>
				</div>
			</section>
			
			<!-- Food Sources -->
			<section class="edu-section">
				<h2>🌱 Food Sources: Veg & Non-Veg</h2>
				
				<div class="info-card">
					<h3>Complete Nutrition Guide</h3>
					<p>
						As you age, your goal should be to <strong>maintain lean muscle</strong>, 
						<strong>support recovery</strong>, and <strong>stay energetic</strong>.
					</p>
					<p>
						For that, you need both <strong>macronutrients (protein)</strong> and 
						<strong>micronutrients (vitamins & minerals)</strong> from 
						<strong>balanced food sources</strong>.
					</p>
				</div>
				
				<!-- Vegetarian Sources -->
				<div class="sources-section">
					<h3 class="section-title">🌱 Vegetarian Sources</h3>
					
					<div class="source-card">
						<h4>🫘 Black Chana (Kala Chana)</h4>
						<ul>
							<li>Rich in <strong>plant protein</strong> and <strong>fiber</strong></li>
							<li>Contains <strong>iron, magnesium, and vitamin B1</strong> (Thiamine) — supports energy production and muscle recovery</li>
							<li>Great for <strong>post-workout meals</strong> when mixed with sprouts or curd</li>
						</ul>
					</div>
					
					<div class="source-card">
						<h4>🌾 Flax Seeds</h4>
						<ul>
							<li>Excellent source of <strong>Omega-3 fatty acids (ALA form)</strong> — helps reduce inflammation and supports brain function</li>
							<li>Also provides <strong>fiber</strong> and <strong>magnesium</strong> for better digestion and muscle relaxation</li>
						</ul>
					</div>
					
					<div class="source-card">
						<h4>🌿 Moringa Leaves (Drumstick Leaves)</h4>
						<ul>
							<li>A <strong>superfood</strong> rich in <strong>vitamin A, C, calcium, iron, and plant protein</strong></li>
							<li>Helps in detoxification, supports the immune system, and improves stamina</li>
							<li>Natural anti-aging food due to its <strong>antioxidants</strong></li>
						</ul>
					</div>
					
					<div class="source-card">
						<h4>🥤 Wheatgrass Juice</h4>
						<ul>
							<li>Rich in <strong>chlorophyll</strong>, <strong>vitamin B complex</strong>, and <strong>magnesium oxide</strong></li>
							<li>Purifies blood, boosts energy levels, and helps in oxygen circulation</li>
							<li>Great for improving metabolism and keeping the body alkaline</li>
						</ul>
					</div>
					
					<div class="source-card">
						<h4>☀️ Sunlight</h4>
						<ul>
							<li>Natural source of <strong>Vitamin D3</strong></li>
							<li>Helps absorb <strong>calcium</strong> and maintain bone & muscle strength</li>
							<li>Just <strong>15–20 minutes of early morning sunlight</strong> daily can fulfill your Vitamin D requirement</li>
						</ul>
					</div>
					
					<div class="source-card">
						<h4>🥛 Milk & Milk Products</h4>
						<ul>
							<li>Rich in <strong>protein (casein + whey)</strong> and <strong>calcium</strong></li>
							<li>Also provides <strong>B vitamins</strong>, <strong>zinc</strong>, and <strong>leucine</strong>, the key amino acid for muscle building</li>
							<li>Helps you stay <strong>anabolic</strong> (muscle gain + recovery)</li>
						</ul>
					</div>
					
					<!-- Nutritious Roti Recipe -->
					<div class="recipe-card highlight">
						<h3>🍞 Nutritious Roti Recipe</h3>
						<p class="recipe-intro">
							Add all protein and nutrients to your daily routine by making this super-nutritious roti!
						</p>
						
						<div class="recipe-infographic">
							<img 
								src="/images/diet/nutritious-roti-recipe.png" 
								alt="Nutritious Roti Recipe - Ingredients: Powder Black Chana, Wheat Flour, Moringa Leaves, Powdered Flax Seed"
								class="roti-recipe-image"
							/>
						</div>
						
						<div class="recipe-steps">
							<h4>How to Make:</h4>
							<ol>
								<li>Take <strong>wheat flour</strong> as base</li>
								<li>Add <strong>powdered black chana</strong> (roasted & ground)</li>
								<li>Add <strong>roasted & powdered flax seeds</strong></li>
								<li>Add finely chopped or powdered <strong>moringa leaves</strong></li>
								<li>Mix all ingredients and make <strong>dough</strong></li>
								<li>Make <strong>roti</strong> as usual</li>
							</ol>
							<p class="recipe-tip">
								💡 This way, you get all the protein, Omega-3, vitamins, and minerals in your daily roti!
							</p>
						</div>
					</div>
				</div>
				
				<!-- Non-Vegetarian Sources -->
				<div class="sources-section">
					<h3 class="section-title">🍗 Non-Vegetarian Sources</h3>
					
					<div class="source-card">
						<h4>🥚 Eggs</h4>
						<ul>
							<li>Complete protein source with <strong>all essential amino acids</strong></li>
							<li>Rich in <strong>leucine</strong>, which triggers the <strong>anabolic muscle-building response</strong></li>
							<li>Also contains <strong>B12, choline, and Omega-3</strong> (if fortified)</li>
						</ul>
						<p class="tip-text">
							💡 <strong>Tip:</strong> 2–4 whole eggs daily (depending on activity level) are perfect for lean muscle
						</p>
					</div>
					
					<div class="source-card">
						<h4>🍖 Meat (Chicken, Fish, or Lean Red Meat)</h4>
						<ul>
							<li><strong>High-quality protein</strong> with <strong>heam iron</strong>, <strong>zinc</strong>, and <strong>B vitamins</strong></li>
							<li>Excellent for muscle recovery and strength</li>
							<li>Fish like salmon or sardines are rich in <strong>Omega-3 (EPA & DHA)</strong>, great for heart and brain</li>
						</ul>
						<p class="tip-text">
							💡 <strong>Tip:</strong> Prefer grilled or steamed — avoid deep-fried options
						</p>
					</div>
					
					<div class="source-card">
						<h4>💊 Supplements (Tablet or Powder Form)</h4>
						<ul>
							<li>For people who can't get enough nutrients from food alone</li>
							<li>Common supplements:
								<ul class="nested-list">
									<li><strong>Whey protein / Plant protein</strong> → Muscle growth</li>
									<li><strong>Fish oil / Omega-3 capsules</strong> → Anti-inflammation</li>
									<li><strong>Magnesium oxide tablets</strong> → Sleep & recovery</li>
									<li><strong>B-complex</strong> → Energy & nerve health</li>
								</ul>
							</li>
						</ul>
						<p class="tip-text">
							💡 <strong>Tip:</strong> Use supplements only to <strong>fill nutritional gaps</strong>, not as food replacements
						</p>
					</div>
				</div>
				
				<!-- Summary Table -->
				<div class="info-card highlight">
					<h3>🔄 Summary Table: Veg vs Non-Veg Sources</h3>
					<div class="table-container">
						<table class="comparison-table">
							<thead>
								<tr>
									<th>Nutrient</th>
									<th>Veg Sources</th>
									<th>Non-Veg / Supplement Sources</th>
									<th>Benefit</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td><strong>Protein</strong></td>
									<td>Black chana, milk, moringa</td>
									<td>Eggs, meat, whey</td>
									<td>Muscle building & recovery</td>
								</tr>
								<tr>
									<td><strong>Omega-3</strong></td>
									<td>Flax seeds</td>
									<td>Fish oil, salmon</td>
									<td>Brain & heart health</td>
								</tr>
								<tr>
									<td><strong>Magnesium</strong></td>
									<td>Wheatgrass, moringa, banana</td>
									<td>Magnesium oxide tablets</td>
									<td>Relaxation, better sleep</td>
								</tr>
								<tr>
									<td><strong>Vitamin B1 (Thiamine)</strong></td>
									<td>Black chana, wheatgrass</td>
									<td>Meat, eggs, B-complex tab</td>
									<td>Energy metabolism</td>
								</tr>
								<tr>
									<td><strong>Vitamin D3</strong></td>
									<td>Sunlight, fortified milk</td>
									<td>Fish, D3 supplement</td>
									<td>Bone & muscle strength</td>
								</tr>
								<tr>
									<td><strong>Zinc</strong></td>
									<td>Nuts, seeds, milk</td>
									<td>Meat, eggs</td>
									<td>Immunity & hormone balance</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</section>
			
			<!-- Lifestyle Tips -->
			<section class="edu-section">
				<h2>💧 Lifestyle Tips</h2>
				<div class="tips-grid">
					<div class="tip-card">✅ 7-8 hours sleep</div>
					<div class="tip-card">✅ 2-3 liters water daily</div>
					<div class="tip-card">✅ Walk/stretch daily (10-15 min after meals)</div>
					<div class="tip-card">✅ Strength training 3-5x week</div>
					<div class="tip-card">✅ Manage stress (deep breathing, meditation)</div>
				</div>
			</section>
		</div>
	{/if}
</div>

<style>
	.diet-page {
		padding: 2rem 1.5rem;
		max-width: 800px;
		margin: 0 auto;
		padding-bottom: 100px;
	}
	
	.page-header {
		text-align: center;
		margin-bottom: 2rem;
	}
	
	.page-header h1 {
		font-size: 2rem;
		margin-bottom: 0.5rem;
	}
	
	.subtitle {
		color: var(--text-secondary);
		font-size: 0.9rem;
	}
	
	.tabs {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 2rem;
		background: var(--bg-card);
		padding: 0.5rem;
		border-radius: 0.75rem;
	}
	
	.tab-btn {
		flex: 1;
		padding: 0.75rem;
		background: transparent;
		border: none;
		border-radius: 0.5rem;
		color: var(--text-secondary);
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.tab-btn.active {
		background: var(--primary);
		color: white;
	}
	
	.stats-card {
		background: var(--bg-card);
		border-radius: 1rem;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
	}
	
	.stats-card h3 {
		margin-bottom: 1.5rem;
		font-size: 1.25rem;
	}
	
	.progress-section {
		margin-bottom: 1.5rem;
	}
	
	.progress-header {
		display: flex;
		justify-content: space-between;
		margin-bottom: 0.5rem;
		font-weight: 500;
	}
	
	.progress-value {
		color: var(--primary);
	}
	
	.progress-bar {
		height: 8px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 4px;
		overflow: hidden;
	}
	
	.progress-fill {
		height: 100%;
		background: var(--primary);
		transition: width 0.3s;
	}
	
	.macros-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
		margin-bottom: 1.5rem;
	}
	
	.macro-item {
		text-align: center;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
	}
	
	.macro-label {
		display: block;
		font-size: 0.875rem;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
	}
	
	.macro-value {
		display: block;
		font-size: 1.25rem;
		font-weight: 600;
	}
	
	.micro-section {
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	.micro-section h4 {
		margin-bottom: 1rem;
		font-size: 1rem;
	}
	
	.micro-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 0.75rem;
	}
	
	.micro-item {
		display: flex;
		justify-content: space-between;
		padding: 0.75rem;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		font-size: 0.875rem;
	}
	
	.add-btn {
		width: 100%;
		padding: 1rem;
		background: var(--primary);
		color: white;
		border: none;
		border-radius: 0.75rem;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		margin-bottom: 1.5rem;
		transition: opacity 0.2s;
	}
	
	.add-btn:hover {
		opacity: 0.9;
	}
	
	.form-card {
		background: var(--bg-card);
		border-radius: 1rem;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
	}
	
	.form-card h3 {
		margin-bottom: 1.5rem;
	}
	
	.form-group {
		margin-bottom: 1rem;
	}
	
	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
	}
	
	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: var(--text-primary);
		font-size: 1rem;
	}
	
	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}
	
	.submit-btn {
		width: 100%;
		padding: 0.75rem;
		background: var(--primary);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		cursor: pointer;
		margin-top: 1rem;
	}
	
	.entries-section {
		margin-top: 2rem;
	}
	
	.entries-section h3 {
		margin-bottom: 1rem;
	}
	
	.entries-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	
	.entry-card {
		background: var(--bg-card);
		border-radius: 0.75rem;
		padding: 1rem;
	}
	
	.entry-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}
	
	.meal-badge {
		background: var(--primary);
		color: white;
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		font-size: 0.75rem;
		font-weight: 600;
	}
	
	.delete-btn {
		background: transparent;
		border: none;
		color: var(--text-secondary);
		cursor: pointer;
		font-size: 1.25rem;
		padding: 0.25rem;
	}
	
	.food-item {
		font-weight: 500;
		margin-bottom: 0.75rem;
	}
	
	.entry-macros {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
		font-size: 0.875rem;
		color: var(--text-secondary);
	}
	
	.entry-notes {
		margin-top: 0.5rem;
		font-size: 0.875rem;
		color: var(--text-secondary);
		font-style: italic;
	}
	
	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--text-secondary);
	}
	
	/* Education Styles */
	.education-content {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}
	
	.edu-section {
		background: var(--bg-card);
		border-radius: 1rem;
		padding: 1.5rem;
	}
	
	.edu-section h2 {
		font-size: 1.5rem;
		margin-bottom: 1.5rem;
	}
	
	.info-card {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.75rem;
		padding: 1.25rem;
		margin-bottom: 1rem;
	}
	
	.info-card h3 {
		font-size: 1.125rem;
		margin-bottom: 0.75rem;
		color: var(--primary);
	}
	
	.info-card p {
		margin-bottom: 0.75rem;
		line-height: 1.6;
	}
	
	.info-card.highlight {
		background: rgba(var(--primary-rgb, 255, 100, 50), 0.1);
		border: 1px solid var(--primary);
	}
	
	.info-card h4 {
		font-size: 1rem;
		font-weight: 600;
		margin-top: 1rem;
		margin-bottom: 0.5rem;
		color: var(--text-primary);
	}
	
	.truth-list,
	.summary-list {
		list-style: none;
		padding-left: 0;
	}
	
	.truth-list li,
	.summary-list li {
		margin-bottom: 0.75rem;
		padding-left: 0.5rem;
		line-height: 1.6;
	}
	
	.example-cases {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-top: 1rem;
	}
	
	.case-item {
		padding: 1rem;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 0.5rem;
		border-left: 3px solid var(--primary);
	}
	
	.case-item.highlight {
		background: rgba(16, 185, 129, 0.1);
		border-left-color: var(--accent-green);
	}
	
	.case-item h4 {
		margin-top: 0;
		margin-bottom: 0.5rem;
		color: var(--primary);
	}
	
	.case-item p {
		margin: 0.25rem 0;
	}
	
	.table-container {
		overflow-x: auto;
		margin: 1rem 0;
	}
	
	table {
		width: 100%;
		border-collapse: collapse;
	}
	
	th, td {
		padding: 0.75rem;
		text-align: left;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}
	
	th {
		font-weight: 600;
		color: var(--primary);
	}
	
	.tip {
		margin-top: 1rem;
		padding: 0.75rem;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		font-size: 0.875rem;
	}
	
	.nutrients-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1rem;
	}
	
	.nutrient-card {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.75rem;
		padding: 1.25rem;
	}
	
	.nutrient-card h3 {
		font-size: 1.125rem;
		margin-bottom: 0.75rem;
	}
	
	.nutrient-card p {
		margin-bottom: 0.5rem;
		line-height: 1.6;
	}
	
	.sources {
		font-size: 0.875rem;
		color: var(--text-secondary);
		margin-top: 0.75rem;
	}
	
	.tips-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}
	
	.tip-card {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.75rem;
		padding: 1rem;
		text-align: center;
		font-weight: 500;
	}
	
	.sources-section {
		margin-bottom: 2rem;
	}
	
	.section-title {
		font-size: 1.25rem;
		margin-bottom: 1rem;
		color: var(--primary);
	}
	
	.source-card {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.75rem;
		padding: 1.25rem;
		margin-bottom: 1rem;
	}
	
	.source-card h4 {
		font-size: 1.125rem;
		margin-bottom: 0.75rem;
	}
	
	.source-card ul {
		margin: 0.75rem 0;
		padding-left: 1.5rem;
		line-height: 1.8;
	}
	
	.source-card ul li {
		margin-bottom: 0.5rem;
	}
	
	.nested-list {
		margin-top: 0.5rem;
		margin-left: 1rem;
	}
	
	.recipe-card {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.75rem;
		padding: 1.5rem;
		margin-top: 1.5rem;
		border: 2px solid var(--primary);
	}
	
	.recipe-card h3 {
		font-size: 1.25rem;
		margin-bottom: 0.75rem;
		color: var(--primary);
	}
	
	.recipe-intro {
		margin-bottom: 1.5rem;
		font-size: 1rem;
		line-height: 1.6;
	}
	
	.recipe-infographic {
		position: relative;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 1rem;
		padding: 1rem;
		margin-bottom: 1.5rem;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	
	.roti-recipe-image {
		width: 100%;
		max-width: 600px;
		height: auto;
		border-radius: 0.75rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	}
	
	.recipe-steps {
		margin-top: 1.5rem;
	}
	
	.recipe-steps h4 {
		font-size: 1.125rem;
		margin-bottom: 1rem;
	}
	
	.recipe-steps ol {
		padding-left: 1.5rem;
		line-height: 2;
		margin-bottom: 1rem;
	}
	
	.recipe-steps li {
		margin-bottom: 0.5rem;
	}
	
	.recipe-tip {
		margin-top: 1rem;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		border-left: 3px solid var(--primary);
		font-size: 0.875rem;
	}
	
	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
	
	@media (max-width: 768px) {
		.recipe-infographic {
			padding: 0.5rem;
		}
		
		.roti-recipe-image {
			max-width: 100%;
		}
	}
	
	.comparison-table {
		font-size: 0.875rem;
	}
	
	.comparison-table th {
		background: rgba(255, 255, 255, 0.1);
		position: sticky;
		top: 0;
	}
	
	.comparison-table td {
		vertical-align: top;
		padding: 0.75rem 0.5rem;
	}
	
	.comparison-table td:first-child {
		font-weight: 600;
	}
	
	@media (max-width: 768px) {
		.comparison-table {
			font-size: 0.75rem;
		}
		
		.comparison-table th,
		.comparison-table td {
			padding: 0.5rem 0.25rem;
		}
	}
</style>

