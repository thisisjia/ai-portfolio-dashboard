"""Populate database with real resume data."""

import sqlite3
import json
import os
from datetime import datetime

# Database path - use environment variable or default
DB_PATH = os.getenv("DATABASE_PATH", "/app/resume_dashboard.db")

def populate_resume_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing data (optional - comment out if you want to keep tokens)
    cursor.execute("DELETE FROM projects")
    cursor.execute("DELETE FROM skills")
    cursor.execute("DELETE FROM work_experience")
    cursor.execute("DELETE FROM education")
    cursor.execute("DELETE FROM tools_used")
    cursor.execute("DELETE FROM query_demonstrations")
    
    # ================== PROJECTS ==================
    projects = [
        {
            "name": "Deal Sourcing Engine",
            "description": "Automated multi-API pipeline (Affinity CRM, PitchBook, CapIQ, Alternatives.pe) for sourcing and filtering deals, tagging status, and generating structured outputs for investment teams",
            "tech_stack": ["Python", "FastAPI", "Django ORM", "PostgreSQL", "LangChain", "LangGraph"],
            "github_url": "",  # Add if you want
            "impact_score": 9,
            "start_date": "2024-01-01",
            "end_date": "2025-12-31",
            "status": "in_progress"
        },
        {
            "name": "Market Insights Report Generator",
            "description": "Aggregates global macroeconomic indicators and investment news. Embeds, clusters, and generates structured monthly reports with LLM analysis",
            "tech_stack": ["Python", "LangChain", "Django", "PostgreSQL", "pgvector", "OpenAI Vision", "SerpAPI", "Tavily API"],
            "github_url": "",
            "impact_score": 9,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "status": "in_progress"
        },
        {
            "name": "ESG Reporting Automation",
            "description": "Automated ESG compliance workflow for investee companies with Affinity CRM integration, form triggers, and due diligence report generation",
            "tech_stack": ["Python", "Django", "PostgreSQL", "FastAPI", "OpenAI Vision", "LangGraph"],
            "github_url": "",
            "impact_score": 8,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "status": "in_progress"
        },
        {
            "name": "OCR & Document Intelligence System",
            "description": "Improved OCR pipeline with ColPali integration for layout awareness, table parsing, structured JSON extraction, and semantic embedding for search",
            "tech_stack": ["Python", "PyTorch", "OpenAI Vision", "ColPali", "FAISS", "pgvector"],
            "github_url": "",
            "impact_score": 8,
            "start_date": "2024-06-01",
            "end_date": "2025-12-31",
            "status": "in_progress"
        },
        {
            "name": "Token-Gated Resume Dashboard",
            "description": "Interactive private dashboard for recruiters featuring LangGraph chatbot, SQL query demo, feedback module, and API integration showcase",
            "tech_stack": ["React", "Next.js", "Tailwind", "FastAPI", "LangGraph", "Docker", "SQLite"],
            "github_url": "https://github.com/yourusername/resume-dashboard",  # Update this
            "impact_score": 7,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "status": "in_progress"
        }
    ]
    
    for project in projects:
        cursor.execute("""
            INSERT INTO projects (name, description, tech_stack, github_url, impact_score, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project["name"],
            project["description"],
            json.dumps(project["tech_stack"]),
            project["github_url"],
            project["impact_score"],
            project["start_date"],
            project["end_date"],
            project["status"]
        ))
    
    # ================== SKILLS ==================
    skills = [
        # Backend
        ("Backend", "Python", 5, 5.0, "2025-01-01"),
        ("Backend", "FastAPI", 4, 2.0, "2025-01-01"),
        ("Backend", "Django", 4, 2.0, "2025-01-01"),
        ("Backend", "Flask", 3, 1.0, "2024-01-01"),
        
        # Frontend
        ("Frontend", "React", 3, 1.0, "2024-12-01"),
        ("Frontend", "Next.js", 3, 0.5, "2024-12-01"),
        ("Frontend", "Tailwind CSS", 3, 0.5, "2024-12-01"),
        ("Frontend", "HTML/CSS", 3, 2.0, "2024-01-01"),
        ("Frontend", "JavaScript", 3, 1.5, "2024-01-01"),
        
        # Database
        ("Database", "PostgreSQL", 4, 3.0, "2025-01-01"),
        ("Database", "SQLite", 4, 2.0, "2025-01-01"),
        ("Database", "pgvector", 3, 1.0, "2024-12-01"),
        ("Database", "Redis", 3, 1.0, "2024-01-01"),
        
        # AI/ML
        ("AI/ML", "LangChain", 4, 2.0, "2025-01-01"),
        ("AI/ML", "LangGraph", 3, 1.0, "2025-01-01"),
        ("AI/ML", "OpenAI API", 4, 2.0, "2025-01-01"),
        ("AI/ML", "TensorFlow", 3, 1.0, "2024-01-01"),
        ("AI/ML", "PyTorch", 3, 1.0, "2024-01-01"),
        ("AI/ML", "Embeddings", 4, 1.5, "2025-01-01"),
        
        # DevOps
        ("DevOps", "Docker", 4, 2.0, "2025-01-01"),
        ("DevOps", "Git", 4, 4.0, "2025-01-01"),
        ("DevOps", "CI/CD", 3, 1.0, "2024-01-01"),
        ("DevOps", "Loguru/Loki", 3, 1.0, "2024-06-01"),
        ("DevOps", "AWS", 2, 0.5, "2024-01-01"),
        ("DevOps", "GCP", 2, 0.5, "2024-01-01"),
    ]
    
    for category, skill_name, proficiency, years_exp, last_used in skills:
        cursor.execute("""
            INSERT INTO skills (category, skill_name, proficiency_level, years_experience, last_used)
            VALUES (?, ?, ?, ?, ?)
        """, (category, skill_name, proficiency, years_exp, last_used))
    
    # ================== WORK EXPERIENCE ==================
    work_experiences = [
        {
            "company": "Integrum Global",
            "position": "AI Engineer",
            "start_date": "2024-01-01",
            "end_date": None,  # Current position
            "description": "Building AI-powered investment intelligence and automation systems",
            "achievements": [
                "Built multi-source investment intelligence pipeline integrating APIs, embeddings, and LLM analysis",
                "Designed treasury dashboard for FX and yield curve analysis with Bloomberg data",
                "Developed structured market insights reporting with automated news ingestion and clustering"
            ],
            "tech_stack": ["Python", "FastAPI", "Django ORM", "PostgreSQL", "LangChain", "Docker"]
        },
        {
            "company": "TSGS",
            "position": "Data Scientist / ML Engineer",
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "description": "Developed ML models for healthcare and biomedical applications",
            "achievements": [
                "Developed VAE-LSTM anomaly detection for time-series biomedical data",
                "Built facial weakness detection system using MTCNN & Mediapipe",
                "Transitioned workflows into OOP and clean architecture pipelines with API integrations"
            ],
            "tech_stack": ["Python", "PyTorch", "TensorFlow", "Mediapipe", "FastAPI"]
        },
        {
            "company": "Lee Kong Chian School of Medicine",
            "position": "Research Assistant",
            "start_date": "2020-01-01",
            "end_date": "2021-12-31",
            "description": "Supported neuroscience and genetics research projects",
            "achievements": [
                "Applied image processing techniques for cellular imaging analysis",
                "Supported neuroscience and genetics research projects"
            ],
            "tech_stack": ["Python", "ImageJ", "R"]
        },
        {
            "company": "A*STAR",
            "position": "Research Officer",
            "start_date": "2019-01-01",
            "end_date": "2020-12-31",
            "description": "Conducted biomedical research in genetics and pathology",
            "achievements": [
                "Conducted wet-lab experiments across genetics, pathology, and biochemistry",
                "Co-authored publications in eLife and EMBO Reports"
            ],
            "tech_stack": ["Python", "R", "Laboratory Techniques"]
        }
    ]
    
    for exp in work_experiences:
        cursor.execute("""
            INSERT INTO work_experience (company, position, start_date, end_date, description, achievements, tech_stack)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            exp["company"],
            exp["position"],
            exp["start_date"],
            exp["end_date"],
            exp["description"],
            json.dumps(exp["achievements"]),
            json.dumps(exp["tech_stack"])
        ))
    
    # ================== EDUCATION ==================
    education_records = [
        {
            "institution": "University of Western Australia",
            "degree": "Bachelor of Medical Science (BMedSc) & Bachelor of Science (BSc)",
            "field_of_study": "Genetics, Neuroscience, Biochemistry, Molecular Genetics",
            "start_date": "2015-01-01",  # Update these dates
            "end_date": "2019-12-31",     # Update these dates
            "gpa": None,  # Add if you want
            "achievements": ["Publications in peer-reviewed journals (eLife, EMBO Reports)"]
        },
        {
            "institution": "Le Wagon",
            "degree": "Certificate in Data Science",
            "field_of_study": "Data Science and Machine Learning",
            "start_date": "2022-01-01",  # Update these dates
            "end_date": "2022-06-30",     # Update these dates
            "gpa": None,
            "achievements": ["Completed intensive bootcamp program"]
        }
    ]
    
    for edu in education_records:
        cursor.execute("""
            INSERT INTO education (institution, degree, field_of_study, start_date, end_date, gpa, achievements)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            edu["institution"],
            edu["degree"],
            edu["field_of_study"],
            edu["start_date"],
            edu["end_date"],
            edu["gpa"],
            json.dumps(edu["achievements"])
        ))
    
    # ================== DEMO QUERIES ==================
    demo_queries = [
        ("My Top Projects", 
         "SELECT name, description, impact_score, status FROM projects ORDER BY impact_score DESC LIMIT 5;",
         "Shows my highest-impact projects ranked by importance",
         "portfolio"),
        
        ("Technical Stack Overview",
         """SELECT category, COUNT(*) as skill_count, 
            ROUND(AVG(proficiency_level), 1) as avg_proficiency,
            ROUND(AVG(years_experience), 1) as avg_years
            FROM skills GROUP BY category ORDER BY avg_proficiency DESC;""",
         "Summarizes my technical skills by category with proficiency levels",
         "skills"),
         
        ("Current Projects",
         """SELECT name, tech_stack, 
            julianday('now') - julianday(start_date) as days_active
            FROM projects WHERE status = 'in_progress' 
            ORDER BY impact_score DESC;""",
         "Shows all active projects I'm currently working on",
         "portfolio"),
         
        ("Career Timeline",
         """SELECT company, position, start_date, end_date,
            CASE WHEN end_date IS NULL THEN 'Current' ELSE end_date END as period
            FROM work_experience ORDER BY start_date DESC;""",
         "My professional journey from research to AI engineering",
         "experience"),
         
        ("AI/ML Expertise",
         """SELECT skill_name, proficiency_level, years_experience 
            FROM skills WHERE category = 'AI/ML' 
            ORDER BY proficiency_level DESC, years_experience DESC;""",
         "Deep dive into my AI and machine learning capabilities",
         "skills"),
         
        ("Investment Tech Stack",
         """SELECT p.name as project, p.tech_stack 
            FROM projects p 
            WHERE p.name LIKE '%Deal%' OR p.name LIKE '%Market%' OR p.name LIKE '%ESG%'
            ORDER BY p.impact_score DESC;""",
         "Technologies used in my investment and finance projects",
         "portfolio")
    ]
    
    for name, sql, desc, category in demo_queries:
        cursor.execute("""
            INSERT INTO query_demonstrations (query_name, query_sql, description, category)
            VALUES (?, ?, ?, ?)
        """, (name, sql, desc, category))
    
    conn.commit()
    conn.close()
    print("✅ Database populated with resume data!")
    
    # Show summary
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📊 Database Summary:")
    print(f"- Projects: {cursor.execute('SELECT COUNT(*) FROM projects').fetchone()[0]}")
    print(f"- Skills: {cursor.execute('SELECT COUNT(*) FROM skills').fetchone()[0]}")
    print(f"- Work Experience: {cursor.execute('SELECT COUNT(*) FROM work_experience').fetchone()[0]}")
    print(f"- Education: {cursor.execute('SELECT COUNT(*) FROM education').fetchone()[0]}")
    print(f"- Demo Queries: {cursor.execute('SELECT COUNT(*) FROM query_demonstrations').fetchone()[0]}")
    
    conn.close()

if __name__ == "__main__":
    populate_resume_data()
    print("\n🎯 Your resume dashboard database is ready!")
    print("Test tokens still work: 'hello', 'world', 'test123'")