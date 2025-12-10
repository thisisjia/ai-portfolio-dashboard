"""Admin analytics endpoint for viewing dashboard access logs."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime
import os
import aiosqlite
from ..utils.database import DatabaseManager

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin token - loaded from environment variable
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

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

        visitors = []
        for row in result:
            visitors.append({
                "company": row[0] or "Unknown",
                "company_name": row[1] or row[0] or "Unknown",
                "last_accessed": row[2],
                "first_accessed": row[3],
                "visit_count": row[4] if row[4] > 0 else 1
            })

        # Generate HTML response
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Analytics - Resume Dashboard</title>
            <style>
                body {{
                    font-family: system-ui, -apple-system, sans-serif;
                    max-width: 1200px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                h1 {{
                    margin: 0;
                    font-size: 32px;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .stat-number {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .stat-label {{
                    color: #666;
                    margin-top: 5px;
                }}
                table {{
                    width: 100%;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-collapse: collapse;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    padding: 15px;
                    text-align: left;
                    font-weight: 600;
                }}
                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #eee;
                }}
                tr:hover {{
                    background: #f9f9f9;
                }}
                .badge {{
                    background: #667eea;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                .time {{
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 Admin Analytics Dashboard</h1>
                <p>Resume Dashboard Access Logs</p>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(visitors)}</div>
                    <div class="stat-label">Total Visitors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(v['visit_count'] for v in visitors)}</div>
                    <div class="stat-label">Total Visits</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([v for v in visitors if v['last_accessed'] and (datetime.now() - datetime.fromisoformat(v['last_accessed'])).days < 7])}</div>
                    <div class="stat-label">This Week</div>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Company Domain</th>
                        <th>Company Name</th>
                        <th>Last Accessed</th>
                        <th>First Accessed</th>
                        <th>Visit Count</th>
                    </tr>
                </thead>
                <tbody>
        """

        for visitor in visitors:
            last_accessed = visitor['last_accessed']
            first_accessed = visitor['first_accessed']

            # Format timestamps
            if last_accessed:
                try:
                    dt = datetime.fromisoformat(last_accessed)
                    last_accessed = dt.strftime("%b %d, %Y %I:%M %p")
                except:
                    last_accessed = "Unknown"
            else:
                last_accessed = "Never"

            if first_accessed:
                try:
                    dt = datetime.fromisoformat(first_accessed)
                    first_accessed = dt.strftime("%b %d, %Y")
                except:
                    first_accessed = "Unknown"
            else:
                first_accessed = "Unknown"

            html += f"""
                    <tr>
                        <td><strong>{visitor['company']}</strong></td>
                        <td>{visitor['company_name']}</td>
                        <td class="time">{last_accessed}</td>
                        <td class="time">{first_accessed}</td>
                        <td><span class="badge">{visitor['visit_count']} visits</span></td>
                    </tr>
            """

        if not visitors:
            html += """
                    <tr>
                        <td colspan="5" style="text-align: center; padding: 40px; color: #999;">
                            No visitors yet
                        </td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </body>
        </html>
        """

        return {"html": html, "visitors": visitors}

    finally:
        await db.close()
