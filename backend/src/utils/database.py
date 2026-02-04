"""Database management utilities."""

import sqlite3
import aiosqlite
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use path relative to backend folder
            import os
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            db_path = os.path.join(backend_dir, "resume_dashboard.db")
        self.db_path = db_path
        self.schema_path = Path(__file__).parent.parent / "schema.sql"
    
    async def initialize(self):
        """Initialize database with schema."""
        # Create database file if it doesn't exist
        if not Path(self.db_path).exists():
            await self._create_schema()
            await self._insert_sample_data()
        
        print(f"✅ Database initialized: {self.db_path}")
    
    async def _create_schema(self):
        """Create database schema from SQL file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(schema_sql)
            await db.commit()
    
    async def _insert_sample_data(self):
        """Insert sample resume data and tokens."""
        async with aiosqlite.connect(self.db_path) as db:
            # Sample tokens (matching our current JSON tokens)
            token_data = [
                ("2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824", "acme_corp", "Acme Corporation", '{"industry": "Technology", "size": "enterprise", "focus_areas": ["AI", "automation", "scaling"]}'),
                ("486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65260e9cb8a7", "startup_xyz", "Startup XYZ", '{"industry": "Fintech", "size": "startup", "focus_areas": ["payments", "blockchain", "mobile"]}'),
                ("ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae", "big_tech", "BigTech Solutions", '{"industry": "Enterprise Software", "size": "large", "focus_areas": ["cloud", "enterprise", "AI/ML"]}')
            ]
            
            for token_hash, company, company_name, custom_data in token_data:
                await db.execute("""
                    INSERT OR IGNORE INTO token_access (token_hash, company, company_name, custom_data)
                    VALUES (?, ?, ?, ?)
                """, (token_hash, company, company_name, custom_data))
            # Sample projects
            await db.execute("""
                INSERT INTO projects (name, description, tech_stack, github_url, impact_score, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Resume Dashboard",
                "Token-gated interactive portfolio with AI chatbot and real-time API integrations",
                json.dumps(["Python", "FastAPI", "LangGraph", "React", "SQLite"]),
                "https://github.com/user/resume-dashboard",
                9,
                "2024-12-01",
                "2025-01-15",
                "in_progress"
            ))
            
            # Sample skills
            skills_data = [
                ("Backend", "Python", 5, 3.5, "2024-12-01"),
                ("Backend", "FastAPI", 4, 1.0, "2024-12-01"),
                ("AI/ML", "LangChain", 4, 0.5, "2024-12-01"),
                ("AI/ML", "OpenAI API", 4, 1.0, "2024-12-01"),
                ("Frontend", "React", 4, 2.0, "2024-11-01"),
                ("Database", "SQLite", 4, 2.0, "2024-12-01"),
                ("DevOps", "Docker", 3, 1.5, "2024-10-01"),
            ]
            
            for category, skill_name, proficiency, years_exp, last_used in skills_data:
                await db.execute("""
                    INSERT INTO skills (category, skill_name, proficiency_level, years_experience, last_used)
                    VALUES (?, ?, ?, ?, ?)
                """, (category, skill_name, proficiency, years_exp, last_used))
            
            # Sample work experience
            await db.execute("""
                INSERT INTO work_experience (company, position, start_date, end_date, description, achievements, tech_stack)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Tech Innovations Inc",
                "Full Stack Developer",
                "2023-06-01",
                "2024-11-30",
                "Developed web applications and AI-powered features",
                json.dumps([
                    "Built 3 production web applications serving 10k+ users",
                    "Implemented AI chatbot reducing support tickets by 40%",
                    "Led migration to microservices architecture"
                ]),
                json.dumps(["Python", "React", "PostgreSQL", "Docker", "AWS"])
            ))
            
            # Sample query demonstrations
            demo_queries = [
                ("Project Overview", "SELECT name, description, status, impact_score FROM projects ORDER BY impact_score DESC;", "Shows all projects ranked by impact", "portfolio"),
                ("Skills by Category", "SELECT category, COUNT(*) as skill_count, AVG(proficiency_level) as avg_proficiency FROM skills GROUP BY category;", "Summarizes skills expertise by category", "skills"),
                ("Recent Projects", "SELECT name, tech_stack, start_date FROM projects WHERE start_date >= '2024-01-01' ORDER BY start_date DESC;", "Shows projects from current year", "portfolio"),
            ]
            
            for name, sql, desc, category in demo_queries:
                await db.execute("""
                    INSERT INTO query_demonstrations (query_name, query_sql, description, category)
                    VALUES (?, ?, ?, ?)
                """, (name, sql, desc, category))
            
            await db.commit()
            print("✅ Sample data inserted")
    
    async def log_access(self, token_hash: str, ip_address: str, user_agent: str, page_accessed: str, company_domain: str = None):
        """Log access attempt."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO access_logs (token_hash, ip_address, user_agent, page_accessed, company_domain)
                VALUES (?, ?, ?, ?, ?)
            """, (token_hash, ip_address, user_agent, page_accessed, company_domain))
            await db.commit()
    
    async def log_chat(self, session_id: str, token: str, company: str,
                      user_message: str, ai_response: str, agent_used: str):
        """Log chat interaction."""
        import hashlib
        import time

        # Hash the token for storage (handle None token)
        if token:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
        else:
            token_hash = hashlib.sha256("anonymous".encode()).hexdigest()

        # Calculate a mock response time (in real app, measure actual time)
        response_time_ms = int(time.time() * 1000) % 1000 + 500  # Mock 500-1500ms

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO chat_logs (session_id, token_hash, agent_type, user_message, bot_response, response_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, token_hash, agent_used, user_message, ai_response, response_time_ms))
            await db.commit()
    
    async def log_feedback(self, token: str, session_id: str, feedback_type: str,
                           feedback_value: str, metadata: Dict[str, Any] = None):
        """Log user feedback."""
        import hashlib
        
        # Hash the token for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO feedback_logs (token_hash, session_id, feedback_type, feedback_value, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (token_hash, session_id, feedback_type, feedback_value, json.dumps(metadata or {})))
            await db.commit()
    
    async def execute_demo_query(self, query_name: str) -> Dict[str, Any]:
        """Execute a demonstration query by name."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get the query
            cursor = await db.execute("""
                SELECT query_sql, description FROM query_demonstrations WHERE query_name = ?
            """, (query_name,))
            result = await cursor.fetchone()
            
            if not result:
                raise ValueError(f"Query '{query_name}' not found")
            
            query_sql, description = result
            
            # Execute the actual query
            cursor = await db.execute(query_sql)
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            return {
                "query_name": query_name,
                "description": description,
                "sql": query_sql,
                "columns": columns,
                "rows": [dict(zip(columns, row)) for row in rows],
                "count": len(rows)
            }
    
    async def get_available_queries(self) -> List[Dict[str, Any]]:
        """Get list of available demonstration queries."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT query_name, description, category FROM query_demonstrations ORDER BY category, query_name
            """)
            rows = await cursor.fetchall()
            
            return [
                {"name": row[0], "description": row[1], "category": row[2]}
                for row in rows
            ]
    
    async def get_token_info(self, token_hash: str) -> Optional[Dict[str, Any]]:
        """Get token information from database."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT company, company_name, custom_data, last_accessed
                FROM token_access WHERE token_hash = ?
            """, (token_hash,))
            row = await cursor.fetchone()
            
            if row:
                return {
                    "company": row[0],
                    "company_name": row[1], 
                    "custom_data": json.loads(row[2]) if row[2] else {},
                    "last_accessed": row[3]
                }
            return None
    
    async def update_token_access(self, token_hash: str):
        """Update last accessed time for token."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE token_access SET last_accessed = CURRENT_TIMESTAMP
                WHERE token_hash = ?
            """, (token_hash,))
            await db.commit()

    async def update_token_company(self, token_hash: str, company: str, company_name: str):
        """Update company information for a token."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE token_access
                SET company = ?, company_name = ?, last_accessed = CURRENT_TIMESTAMP
                WHERE token_hash = ?
            """, (company, company_name, token_hash))
            await db.commit()
    
    async def create_token(self, token_hash: str, company: str, company_name: str, 
                          custom_data: Dict[str, Any] = None) -> bool:
        """Create a new access token."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO token_access (token_hash, company, company_name, custom_data)
                    VALUES (?, ?, ?, ?)
                """, (token_hash, company, company_name, json.dumps(custom_data or {})))
                await db.commit()
                return True
        except Exception:
            return False
    
    async def revoke_token(self, token_hash: str) -> bool:
        """Revoke (delete) an access token."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    DELETE FROM token_access WHERE token_hash = ?
                """, (token_hash,))
                await db.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    async def list_tokens(self) -> List[Dict[str, Any]]:
        """List all active tokens."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT token_hash, company, company_name, created_at, last_accessed
                FROM token_access ORDER BY created_at DESC
            """)
            rows = await cursor.fetchall()
            
            return [
                {
                    "token_hash": row[0][:8] + "...",  # Show only first 8 chars for security
                    "company": row[1],
                    "company_name": row[2],
                    "created_at": row[3],
                    "last_accessed": row[4]
                }
                for row in rows
            ]

    async def close(self):
        """Close database connections."""
        # No persistent connections to close for aiosqlite
        pass