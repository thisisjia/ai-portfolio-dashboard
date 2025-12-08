"""Update database with new resume data from resume_docs/resume.json"""

import sqlite3
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Database path - check multiple locations
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

def clear_existing_data(conn):
    """Clear all existing resume data."""
    cursor = conn.cursor()

    print("🗑️  Clearing existing data...")

    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # Clear tables that exist
    for table in ["projects", "skills", "work_experience", "education", "tools_used", "publications"]:
        if table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  ✓ Cleared {table}")

    conn.commit()
    print("✅ Old data cleared")

def populate_projects(conn, resume_data):
    """Populate projects table."""
    cursor = conn.cursor()

    print("\n📁 Adding projects...")
    for project in resume_data.get("projects", []):
        cursor.execute("""
            INSERT INTO projects (name, description, tech_stack, github_url, impact_score, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.get("name"),
            project.get("description"),
            json.dumps(project.get("tech_stack", project.get("technologies", []))),
            project.get("github_url", ""),
            project.get("impact_score", 8),
            project.get("start_date", "2024-01-01"),
            project.get("end_date", "2025-12-31"),
            project.get("status", "completed")
        ))
        print(f"  ✓ {project.get('name')}")

    conn.commit()

def populate_skills(conn, resume_data):
    """Populate skills table."""
    cursor = conn.cursor()

    print("\n🛠️  Adding skills...")
    skills_data = resume_data.get("skills", {})

    # Process each category
    for category, items in skills_data.items():
        # Map category names
        category_map = {
            "languages": "Programming Languages",
            "frameworks": "Frameworks & Libraries",
            "databases": "Databases",
            "cloud": "Cloud & Infrastructure",
            "tools": "Tools & DevOps",
            "frontend": "Frontend Development",
            "ai_ml": "AI/ML & Data Science"
        }

        display_category = category_map.get(category, category.title())

        if isinstance(items, list):
            for skill in items:
                cursor.execute("""
                    INSERT INTO skills (category, skill_name, proficiency_level, years_experience, last_used)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    display_category,
                    skill,
                    4,  # Default proficiency
                    2.0,  # Default years
                    "2025-01-01"
                ))

        print(f"  ✓ {display_category}: {len(items) if isinstance(items, list) else 0} skills")

    conn.commit()

def populate_work_experience(conn, resume_data):
    """Populate work experience table."""
    cursor = conn.cursor()

    print("\n💼 Adding work experience...")
    for exp in resume_data.get("experience", []):
        # Parse dates
        duration = exp.get("duration", "")
        if " - " in duration:
            start_date, end_date = duration.split(" - ")
            start_date = start_date.strip()
            end_date = end_date.strip()

            # Convert to date format
            if start_date.isdigit():
                start_date = f"{start_date}-01-01"

            if end_date == "Present":
                end_date = None
            elif end_date.isdigit():
                end_date = f"{end_date}-12-31"
        else:
            start_date = "2024-01-01"
            end_date = None

        cursor.execute("""
            INSERT INTO work_experience (company, position, start_date, end_date, description, achievements, tech_stack)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            exp.get("company"),
            exp.get("role"),
            start_date,
            end_date,
            f"{exp.get('location', '')} | {exp.get('duration', '')}",
            json.dumps(exp.get("highlights", [])),
            json.dumps([])  # Tech stack extracted from highlights if needed
        ))
        print(f"  ✓ {exp.get('company')} - {exp.get('role')}")

    conn.commit()

def populate_education(conn, resume_data):
    """Populate education table."""
    cursor = conn.cursor()

    print("\n🎓 Adding education...")
    for edu in resume_data.get("education", []):
        year = edu.get("year", "2020")

        cursor.execute("""
            INSERT INTO education (institution, degree, field_of_study, start_date, end_date, gpa, achievements)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            edu.get("school"),
            edu.get("degree"),
            edu.get("details", ""),
            f"{int(year)-3}-01-01" if year.isdigit() else "2010-01-01",
            f"{year}-12-31" if year.isdigit() else "2020-12-31",
            None,
            json.dumps(edu.get("coursework", []))
        ))
        print(f"  ✓ {edu.get('degree')} - {edu.get('school')}")

    conn.commit()

def populate_publications(conn, resume_data):
    """Populate publications table."""
    cursor = conn.cursor()

    # Check if table exists, create if not
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT NOT NULL,
            journal TEXT NOT NULL,
            year INTEGER NOT NULL,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("\n📚 Adding publications...")
    for pub in resume_data.get("publications", []):
        cursor.execute("""
            INSERT INTO publications (title, authors, journal, year, link)
            VALUES (?, ?, ?, ?, ?)
        """, (
            pub.get("title"),
            pub.get("authors"),
            pub.get("journal"),
            int(pub.get("year", 2020)),
            pub.get("link", "")
        ))
        print(f"  ✓ {pub.get('title')[:60]}...")

    conn.commit()

def main():
    """Main function to update database."""
    print("=" * 60)
    print("📝 Resume Database Update Script")
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
        # Clear existing data
        clear_existing_data(conn)

        # Populate new data
        populate_projects(conn, resume_data)
        populate_skills(conn, resume_data)
        populate_work_experience(conn, resume_data)
        populate_education(conn, resume_data)
        populate_publications(conn, resume_data)

        print("\n" + "=" * 60)
        print("✅ Database updated successfully!")
        print("=" * 60)

        # Show summary
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        projects_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM skills")
        skills_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM work_experience")
        work_exp_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM education")
        education_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM publications")
        publications_count = cursor.fetchone()[0]

        print(f"\n📊 Summary:")
        print(f"  • Projects: {projects_count}")
        print(f"  • Skills: {skills_count}")
        print(f"  • Work Experience: {work_exp_count}")
        print(f"  • Education: {education_count}")
        print(f"  • Publications: {publications_count}")
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
