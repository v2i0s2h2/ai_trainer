import sqlite3
import os
from pathlib import Path

# Path to the database
DB_PATH = Path("data/fitness.db")

def migrate():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}. Nothing to migrate.")
        return

    print(f"🔍 Checking database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if 'role' column exists in 'users' table
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role' not in columns:
            print("🚀 Adding 'role' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            print("✅ Successfully added 'role' column.")
        else:
            print("ℹ️  'role' column already exists in 'users' table.")

        conn.commit()
        print("🎉 Migration complete!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
