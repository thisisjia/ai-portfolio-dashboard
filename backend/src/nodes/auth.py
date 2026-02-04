from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime
from langgraph.graph import StateGraph
from pydantic import BaseModel


class AuthState(BaseModel):
    token: Optional[str] = None
    authenticated: bool = False
    company: Optional[str] = None
    company_name: Optional[str] = None
    custom_data: Dict[str, Any] = {}
    session_id: Optional[str] = None
    error: Optional[str] = None


class TokenAuthNode:
    """Handles token-based authentication for the resume dashboard using database.
    
    Args:
        db_manager: Database manager instance
        log_access: Whether to log access attempts
    """
    
    def __init__(self, db_manager=None, log_access: bool = True):
        self.db_manager = db_manager
        self.log_access = log_access
        self.access_logs = []
    
    def _hash_token(self, token: str) -> str:
        """Hash a token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def __call__(self, state: AuthState, **kwargs) -> AuthState:
        """Validate token and return authentication result.
        
        Args:
            state: AuthState containing token
            
        Returns:
            Updated AuthState with authentication result
        """
        if not state.token:
            state.error = "No token provided"
            return state
        
        if not self.db_manager:
            state.error = "Database not available"
            return state
        
        hashed_token = self._hash_token(state.token)
        
        # Check token in database
        token_info = await self.db_manager.get_token_info(hashed_token)

        if token_info:
            # Update the company field with whatever the user entered
            if state.company:
                await self.db_manager.update_token_company(hashed_token, state.company, state.company)

            if self.log_access:
                # Update last accessed time
                await self.db_manager.update_token_access(hashed_token)

                self.access_logs.append({
                    "token_hash": hashed_token,
                    "company": state.company or token_info.get("company"),
                    "timestamp": datetime.now().isoformat(),
                    "ip": kwargs.get("ip_address", "unknown")
                })

            state.authenticated = True
            state.company = state.company or token_info.get("company")
            state.company_name = state.company or token_info.get("company_name")
            state.custom_data = token_info.get("custom_data", {})
            state.session_id = f"{hashed_token[:8]}_{int(datetime.now().timestamp())}"
        else:
            state.error = "Invalid token"
        
        return state