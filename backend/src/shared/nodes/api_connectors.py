"""API connector nodes for external services."""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph
from pydantic import BaseModel
import httpx
import os


class TavilySearchState(BaseModel):
    query: str = ""
    search_results: Optional[Dict[str, Any]] = None
    search_params: Dict[str, Any] = {}


class TavilySearchNode:
    """Node for searching via Tavily API.
    
    Args:
        api_key: Tavily API key
        search_depth: "basic" or "advanced"
    """
    
    def __init__(self, api_key: Optional[str] = None, search_depth: str = "basic"):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.search_depth = search_depth
        self.base_url = "https://api.tavily.com/search"
    
    def __call__(self, state: TavilySearchState) -> TavilySearchState:
        """Search using Tavily API.
        
        Args:
            state: TavilySearchState containing query and search parameters
            
        Returns:
            Updated state with search results
        """
        if not self.api_key:
            raise ValueError("Tavily API key not provided")
        
        payload = {
            "api_key": self.api_key,
            "query": state.query,
            "search_depth": self.search_depth,
            **state.search_params
        }
        
        with httpx.Client() as client:
            response = client.post(self.base_url, json=payload)
            response.raise_for_status()
            state.search_results = response.json()
        
        return state


class ExternalAPIState(BaseModel):
    endpoint: str = ""
    method: str = "GET"
    request_params: Dict[str, Any] = {}
    api_response: Optional[Dict[str, Any]] = None


class ExternalAPINode:
    """Generic node for external API calls.
    
    Args:
        base_url: Base URL for the API
        headers: Optional headers dict
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = headers or {}
    
    def __call__(self, state: ExternalAPIState) -> ExternalAPIState:
        """Make API request.
        
        Args:
            state: ExternalAPIState containing endpoint and request parameters
            
        Returns:
            Updated state with API response
        """
        url = f"{self.base_url}/{state.endpoint.lstrip('/')}"
        
        with httpx.Client() as client:
            response = client.request(
                method=state.method,
                url=url,
                headers=self.headers,
                **state.request_params
            )
            response.raise_for_status()
            state.api_response = response.json()
        
        return state