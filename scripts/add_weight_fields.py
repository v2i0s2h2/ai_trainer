"""
Migration script to add weight, sets_completed, and reps_per_set columns to workouts table
"""

import sqlite3
import sys
from pathlib import Path

# Get database path
DB_PATH = Path(__file__).parent.parent / "data" / "fitness.db"

print(f"🔧 Adding weight and sets/reps fields to workouts table...")
print(f"📁 Database: {DB_PATH}")

try:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(workouts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add weight_lbs column if it doesn't exist
    if 'weight_lbs' not in columns:
        print("🔄 Adding weight_lbs column...")
        cursor.execute("""
            ALTER TABLE workouts 
            ADD COLUMN weight_lbs REAL
        """)
        conn.commit()
        print("✅ weight_lbs column added!")
    else:
        print("✅ weight_lbs column already exists")
    
    # Add sets_completed column if it doesn't exist
    if 'sets_completed' not in columns:
        print("🔄 Adding sets_completed column...")
        cursor.execute("""
            ALTER TABLE workouts 
            ADD COLUMN sets_completed INTEGER DEFAULT 2
        """)
        conn.commit()
        print("✅ sets_completed column added!")
    else:
        print("✅ sets_completed column already exists")
    
    # Add reps_per_set column if it doesn't exist
    if 'reps_per_set' not in columns:
        print("🔄 Adding reps_per_set column...")
        cursor.execute("""
            ALTER TABLE workouts 
            ADD COLUMN reps_per_set INTEGER DEFAULT 15
        """)
        conn.commit()
        print("✅ reps_per_set column added!")
    else:
        print("✅ reps_per_set column already exists")
    
    # Update existing rows with default values
    cursor.execute("""
        UPDATE workouts 
        SET sets_completed = 2 
        WHERE sets_completed IS NULL
    """)
    cursor.execute("""
        UPDATE workouts 
        SET reps_per_set = 15 
        WHERE reps_per_set IS NULL
    """)
    conn.commit()
    print("✅ Updated existing workouts with default values")
    
    conn.close()
    print("\n✅ Migration complete! Weight tracking is now enabled.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


