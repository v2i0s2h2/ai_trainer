"""
Seed Achievements into Database
Categorized by: rehab, basic, advanced, lifting
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.database.db import SessionLocal, init_db, engine
from src.backend.database.models import Achievement
from sqlalchemy import text
import sqlite3

def ensure_category_column():
    """Ensure category column exists in achievements table"""
    # Use direct SQLite connection for ALTER TABLE
    db_path = str(Path(__file__).parent.parent / "data" / "fitness.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(achievements)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'category' not in columns:
            print("🔄 Adding category column to achievements table...")
            cursor.execute("""
                ALTER TABLE achievements 
                ADD COLUMN category TEXT DEFAULT 'basic'
            """)
            conn.commit()
            print("✅ Category column added!")
        else:
            print("✅ Category column already exists")
    except Exception as e:
        print(f"⚠️  Note: {e}")
    finally:
        conn.close()

def seed_achievements():
    """Seed achievements categorized by progression stages"""
    
    # Ensure category column exists first
    ensure_category_column()
    
    # Initialize database tables
    init_db()
    
    db = SessionLocal()
    
    try:
        # Define achievements by category
        achievements_data = [
            # REHAB Category
            {
                "id": "rehab-first-workout",
                "name": "Rehab Starter",
                "description": "Complete your first rehab workout",
                "icon": "🏥",
                "requirement": "Complete 1 rehab workout",
                "category": "rehab"
            },
            {
                "id": "rehab-10-reps",
                "name": "Rehab Progress",
                "description": "Complete 10 reps in rehab exercises",
                "icon": "💪",
                "requirement": "Complete 10 rehab reps",
                "category": "rehab"
            },
            {
                "id": "rehab-3-months",
                "name": "Rehab Graduate",
                "description": "Complete 3 months of rehab training",
                "icon": "🎓",
                "requirement": "Complete 3 months of rehab workouts",
                "category": "rehab"
            },
            
            # BASIC Category
            {
                "id": "basic-first-workout",
                "name": "First Steps",
                "description": "Complete your first basic workout",
                "icon": "👟",
                "requirement": "Complete 1 basic workout",
                "category": "basic"
            },
            {
                "id": "basic-50-reps",
                "name": "50 Reps Club",
                "description": "Complete 50 reps in basic exercises",
                "icon": "💪",
                "requirement": "Complete 50 basic reps",
                "category": "basic"
            },
            {
                "id": "basic-100-reps",
                "name": "100 Reps Club",
                "description": "Complete 100 reps in basic exercises",
                "icon": "🔥",
                "requirement": "Complete 100 basic reps",
                "category": "basic"
            },
            {
                "id": "basic-7-day-streak",
                "name": "7-Day Streak",
                "description": "Workout for 7 consecutive days",
                "icon": "🔥",
                "requirement": "Maintain 7-day workout streak",
                "category": "basic"
            },
            {
                "id": "basic-14-day-streak",
                "name": "14-Day Streak",
                "description": "Workout for 14 consecutive days",
                "icon": "🔥🔥",
                "requirement": "Maintain 14-day workout streak",
                "category": "basic"
            },
            {
                "id": "basic-30-day-streak",
                "name": "30-Day Streak",
                "description": "Workout for 30 consecutive days",
                "icon": "🔥🔥🔥",
                "requirement": "Maintain 30-day workout streak",
                "category": "basic"
            },
            {
                "id": "basic-early-bird",
                "name": "Early Bird",
                "description": "Complete workout before 8 AM",
                "icon": "🌅",
                "requirement": "Complete workout before 8 AM",
                "category": "basic"
            },
            {
                "id": "basic-week-warrior",
                "name": "Week Warrior",
                "description": "Complete 5 workouts in a week",
                "icon": "⚔️",
                "requirement": "Complete 5 workouts in one week",
                "category": "basic"
            },
            
            # ADVANCED Category
            {
                "id": "advanced-first-workout",
                "name": "Advanced Entry",
                "description": "Complete your first advanced workout",
                "icon": "⭐",
                "requirement": "Complete 1 advanced workout",
                "category": "advanced"
            },
            {
                "id": "advanced-200-reps",
                "name": "200 Reps Master",
                "description": "Complete 200 reps in advanced exercises",
                "icon": "💎",
                "requirement": "Complete 200 advanced reps",
                "category": "advanced"
            },
            {
                "id": "advanced-500-reps",
                "name": "500 Reps Elite",
                "description": "Complete 500 reps in advanced exercises",
                "icon": "👑",
                "requirement": "Complete 500 advanced reps",
                "category": "advanced"
            },
            {
                "id": "advanced-perfect-form",
                "name": "Perfect Form",
                "description": "Complete workout with 95%+ form accuracy",
                "icon": "✨",
                "requirement": "Achieve 95%+ form accuracy in workout",
                "category": "advanced"
            },
            {
                "id": "advanced-speed-demon",
                "name": "Speed Demon",
                "description": "Complete advanced workout in record time",
                "icon": "⚡",
                "requirement": "Complete advanced workout in record time",
                "category": "advanced"
            },
            
            # LIFTING Category
            {
                "id": "lifting-first-workout",
                "name": "Lifting Debut",
                "description": "Complete your first lifting workout",
                "icon": "🏋️",
                "requirement": "Complete 1 lifting workout",
                "category": "lifting"
            },
            {
                "id": "lifting-1000-reps",
                "name": "1000 Reps Legend",
                "description": "Complete 1000 reps in lifting exercises",
                "icon": "🏆",
                "requirement": "Complete 1000 lifting reps",
                "category": "lifting"
            },
            {
                "id": "lifting-consistency-king",
                "name": "Consistency King",
                "description": "Workout consistently for 60 days",
                "icon": "👑",
                "requirement": "Maintain 60-day workout consistency",
                "category": "lifting"
            },
            {
                "id": "lifting-power-hour",
                "name": "Power Hour",
                "description": "Complete 100 reps in one hour",
                "icon": "⚡",
                "requirement": "Complete 100 reps in one hour",
                "category": "lifting"
            },
            {
                "id": "lifting-iron-will",
                "name": "Iron Will",
                "description": "Complete 100 lifting workouts",
                "icon": "🦾",
                "requirement": "Complete 100 lifting workouts",
                "category": "lifting"
            },
            
            # WEIGHT MILESTONE Achievements (across all categories)
            {
                "id": "weight-5lbs",
                "name": "5 lbs Club",
                "description": "Reach 5 lbs weight on any exercise",
                "icon": "⚖️",
                "requirement": "Use 5 lbs weight in any workout",
                "category": "basic"
            },
            {
                "id": "weight-10lbs",
                "name": "10 lbs Milestone",
                "description": "Reach 10 lbs weight on any exercise",
                "icon": "💪",
                "requirement": "Use 10 lbs weight in any workout",
                "category": "basic"
            },
            {
                "id": "weight-15lbs",
                "name": "15 lbs Strong",
                "description": "Reach 15 lbs weight on any exercise",
                "icon": "🔥",
                "requirement": "Use 15 lbs weight in any workout",
                "category": "advanced"
            },
            {
                "id": "weight-20lbs",
                "name": "20 lbs Warrior",
                "description": "Reach 20 lbs weight on any exercise",
                "icon": "⚔️",
                "requirement": "Use 20 lbs weight in any workout",
                "category": "advanced"
            },
            {
                "id": "weight-25lbs",
                "name": "25 lbs Beast",
                "description": "Reach 25 lbs weight on any exercise",
                "icon": "🦾",
                "requirement": "Use 25 lbs weight in any workout",
                "category": "lifting"
            },
            {
                "id": "weight-30lbs",
                "name": "30 lbs Champion",
                "description": "Reach 30 lbs weight on any exercise",
                "icon": "👑",
                "requirement": "Use 30 lbs weight in any workout",
                "category": "lifting"
            },
            {
                "id": "weight-progression-master",
                "name": "Progression Master",
                "description": "Progress from 0 to 20+ lbs on any exercise",
                "icon": "📈",
                "requirement": "Progress from bodyweight/0lbs to 20+ lbs on any exercise",
                "category": "advanced"
            },
            
            # DIET Achievements
            {
                "id": "diet-first-entry",
                "name": "Nutrition Starter",
                "description": "Log your first meal",
                "icon": "🍎",
                "requirement": "Log your first meal entry",
                "category": "basic"
            },
            {
                "id": "diet-protein-goal-1",
                "name": "Protein Power",
                "description": "Meet daily protein goal once",
                "icon": "🥩",
                "requirement": "Meet daily protein goal (126g) once",
                "category": "basic"
            },
            {
                "id": "diet-protein-goal-7",
                "name": "Protein Week",
                "description": "Meet protein goal for 7 days",
                "icon": "💪",
                "requirement": "Meet daily protein goal for 7 consecutive days",
                "category": "advanced"
            },
            {
                "id": "diet-protein-goal-30",
                "name": "Protein Month",
                "description": "Meet protein goal for 30 days",
                "icon": "🏆",
                "requirement": "Meet daily protein goal for 30 days",
                "category": "lifting"
            },
            {
                "id": "diet-meal-logger",
                "name": "Meal Logger",
                "description": "Log 10 meals",
                "icon": "📝",
                "requirement": "Log 10 meal entries",
                "category": "basic"
            },
            {
                "id": "diet-consistency-7",
                "name": "7-Day Nutrition",
                "description": "Log meals for 7 consecutive days",
                "icon": "📊",
                "requirement": "Log meals for 7 consecutive days",
                "category": "basic"
            },
            {
                "id": "diet-consistency-30",
                "name": "30-Day Nutrition",
                "description": "Log meals for 30 days",
                "icon": "📈",
                "requirement": "Log meals for 30 days",
                "category": "advanced"
            },
            {
                "id": "diet-macro-balance",
                "name": "Macro Master",
                "description": "Balance protein, carbs, and fats for 7 days",
                "icon": "⚖️",
                "requirement": "Maintain balanced macros (protein/carbs/fats) for 7 days",
                "category": "advanced"
            },
            {
                "id": "diet-complete-nutrition",
                "name": "Complete Nutrition",
                "description": "Track all macros and micronutrients for 7 days",
                "icon": "🌟",
                "requirement": "Track complete nutrition (macros + micronutrients) for 7 days",
                "category": "lifting"
            }
        ]
        
        # Check if achievements already exist
        existing_count = db.query(Achievement).count()
        
        if existing_count > 0:
            print(f"⚠️  {existing_count} achievements already exist in database.")
            response = input("Do you want to add new achievements? (y/n): ")
            if response.lower() != 'y':
                print("Skipping seed...")
                return
        
        # Add achievements to database
        added_count = 0
        skipped_count = 0
        
        for ach_data in achievements_data:
            # Check if achievement already exists
            existing = db.query(Achievement).filter(Achievement.id == ach_data["id"]).first()
            
            if existing:
                print(f"⏭️  Skipping {ach_data['id']} (already exists)")
                skipped_count += 1
                continue
            
            achievement = Achievement(**ach_data)
            db.add(achievement)
            added_count += 1
            print(f"✅ Added: {ach_data['name']} ({ach_data['category']})")
        
        db.commit()
        
        print(f"\n🎉 Seeding complete!")
        print(f"   ✅ Added: {added_count} achievements")
        print(f"   ⏭️  Skipped: {skipped_count} achievements")
        print(f"   📊 Total: {db.query(Achievement).count()} achievements in database")
        
        # Show breakdown by category
        print(f"\n📋 Breakdown by category:")
        for category in ["rehab", "basic", "advanced", "lifting"]:
            count = db.query(Achievement).filter(Achievement.category == category).count()
            print(f"   {category.capitalize()}: {count} achievements")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding achievements: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding achievements into database...\n")
    seed_achievements()

