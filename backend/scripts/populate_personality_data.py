"""Populate personality, interests, achievements, and certifications from resume.json"""

import sqlite3
import json
import sys
from pathlib import Path

# Database path
project_root = Path(__file__).parent.parent.parent
backend_db = Path(__file__).parent.parent / "resume_dashboard.db"

if backend_db.exists():
    DB_PATH = backend_db
else:
    DB_PATH = project_root / "resume_dashboard.db"

RESUME_JSON_PATH = project_root / "resume_docs" / "resume.json"

def load_resume_data():
    """Load resume data from JSON file."""
    with open(RESUME_JSON_PATH, 'r') as f:
        return json.load(f)

def create_tables_if_not_exist(conn):
    """Create personality-related tables if they don't exist."""
    cursor = conn.cursor()

    print("📋 Creating tables if they don't exist...")

    # Personality table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personality_summary TEXT,
            work_style TEXT,
            strengths JSON,
            personal_values JSON,
            motivations JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Interests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interest_name TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Achievements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_text TEXT NOT NULL,
            category TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Certifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certification_name TEXT NOT NULL,
            issuer TEXT NOT NULL,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    print("✅ Tables ready")

def clear_personality_data(conn):
    """Clear existing personality data."""
    cursor = conn.cursor()

    print("\n🗑️  Clearing existing personality data...")

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # Clear personality tables
    for table in ["personality", "interests", "achievements", "certifications"]:
        if table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  ✓ Cleared {table}")

    conn.commit()
    print("✅ Old personality data cleared")

def populate_personality(conn, resume_data):
    """Populate personality table."""
    cursor = conn.cursor()

    print("\n🧠 Adding personality data...")
    personality = resume_data.get("personality", {})

    if personality:
        cursor.execute("""
            INSERT INTO personality (personality_summary, work_style, strengths, personal_values, motivations)
            VALUES (?, ?, ?, ?, ?)
        """, (
            personality.get("personality_summary", ""),
            personality.get("work_style", ""),
            json.dumps(personality.get("strengths", [])),
            json.dumps(personality.get("values", [])),
            json.dumps(personality.get("motivations", []))
        ))
        print(f"  ✓ Added personality profile")
        print(f"    - Strengths: {len(personality.get('strengths', []))}")
        print(f"    - Values: {len(personality.get('values', []))}")
        print(f"    - Motivations: {len(personality.get('motivations', []))}")

    conn.commit()

def populate_interests(conn, resume_data):
    """Populate interests table."""
    cursor = conn.cursor()

    print("\n💡 Adding interests...")
    interests = resume_data.get("interests", [])

    for interest in interests:
        cursor.execute("""
            INSERT INTO interests (interest_name, category)
            VALUES (?, ?)
        """, (interest, "Professional"))
        print(f"  ✓ {interest}")

    print(f"\n  Total: {len(interests)} interests")
    conn.commit()

def populate_achievements(conn, resume_data):
    """Populate achievements table."""
    cursor = conn.cursor()

    print("\n🏆 Adding achievements...")
    achievements = resume_data.get("achievements", [])

    for achievement in achievements:
        # Try to extract year if mentioned
        year = None
        if "2025" in achievement:
            year = 2025
        elif "2024" in achievement:
            year = 2024
        elif "2023" in achievement:
            year = 2023
        elif "2021" in achievement:
            year = 2021

        cursor.execute("""
            INSERT INTO achievements (achievement_text, category, year)
            VALUES (?, ?, ?)
        """, (achievement, "Career", year))
        print(f"  ✓ {achievement[:60]}...")

    print(f"\n  Total: {len(achievements)} achievements")
    conn.commit()

def populate_certifications(conn, resume_data):
    """Populate certifications table."""
    cursor = conn.cursor()

    print("\n📜 Adding certifications...")
    certifications = resume_data.get("certifications", [])

    for cert in certifications:
        cursor.execute("""
            INSERT INTO certifications (certification_name, issuer, year)
            VALUES (?, ?, ?)
        """, (
            cert.get("name"),
            cert.get("issuer"),
            int(cert.get("year", 2020)) if cert.get("year") else None
        ))
        print(f"  ✓ {cert.get('name')} - {cert.get('issuer')}")

    print(f"\n  Total: {len(certifications)} certifications")
    conn.commit()

def main():
    """Main function."""
    print("=" * 60)
    print("🎭 Personality Data Population Script")
    print("=" * 60)

    # Check if resume JSON exists
    if not RESUME_JSON_PATH.exists():
        print(f"❌ Error: Resume JSON not found at {RESUME_JSON_PATH}")
        sys.exit(1)

    # Load resume data
    print(f"\n📂 Loading resume data from: {RESUME_JSON_PATH}")
    resume_data = load_resume_data()
    print(f"✅ Resume data loaded: {resume_data.get('name')}")

    # Connect to database
    print(f"\n🔌 Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    try:
        # Create tables if needed
        create_tables_if_not_exist(conn)

        # Clear existing data
        clear_personality_data(conn)

        # Populate new data
        populate_personality(conn, resume_data)
        populate_interests(conn, resume_data)
        populate_achievements(conn, resume_data)
        populate_certifications(conn, resume_data)

        print("\n" + "=" * 60)
        print("✅ Personality data updated successfully!")
        print("=" * 60)

        # Show summary
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM personality")
        personality_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM interests")
        interests_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM achievements")
        achievements_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM certifications")
        certifications_count = cursor.fetchone()[0]

        print(f"\n📊 Summary:")
        print(f"  • Personality Profile: {personality_count}")
        print(f"  • Interests: {interests_count}")
        print(f"  • Achievements: {achievements_count}")
        print(f"  • Certifications: {certifications_count}")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
