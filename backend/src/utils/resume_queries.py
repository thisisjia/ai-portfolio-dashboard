"""
Direct database queries for resume data.
This replaces RAG/vector search with accurate structured data queries.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class ResumeDataQueries:
    """Direct database queries for resume information."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Use the database in the backend working directory
            import os
            db_path = os.path.join(os.getcwd(), "resume_dashboard.db")
        self.db_path = str(db_path)  # Convert to string for sqlite3
        self._connection = None

    def get_connection(self):
        """Get database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
        return self._connection

    def get_skills_by_category(self, category: Optional[str] = None) -> List[Dict]:
        """Get skills, optionally filtered by category."""
        conn = self.get_connection()
        cursor = conn.cursor()

        if category:
            cursor.execute('''
                SELECT category, skill_name, proficiency_level, years_experience
                FROM skills
                WHERE category = ?
                ORDER BY proficiency_level DESC, skill_name
            ''', (category,))
        else:
            cursor.execute('''
                SELECT category, skill_name, proficiency_level, years_experience
                FROM skills
                ORDER BY category, proficiency_level DESC, skill_name
            ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'category': row[0],
                'skill_name': row[1],
                'proficiency_level': row[2],
                'years_experience': row[3]
            })

        return results

    def get_all_skills_grouped(self) -> Dict[str, List[str]]:
        """Get all skills grouped by category."""
        skills = self.get_skills_by_category()
        grouped = {}

        for skill in skills:
            category = skill['category']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(skill['skill_name'])

        return grouped

    def search_skills(self, query: str) -> List[Dict]:
        """Search for skills by name or category."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT category, skill_name, proficiency_level, years_experience
            FROM skills
            WHERE skill_name LIKE ? OR category LIKE ?
            ORDER BY proficiency_level DESC
        ''', (f'%{query}%', f'%{query}%'))

        results = []
        for row in cursor.fetchall():
            results.append({
                'category': row[0],
                'skill_name': row[1],
                'proficiency_level': row[2],
                'years_experience': row[3]
            })

        return results

    def get_work_experience(self) -> List[Dict]:
        """Get all work experience."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT company, position, start_date, end_date, description, achievements, tech_stack
            FROM work_experience
            ORDER BY start_date DESC
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'company': row[0],
                'position': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'description': row[4],
                'achievements': json.loads(row[5]) if row[5] else [],
                'tech_stack': json.loads(row[6]) if row[6] else []
            })

        return results

    def get_education(self) -> List[Dict]:
        """Get education background."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT institution, degree, field_of_study, start_date, end_date, achievements
            FROM education
            ORDER BY start_date DESC
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'institution': row[0],
                'degree': row[1],
                'field_of_study': row[2],
                'start_date': row[3],
                'end_date': row[4],
                'achievements': json.loads(row[5]) if row[5] else []
            })

        return results

    def get_projects(self) -> List[Dict]:
        """Get projects."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT name, description, tech_stack, status, start_date, end_date
            FROM projects
            ORDER BY start_date DESC
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'name': row[0],
                'description': row[1],
                'tech_stack': json.loads(row[2]) if row[2] else [],
                'status': row[3],
                'start_date': row[4],
                'end_date': row[5]
            })

        return results

    def get_publications(self) -> List[Dict]:
        """Get publications."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT title, authors, journal, year, link
            FROM publications
            ORDER BY year DESC
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'title': row[0],
                'authors': row[1].split(', ') if row[1] else [],
                'journal': row[2],
                'year': row[3],
                'link': row[4]
            })

        return results

    def get_personality_summary(self) -> Dict:
        """Get personality summary."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT personality_summary, work_style, strengths, personal_values, motivations
            FROM personality
            ORDER BY created_at DESC
            LIMIT 1
        ''')

        row = cursor.fetchone()
        if row:
            return {
                'personality_summary': row[0],
                'work_style': row[1],
                'strengths': json.loads(row[2]) if row[2] else [],
                'personal_values': json.loads(row[3]) if row[3] else [],
                'motivations': json.loads(row[4]) if row[4] else []
            }

        return {}

    def get_complete_resume_data(self) -> Dict:
        """Get complete resume data structured like the original JSON."""
        skills_grouped = self.get_all_skills_grouped()

        return {
            'skills': {
                'languages': skills_grouped.get('Programming Languages', []),
                'frameworks': skills_grouped.get('Frameworks & Libraries', []),
                'databases': skills_grouped.get('Databases', []),
                'cloud': skills_grouped.get('Cloud & DevOps', []),
                'tools': skills_grouped.get('Developer Tools', []),
                'frontend': skills_grouped.get('Frontend Technologies', []),
                'ai_ml': skills_grouped.get('AI/ML Technologies', [])
            },
            'experience': self.get_work_experience(),
            'education': self.get_education(),
            'projects': self.get_projects(),
            'publications': self.get_publications(),
            'personality': self.get_personality_summary()
        }

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

# Singleton instance
_resume_queries = None

def get_resume_queries() -> ResumeDataQueries:
    """Get singleton instance of resume queries."""
    global _resume_queries
    if _resume_queries is None:
        _resume_queries = ResumeDataQueries()
    return _resume_queries