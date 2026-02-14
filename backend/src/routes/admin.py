"""Admin analytics endpoint for viewing dashboard access logs."""

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime
from pathlib import Path
import os
import aiosqlite
from ..utils.database import DatabaseManager

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin token - loaded from environment variable
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

# Setup Jinja2 templates
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/analytics")
async def get_analytics(authorization: Optional[str] = Header(None)):
    """Get dashboard access analytics.

    Requires admin token in Authorization header.
    """
    # Check admin token
    if not authorization or authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=403, detail="Unauthorized - Invalid admin token")

    # Get database manager
    db = DatabaseManager()
    await db.initialize()

    try:
        # Query all tokens with access info and count visits
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT
                    t.company,
                    t.company_name,
                    t.last_accessed,
                    t.created_at,
                    COUNT(a.id) as access_count
                FROM token_access t
                LEFT JOIN access_logs a ON t.token_hash = a.token_hash
                WHERE t.company IS NOT NULL
                GROUP BY t.token_hash, t.company, t.company_name, t.last_accessed, t.created_at
                ORDER BY t.last_accessed DESC
            """)
            result = await cursor.fetchall()

        # Process visitor data and format timestamps
        visitors = []
        for row in result:
            visitor = {
                "company": row[0] or "Unknown",
                "company_name": row[1] or row[0] or "Unknown",
                "last_accessed": row[2],
                "first_accessed": row[3],
                "visit_count": row[4] if row[4] > 0 else 1
            }

            # Format timestamps
            if visitor['last_accessed']:
                try:
                    dt = datetime.fromisoformat(visitor['last_accessed'])
                    visitor['last_accessed_formatted'] = dt.strftime("%b %d, %Y %I:%M %p")
                except:
                    visitor['last_accessed_formatted'] = "Unknown"
            else:
                visitor['last_accessed_formatted'] = "Never"

            if visitor['first_accessed']:
                try:
                    dt = datetime.fromisoformat(visitor['first_accessed'])
                    visitor['first_accessed_formatted'] = dt.strftime("%b %d, %Y")
                except:
                    visitor['first_accessed_formatted'] = "Unknown"
            else:
                visitor['first_accessed_formatted'] = "Unknown"

            visitors.append(visitor)

        # Calculate stats
        total_visitors = len(visitors)
        total_visits = sum(v['visit_count'] for v in visitors)
        visitors_this_week = len([
            v for v in visitors
            if v['last_accessed'] and (datetime.now() - datetime.fromisoformat(v['last_accessed'])).days < 7
        ])

        # Render template
        html_content = templates.get_template("admin_analytics.html").render(
            total_visitors=total_visitors,
            total_visits=total_visits,
            visitors_this_week=visitors_this_week,
            visitors=visitors
        )

        return HTMLResponse(content=html_content)

    finally:
        await db.close()
