"""
Simple script to add category column using direct SQLite connection
"""

import sqlite3
import sys
from pathlib import Path

# Get database path
DB_PATH = Path(__file__).parent.parent / "data" / "fitness.db"

print(f"🔧 Adding category column to achievements table...")
print(f"📁 Database: {DB_PATH}")

try:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(achievements)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'category' in columns:
        print("✅ Category column already exists!")
    else:
        print("🔄 Adding category column...")
        cursor.execute("""
            ALTER TABLE achievements 
            ADD COLUMN category TEXT DEFAULT 'basic'
        """)
        conn.commit()
        print("✅ Category column added successfully!")
        
        # Update existing rows
        cursor.execute("""
            UPDATE achievements 
            SET category = 'basic' 
            WHERE category IS NULL
        """)
        conn.commit()
        print("✅ Updated existing achievements")
    
    conn.close()
    print("\n✅ Done! Now you can run seed_achievements.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



