#!/usr/bin/env python3
"""
Populate database with resume data from resume.json
This script clears existing data and imports fresh data from resume_docs/resume.json
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

def clear_database(conn):
    """Clear all existing data except token_access"""
    cursor = conn.cursor()

    # Tables to clear (keep token_access)
    tables_to_clear = [
        'skills', 'projects', 'work_experience', 'education',
        'publications', 'personality', 'interests', 'achievements',
        'certifications', 'tools_used', 'access_logs', 'chat_logs',
        'feedback_logs', 'api_interactions', 'query_demonstrations'
    ]

    print("Clearing existing data...")
    for table in tables_to_clear:
        cursor.execute(f'DELETE FROM {table}')
        print(f"  Cleared {table}")

    conn.commit()

def populate_skills(conn, resume_data):
    """Populate skills table from resume data"""
    cursor = conn.cursor()
    skills_data = resume_data.get('skills', {})

    # Map categories and their skills
    skill_categories = {
        'Programming Languages': skills_data.get('languages', []),
        'Frameworks & Libraries': skills_data.get('frameworks', []),
        'Databases': skills_data.get('databases', []),
        'Cloud & DevOps': skills_data.get('cloud', []),
        'Developer Tools': skills_data.get('tools', []),
        'Frontend Technologies': skills_data.get('frontend', []),
        'AI/ML Technologies': skills_data.get('ai_ml', [])
    }

    print("Populating skills...")
    skill_count = 0
    for category, skills in skill_categories.items():
        for skill in skills:
            cursor.execute('''
                INSERT INTO skills (category, skill_name, proficiency_level, years_experience, last_used)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, skill, 4, 2.0, '2025-01-01'))
            skill_count += 1

    print(f"  Inserted {skill_count} skills")
    conn.commit()

def populate_experience(conn, resume_data):
    """Populate work experience table"""
    cursor = conn.cursor()
    experiences = resume_data.get('experience', [])

    print("Populating work experience...")
    for exp in experiences:
        # Parse duration to get start/end dates
        duration = exp.get('duration', '')
        start_year = None
        end_year = None

        if ' - Present' in duration:
            start_year = duration.split(' - ')[0]
            end_year = None
        else:
            years = duration.split(' - ')
            start_year = years[0] if len(years) > 0 else None
            end_year = years[1] if len(years) > 1 else None

        # Convert years to dates
        start_date = f"{start_year}-01-01" if start_year and start_year.isdigit() else None
        end_date = f"{end_year}-12-31" if end_year and end_year.isdigit() else None

        cursor.execute('''
            INSERT INTO work_experience (company, position, start_date, end_date, description, achievements, tech_stack)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            exp.get('company'),
            exp.get('role'),
            start_date,
            end_date,
            exp.get('highlights', [''])[0] if exp.get('highlights') else None,
            json.dumps(exp.get('highlights', [])),
            json.dumps([])  # Tech stack would need to be extracted from highlights
        ))

    print(f"  Inserted {len(experiences)} work experiences")
    conn.commit()

def populate_education(conn, resume_data):
    """Populate education table"""
    cursor = conn.cursor()
    education = resume_data.get('education', [])

    print("Populating education...")
    for edu in education:
        # Parse year
        year = edu.get('year', '')
        if year and year.isdigit():
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
        else:
            start_date = None
            end_date = None

        cursor.execute('''
            INSERT INTO education (institution, degree, field_of_study, start_date, end_date, achievements)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            edu.get('school'),  # Use 'school' instead of 'institution'
            edu.get('degree'),
            edu.get('details', '').split(' | ')[1] if ' | ' in edu.get('details', '') else None,  # Extract field of study
            start_date,
            end_date,
            json.dumps(edu.get('coursework', []))  # Use coursework as achievements
        ))

    print(f"  Inserted {len(education)} education records")
    conn.commit()

def populate_projects(conn, resume_data):
    """Populate projects table from experience highlights"""
    cursor = conn.cursor()

    # Extract potential projects from experience highlights
    experiences = resume_data.get('experience', [])
    projects = []

    for exp in experiences:
        highlights = exp.get('highlights', [])
        for i, highlight in enumerate(highlights):
            # Create project entries from significant highlights
            if any(keyword in highlight.lower() for keyword in ['built', 'developed', 'created', 'implemented']):
                projects.append({
                    'name': f"{exp.get('company', 'Project')} - Feature {i+1}",
                    'description': highlight,
                    'tech_stack': extract_tech_from_highlight(highlight),
                    'status': 'completed',
                    'start_date': '2024-01-01',  # Would need better extraction
                    'end_date': '2024-12-31'
                })

    print("Populating projects...")
    for project in projects:
        cursor.execute('''
            INSERT INTO projects (name, description, tech_stack, status, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            project['name'],
            project['description'],
            json.dumps(project['tech_stack']),
            project['status'],
            project['start_date'],
            project['end_date']
        ))

    print(f"  Inserted {len(projects)} projects")
    conn.commit()

def populate_publications(conn, resume_data):
    """Populate publications table"""
    cursor = conn.cursor()
    publications = resume_data.get('publications', [])

    print("Populating publications...")
    for pub in publications:
        cursor.execute('''
            INSERT INTO publications (title, authors, journal, year, link)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            pub.get('title', 'Untitled Publication'),
            pub.get('authors', 'Unknown Author'),
            pub.get('journal', 'Unknown Journal'),  # Use journal field from resume.json
            int(pub.get('year', 2020)) if str(pub.get('year', '')).isdigit() else 2020,
            pub.get('link', '')
        ))

    print(f"  Inserted {len(publications)} publications")
    conn.commit()

def populate_personality(conn, resume_data):
    """Populate personality data"""
    cursor = conn.cursor()

    # Extract personality traits from summary
    summary = resume_data.get('summary', '')

    personality_data = {
        'work_style': 'Fast-paced environments, learn quickly, adapt naturally, lead projects with independence and precision',
        'strengths': 'Planning, analysis, execution with scientific rigor, building systems that learn, scale, and last',
        'background': 'Biomedical research to production AI systems',
        'approach': 'Multi-agentic flows connecting data, reasoning, and visualization'
    }

    print("Populating personality data...")
    cursor.execute('''
        INSERT INTO personality (personality_summary, work_style, strengths, personal_values, motivations, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        resume_data.get('summary', ''),  # Use summary as personality_summary
        personality_data['work_style'],
        json.dumps([personality_data['strengths']]),  # Convert to JSON array
        json.dumps([personality_data['background']]),  # Use as personal_values
        json.dumps([personality_data['approach']]),  # Use as motivations
        datetime.now()
    ))

    print("  Inserted personality data")
    conn.commit()

def extract_tech_from_highlight(highlight):
    """Extract technologies mentioned in a highlight"""
    tech_keywords = [
        'React', 'TypeScript', 'Python', 'FastAPI', 'Django', 'LangChain', 'LangGraph',
        'Celery', 'Redis', 'PostgreSQL', 'Docker', 'TailwindCSS', 'Shadcn/ui', 'Radix UI',
        'ApexCharts', 'Recharts', 'Plotly', 'Framer Motion', 'React Query', 'Redux',
        'React Router', 'Axios', 'React Hook Form', 'WebSockets', 'OpenAI', 'Anthropic',
        'Google Gemini', 'Perplexity AI', 'RAG', 'pgvector', 'VAE', 'LSTM', 'CNN',
        'Elasticsearch', 'Nginx', 'Gunicorn', 'Uvicorn'
    ]

    found_tech = []
    highlight_lower = highlight.lower()

    for tech in tech_keywords:
        if tech.lower() in highlight_lower:
            found_tech.append(tech)

    return found_tech

def main():
    """Main migration function"""
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    db_path = project_root / "backend" / "resume_dashboard.db"
    resume_path = project_root / "resume_docs" / "resume.json"

    print(f"Database path: {db_path}")
    print(f"Resume JSON path: {resume_path}")

    # Load resume data
    try:
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        print("✅ Loaded resume.json successfully")
    except Exception as e:
        print(f"❌ Error loading resume.json: {e}")
        return

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return

    try:
        # Clear existing data
        clear_database(conn)

        # Populate all tables
        populate_skills(conn, resume_data)
        populate_experience(conn, resume_data)
        populate_education(conn, resume_data)
        populate_projects(conn, resume_data)
        populate_publications(conn, resume_data)
        populate_personality(conn, resume_data)

        print("\n✅ Database migration completed successfully!")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()