"""Main application entry point for the Token-Gated Resume Dashboard."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from pathlib import Path
import os

from .nodes.auth import TokenAuthNode, AuthState
from .utils.database import DatabaseManager
from .utils.config import get_settings
from .utils.domain_validator import get_domain_validator
from .routes import sql_demo, chat, admin

settings = get_settings()

# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Initialize components
db_manager = DatabaseManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    await db_manager.initialize()
    print("🚀 Resume Dashboard started successfully")
    yield
    # Shutdown
    await db_manager.close()
    print("👋 Resume Dashboard shutdown complete")


app = FastAPI(
    title="Token-Gated Resume Dashboard",
    description="Interactive portfolio experience with AI-powered features",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Configured via ALLOWED_ORIGINS env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize auth node
auth_node = TokenAuthNode(db_manager=db_manager)

# Include routers
app.include_router(sql_demo.router)
app.include_router(chat.router)
app.include_router(admin.router)


class TokenRequest(BaseModel):
    token: str
    company_domain: str | None = None


class AuthResponse(BaseModel):
    authenticated: bool
    company: str | None = None
    company_name: str | None = None
    session_id: str | None = None
    error: str | None = None
    domain_valid: bool | None = None
    domain_message: str | None = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Token-Gated Resume Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { text-align: center; padding: 50px 20px; }
            .token-form { margin: 30px 0; }
            input[type="text"] { padding: 12px; font-size: 16px; width: 300px; border: 2px solid #ddd; border-radius: 8px; }
            button { padding: 12px 24px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; margin-left: 10px; }
            button:hover { background: #0056b3; }
            .error { color: red; margin: 10px 0; }
            .success { color: green; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Token-Gated Resume Dashboard</h1>
            <p>Enter your access token to view the interactive portfolio</p>
            
            <div class="token-form">
                <input type="text" id="tokenInput" placeholder="Enter your access token" />
                <button onclick="authenticate()">Access Dashboard</button>
            </div>
            
            <div id="message"></div>
        </div>

        <script>
            async function authenticate() {
                const token = document.getElementById('tokenInput').value;
                const messageDiv = document.getElementById('message');
                
                if (!token) {
                    messageDiv.innerHTML = '<div class="error">Please enter a token</div>';
                    return;
                }
                
                try {
                    const response = await fetch('/auth/token', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ token: token })
                    });
                    
                    const result = await response.json();
                    
                    if (result.authenticated) {
                        messageDiv.innerHTML = `<div class="success">✅ Access granted for ${result.company_name || result.company}</div>`;
                        setTimeout(() => {
                            window.location.href = `/dashboard?session=${result.session_id}`;
                        }, 1500);
                    } else {
                        messageDiv.innerHTML = `<div class="error">❌ ${result.error}</div>`;
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="error">❌ Authentication failed</div>';
                }
            }
            
            // Allow Enter key to submit
            document.getElementById('tokenInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') authenticate();
            });
        </script>
    </body>
    </html>
    """


@app.post("/auth/token", response_model=AuthResponse)
async def authenticate_token(token_request: TokenRequest, request: Request):
    """Authenticate user with provided token and company domain."""
    auth_state = AuthState(token=token_request.token)

    # Initialize response
    response = AuthResponse(
        authenticated=False,
        domain_valid=None,
        domain_message=None
    )

    # Validate domain if provided (optional, always accept for tracking)
    # IMPORTANT: Set company BEFORE calling auth_node so it can save it
    domain_validator = get_domain_validator()
    if token_request.company_domain:
        domain_valid, domain_message = domain_validator.is_valid_domain(token_request.company_domain)
        response.domain_valid = domain_valid
        response.domain_message = domain_message
        # Continue with authentication regardless of domain validation
        auth_state.company = token_request.company_domain
    else:
        # Domain is optional - use generic placeholder
        auth_state.company = "not_provided"
        response.domain_valid = True
        response.domain_message = "Domain not required"

    # Get client IP for logging
    client_ip = request.client.host
    result = await auth_node(auth_state, ip_address=client_ip)

    # Token authentication
    if result.authenticated:
        # Log successful access with domain
        await db_manager.log_access(
            token_hash=auth_node._hash_token(token_request.token),
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            page_accessed="/auth/token",
            company_domain=token_request.company_domain  # Add domain to log
        )

        response.authenticated = True
        response.company = result.company
        response.company_name = result.company_name
        response.session_id = result.session_id
    else:
        response.error = result.error

    return response


@app.get("/dashboard")
async def dashboard(session: str = None):
    """Serve the main dashboard interface."""
    if not session:
        raise HTTPException(status_code=401, detail="Session required")
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .section {{ background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }}
            .coming-soon {{ color: #666; font-style: italic; }}
            
            /* SQL Demo Styles */
            .query-selector {{ display: flex; gap: 10px; margin-bottom: 20px; }}
            select {{ padding: 10px; font-size: 14px; border: 2px solid #e2e8f0; border-radius: 8px; flex: 1; max-width: 400px; }}
            .btn {{ padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }}
            .btn:hover {{ background: #5a67d8; }}
            .btn:disabled {{ background: #cbd5e0; cursor: not-allowed; }}
            
            .sql-display {{ background: #1e293b; color: #94a3b8; padding: 15px; border-radius: 8px; margin: 15px 0; font-family: 'Courier New', monospace; font-size: 13px; overflow-x: auto; }}
            .sql-keyword {{ color: #f472b6; }}
            
            .results-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 15px; }}
            .results-table th {{ background: #f8fafc; padding: 12px; text-align: left; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }}
            .results-table td {{ padding: 12px; border-bottom: 1px solid #f1f5f9; }}
            .results-table tr:hover {{ background: #f8fafc; }}
            
            .loading {{ text-align: center; padding: 20px; color: #64748b; }}
            .error {{ background: #fee2e2; color: #dc2626; padding: 10px; border-radius: 8px; margin: 10px 0; }}
            .description {{ color: #64748b; margin: 10px 0; font-size: 14px; }}
            .row-count {{ color: #64748b; font-size: 14px; margin-top: 10px; }}
            
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-left: 10px; }}
            .badge-success {{ background: #dcfce7; color: #16a34a; }}
            
            /* Chat Styles */
            .chat-message {{ margin-bottom: 15px; }}
            .chat-message.user {{ text-align: right; }}
            .chat-message.user .message-bubble {{ background: #667eea; color: white; margin-left: auto; }}
            .chat-message.assistant .message-bubble {{ background: white; border: 1px solid #e2e8f0; }}
            .message-bubble {{ max-width: 70%; padding: 10px 15px; border-radius: 12px; display: inline-block; text-align: left; }}
            .message-meta {{ font-size: 11px; color: #94a3b8; margin-top: 4px; }}
            .suggestion-btn {{ padding: 8px 12px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; font-size: 13px; text-align: left; transition: all 0.2s; }}
            .suggestion-btn:hover {{ background: #f1f5f9; border-color: #cbd5e0; }}
            .typing-indicator {{ display: inline-block; padding: 10px 15px; background: white; border: 1px solid #e2e8f0; border-radius: 12px; }}
            .typing-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #94a3b8; margin: 0 2px; animation: typing 1.4s infinite; }}
            .typing-dot:nth-child(2) {{ animation-delay: 0.2s; }}
            .typing-dot:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes typing {{ 0%, 60%, 100% {{ opacity: 0.3; }} 30% {{ opacity: 1; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Interactive Resume Dashboard</h1>
            <p>Welcome to my interactive portfolio experience</p>
            <p style="opacity: 0.9; font-size: 14px;">Session: {session}</p>
        </div>
        
        <div class="section">
            <h2>🗃️ SQL Query Demonstrations <span class="badge badge-success">LIVE</span></h2>
            <p class="description">Explore my database skills through interactive SQL queries on real resume data</p>
            
            <div class="query-selector">
                <select id="querySelect">
                    <option value="">Loading queries...</option>
                </select>
                <button class="btn" onclick="executeQuery()" id="executeBtn">Execute Query</button>
            </div>
            
            <div id="queryDescription" class="description"></div>
            <div id="sqlDisplay" class="sql-display" style="display: none;"></div>
            <div id="results"></div>
        </div>
        
        <div class="section">
            <h2>🤖 AI Chat Assistant <span class="badge badge-success">LIVE</span></h2>
            <p class="description">Ask me anything about my experience, skills, projects, or work style!</p>
            
            <div id="chatContainer" style="display: flex; gap: 20px; margin-top: 20px;">
                <div style="flex: 1;">
                    <div id="chatMessages" style="height: 400px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; background: #f8fafc; margin-bottom: 15px;">
                        <div style="text-align: center; color: #64748b; padding: 20px;">
                            <p>👋 Hi! I'm an AI assistant powered by multiple specialized agents.</p>
                            <p>Ask me about technical skills, work experience, projects, or anything else!</p>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="chatInput" placeholder="Type your message..." 
                               style="flex: 1; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px;"
                               onkeypress="if(event.key === 'Enter') sendChatMessage()">
                        <button class="btn" onclick="sendChatMessage()" id="sendBtn">Send</button>
                    </div>
                    
                    <div id="agentIndicator" style="margin-top: 10px; font-size: 12px; color: #64748b;"></div>
                </div>
                
                <div style="width: 250px;">
                    <h4 style="margin-top: 0; margin-bottom: 15px; color: #475569;">Suggested Questions</h4>
                    <div id="suggestions" style="display: flex; flex-direction: column; gap: 8px;">
                        <button class="suggestion-btn" onclick="askSuggestion(this)">What languages do you use?</button>
                        <button class="suggestion-btn" onclick="askSuggestion(this)">Tell me about your AI experience</button>
                        <button class="suggestion-btn" onclick="askSuggestion(this)">What motivates you?</button>
                        <button class="suggestion-btn" onclick="askSuggestion(this)">Describe a challenging project</button>
                        <button class="suggestion-btn" onclick="askSuggestion(this)">What's your work style?</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Live API Integrations</h2>
            <p class="coming-soon">Real-time market data and insights coming soon...</p>
        </div>
        
        <div class="section">
            <h2>👍 Feedback Collection</h2>
            <p class="coming-soon">Vision-based feedback with MediaPipe coming soon...</p>
        </div>

        <script>
            // Load available queries on page load
            async function loadQueries() {{
                try {{
                    const response = await fetch('/api/sql/queries');
                    const queries = await response.json();
                    
                    const select = document.getElementById('querySelect');
                    select.innerHTML = '<option value="">Select a query to execute...</option>';
                    
                    queries.forEach(query => {{
                        const option = document.createElement('option');
                        option.value = query.name;
                        option.textContent = query.name;
                        option.dataset.description = query.description;
                        option.dataset.category = query.category;
                        select.appendChild(option);
                    }});
                    
                    select.addEventListener('change', function() {{
                        const selected = select.options[select.selectedIndex];
                        const desc = document.getElementById('queryDescription');
                        if (selected.value) {{
                            desc.textContent = selected.dataset.description;
                        }} else {{
                            desc.textContent = '';
                        }}
                    }});
                }} catch (error) {{
                    console.error('Failed to load queries:', error);
                }}
            }}
            
            async function executeQuery() {{
                const select = document.getElementById('querySelect');
                const queryName = select.value;
                
                if (!queryName) {{
                    alert('Please select a query first');
                    return;
                }}
                
                const btn = document.getElementById('executeBtn');
                const resultsDiv = document.getElementById('results');
                const sqlDiv = document.getElementById('sqlDisplay');
                
                btn.disabled = true;
                resultsDiv.innerHTML = '<div class="loading">Executing query...</div>';
                sqlDiv.style.display = 'none';
                
                try {{
                    const response = await fetch(`/api/sql/execute?query_name=${{encodeURIComponent(queryName)}}`, {{
                        method: 'POST'
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        // Display SQL with syntax highlighting
                        sqlDiv.innerHTML = highlightSQL(result.sql);
                        sqlDiv.style.display = 'block';
                        
                        // Display results in table
                        let html = '<table class="results-table">';
                        
                        // Headers
                        html += '<thead><tr>';
                        result.columns.forEach(col => {{
                            html += `<th>${{col}}</th>`;
                        }});
                        html += '</tr></thead>';
                        
                        // Rows
                        html += '<tbody>';
                        result.rows.forEach(row => {{
                            html += '<tr>';
                            result.columns.forEach(col => {{
                                let value = row[col];
                                // Format JSON arrays nicely
                                if (typeof value === 'string' && (value.startsWith('[') || value.startsWith('{{'))) {{
                                    try {{
                                        const parsed = JSON.parse(value);
                                        if (Array.isArray(parsed)) {{
                                            value = parsed.join(', ');
                                        }}
                                    }} catch {{}}
                                }}
                                html += `<td>${{value !== null ? value : '-'}}</td>`;
                            }});
                            html += '</tr>';
                        }});
                        html += '</tbody></table>';
                        
                        html += `<div class="row-count">Returned ${{result.row_count}} row(s)</div>`;
                        
                        resultsDiv.innerHTML = html;
                    }} else {{
                        resultsDiv.innerHTML = `<div class="error">Error: ${{result.detail}}</div>`;
                    }}
                }} catch (error) {{
                    resultsDiv.innerHTML = `<div class="error">Failed to execute query: ${{error.message}}</div>`;
                }} finally {{
                    btn.disabled = false;
                }}
            }}
            
            function highlightSQL(sql) {{
                const keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'LIMIT', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'AS', 'ON', 'AND', 'OR', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'COUNT', 'AVG', 'SUM', 'MAX', 'MIN', 'ROUND', 'DESC', 'ASC', 'LIKE', 'IN', 'IS', 'NULL', 'NOT'];
                
                let highlighted = sql;
                keywords.forEach(keyword => {{
                    const regex = new RegExp(`\\b${{keyword}}\\b`, 'gi');
                    highlighted = highlighted.replace(regex, `<span class="sql-keyword">${{keyword}}</span>`);
                }});
                
                return highlighted;
            }}
            
            // Load queries when page loads
            loadQueries();
            
            // Chat functionality
            let chatSessionId = null;
            const urlParams = new URLSearchParams(window.location.search);
            const sessionToken = urlParams.get('session') || 'demo-token';
            
            async function sendChatMessage() {{
                const input = document.getElementById('chatInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message to chat
                addMessageToChat('user', message);
                input.value = '';
                
                // Show typing indicator
                showTypingIndicator();
                
                // Disable send button
                document.getElementById('sendBtn').disabled = true;
                
                try {{
                    const response = await fetch('/api/chat/message', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            message: message,
                            session_id: chatSessionId,
                            token: sessionToken,
                            company: 'Demo Company'
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    // Remove typing indicator
                    removeTypingIndicator();
                    
                    if (result.success) {{
                        chatSessionId = result.session_id;
                        addMessageToChat('assistant', result.response, result.agent);
                        updateAgentIndicator(result.agent, result.confidence);
                    }} else {{
                        addMessageToChat('assistant', 'Sorry, I encountered an error. Please try again.', 'error');
                    }}
                }} catch (error) {{
                    removeTypingIndicator();
                    addMessageToChat('assistant', 'Failed to connect to the chat service.', 'error');
                    console.error('Chat error:', error);
                }} finally {{
                    document.getElementById('sendBtn').disabled = false;
                }}
            }}
            
            function addMessageToChat(role, content, agent) {{
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `chat-message ${{role}}`;
                
                const bubble = document.createElement('div');
                bubble.className = 'message-bubble';
                bubble.textContent = content;
                
                messageDiv.appendChild(bubble);
                
                if (role === 'assistant' && agent) {{
                    const meta = document.createElement('div');
                    meta.className = 'message-meta';
                    meta.textContent = `Answered by: ${{agent}} agent`;
                    messageDiv.appendChild(meta);
                }}
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }}
            
            function showTypingIndicator() {{
                const chatMessages = document.getElementById('chatMessages');
                const indicator = document.createElement('div');
                indicator.id = 'typingIndicator';
                indicator.className = 'chat-message assistant';
                indicator.innerHTML = `
                    <div class="typing-indicator">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                    </div>
                `;
                chatMessages.appendChild(indicator);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }}
            
            function removeTypingIndicator() {{
                const indicator = document.getElementById('typingIndicator');
                if (indicator) indicator.remove();
            }}
            
            function updateAgentIndicator(agent, confidence) {{
                const indicator = document.getElementById('agentIndicator');
                const confidencePercent = Math.round(confidence * 100);
                indicator.innerHTML = `🤖 Responded by <strong>${{agent}}</strong> agent ({{confidencePercent}}% confidence)`;
            }}
            
            function askSuggestion(button) {{
                const input = document.getElementById('chatInput');
                input.value = button.textContent;
                sendChatMessage();
            }}
        </script>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


def main():
    """Run the application."""
    uvicorn.run(
        "src.solutions.resume_dashboard.main:app",
        host="0.0.0.0",
        port=9001,
        reload=True
    )


if __name__ == "__main__":
    main()