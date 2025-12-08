"""SQL Query Demonstration routes."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..utils.database import DatabaseManager

router = APIRouter(prefix="/api/sql", tags=["SQL Demo"])
db_manager = DatabaseManager()


@router.get("/queries")
async def get_available_queries() -> List[Dict[str, Any]]:
    """Get list of available demonstration queries."""
    try:
        queries = await db_manager.get_available_queries()
        return queries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_query(query_name: str) -> Dict[str, Any]:
    """Execute a demonstration query by name."""
    try:
        result = await db_manager.execute_demo_query(query_name)
        return {
            "success": True,
            "query_name": result["query_name"],
            "description": result["description"],
            "sql": result["sql"],
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["count"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))