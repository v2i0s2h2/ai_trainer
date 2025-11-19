"""
Add category column to achievements table
Migration script for existing database
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.database.db import engine, SessionLocal
from sqlalchemy import text

def add_category_column():
    """Add category column to achievements table if it doesn't exist"""
    
    db = SessionLocal()
    
    try:
        # Check if column exists using raw SQL
        result = db.execute(text("""
            SELECT COUNT(*) as cnt 
            FROM pragma_table_info('achievements') 
            WHERE name='category'
        """)).fetchone()
        
        if result and result[0] > 0:
            print("✅ Category column already exists in achievements table")
            return
        
        # Add category column with default value
        print("🔄 Adding category column to achievements table...")
        db.execute(text("""
            ALTER TABLE achievements 
            ADD COLUMN category TEXT DEFAULT 'basic'
        """))
        db.commit()
        print("✅ Category column added successfully!")
        
        # Update existing rows to have 'basic' category if NULL
        db.execute(text("""
            UPDATE achievements 
            SET category = 'basic' 
            WHERE category IS NULL
        """))
        db.commit()
        print("✅ Updated existing achievements with default category")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Adding category column to achievements table...\n")
    add_category_column()

