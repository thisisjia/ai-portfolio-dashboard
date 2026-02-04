# Architecture Overview

## Executive Summary

Token-gated interactive resume dashboard featuring a multi-agent AI chat system, live SQL demonstrations, and visitor analytics. Built with modern web technologies and deployed on AWS infrastructure.

**Live Demo:** [Contact for access token]

---

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **AI/ML:** LangChain, Groq API (llama-3.3-70b-versatile)
- **Database:** SQLite (easily upgradable to PostgreSQL)
- **API:** RESTful + Server-Sent Events (SSE) for streaming

### Frontend
- **Framework:** Next.js 15 (React 19)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Build:** Turbopack

### Infrastructure
- **Deployment:** Docker + Docker Compose
- **Web Server:** Nginx (reverse proxy)
- **Platform:** AWS EC2 (t2.micro)
- **SSL/TLS:** Let's Encrypt (Certbot)
- **Domain:** Cloudflare DNS

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Cloudflare │
                    │   DNS + CDN  │
                    └──────┬───────┘
                           │
                    ┌──────▼──────┐
                    │  AWS EC2    │
                    │  t2.micro   │
                    │             │
      ┌─────────────┼─────────────┼─────────────┐
      │             │   Nginx     │             │
      │             │  (Port 80/  │             │
      │             │   443)      │             │
      │             └──────┬──────┘             │
      │                    │                     │
      │         ┌──────────┴──────────┐         │
      │         │                     │         │
      │  ┌──────▼──────┐      ┌──────▼──────┐  │
      │  │  Frontend   │      │  Backend    │  │
      │  │  Container  │      │  Container  │  │
      │  │  Next.js    │      │  FastAPI    │  │
      │  │  Port 3000  │      │  Port 9001  │  │
      │  └─────────────┘      └──────┬──────┘  │
      │                              │          │
      │                       ┌──────▼──────┐  │
      │                       │   SQLite    │  │
      │                       │  Database   │  │
      │                       └──────┬──────┘  │
      │                              │          │
      └──────────────────────────────┼──────────┘
                                     │
                              ┌──────▼──────┐
                              │  Groq API   │
                              │  (External) │
                              └─────────────┘
```

---

## Key Design Decisions

### 1. Multi-Agent AI Architecture

**Challenge:** Generic chatbots provide shallow, unfocused responses.

**Solution:** Implemented a router-based multi-agent system with 6 specialized agents:

- **Router Agent:** Analyzes user intent and routes to appropriate specialist
- **Help Agent:** Handles meta-questions about the system
- **Personal Agent:** Discusses personality, interests, motivation
- **Technical Agent:** Deep dives into technical skills, languages, tools
- **Background Agent:** Covers education, work history, achievements
- **Interview Agent:** Behavioral questions, work style, examples

**Benefits:**
- Higher quality, contextually relevant responses
- Confidence scoring for routing decisions
- Easier to maintain and extend specific domains
- Better logging and analytics per topic

**Implementation:**
```python
# backend/src/solutions/resume_dashboard/agents/router.py
class RouterAgent(BaseAgent):
    def route(self, message: str) -> str:
        # LLM analyzes intent and returns agent name
        return self.llm.invoke(prompt).content.strip()
```

### 2. Groq API vs Local LLM (Ollama)

**Initial Approach:** Ollama running llama3.2 locally

**Problem:**
- Required 4GB+ RAM
- Forced upgrade to t2.medium ($24/month → $36/month)
- Slower inference times

**Final Solution:** Groq Cloud API with llama-3.3-70b-versatile

**Benefits:**
- Runs on t2.micro (1GB RAM) - saves ~$27/month
- Faster inference (300+ tokens/sec)
- Better model quality (70B vs 3B parameters)
- Free tier: 30 req/min, 6000 tokens/min

**Trade-offs:**
- External dependency (mitigated by error handling)
- Rate limits (acceptable for portfolio demo)

**Alternative Considered: Qwen (smallest model)**
- Tested Qwen as minimal local LLM
- Still required significant disk space for model download
- AWS free tier constraints made local hosting impractical

### 3. No RAG/Vector Search (Memory Constraints)

**Original Design:** Hybrid search with embeddings + BM25 + RRF

**Planned Implementation:**
```python
# Implemented in embeddings.py (kept as reference)
- Ollama embeddings with nomic-embed-text (500MB)
- Cosine similarity for semantic search
- BM25-like keyword matching for exact matches
- Reciprocal Rank Fusion (RRF) for result merging
- Hybrid scoring: semantic_weight * cosine + keyword_weight * BM25
```

**Why Not Deployed:**

**Memory Breakdown (AWS t2.micro - 1GB total):**
```
nomic-embed-text model:     ~500 MB
Ollama service overhead:    ~300 MB
FastAPI + dependencies:     ~200 MB
SQLite + OS services:       ~200 MB
-------------------------------------------
Required:                   ~1.2 GB
Available:                   1.0 GB  ❌
```

**Alternatives Evaluated:**

| Model | Memory | Why Not Used |
|-------|--------|-------------|
| **EmbeddingGemma-300M** (quantized) | <200MB | Still need Ollama (~300MB) = ~500MB total |
| **all-MiniLM-L6-v2** | 43MB | Need sentence-transformers library (~200MB) |
| **nomic-embed-text** | 500MB | Original choice, too large |
| **mxbai-embed-large** | 1.2GB | Best quality, but exceeds t2.micro entirely |

Even the smallest viable option (EmbeddingGemma + infrastructure) would consume ~700-800MB, leaving minimal headroom for traffic spikes or OS overhead.

**Final Decision:**
- Use **direct context injection** - entire resume (~5KB) fits in LLM context window
- Keep `embeddings.py` as reference implementation (demonstrates RAG expertise)
- Multi-agent routing provides intelligent query handling without embeddings
- **Saves ~$27/month** by staying on t2.micro vs t2.medium

**Trade-Offs Accepted:**
- Works for current scale: Single resume easily fits in context
- Not scalable: Cannot handle 100+ documents without RAG
- No semantic search capability: Relies on LLM's attention mechanism only
- Forced by memory constraints: No choice for AWS free tier MVP
- Acceptable for portfolio demo: Single-user use case doesn't require document retrieval

**When RAG Would Be Required:**
- Multiple resumes (multi-tenant system)
- Large document library (100+ items exceeding context window)
- External knowledge base integration
- Would necessitate upgrade to t2.medium+ for embedding infrastructure

### 4. Token-Based Authentication

**Why not OAuth/Social Login?**
- Portfolio use case: controlled access for recruiters
- Each company gets unique token for tracking
- Company domain tracking for analytics
- Simple implementation, no session management complexity

**Security Features:**
- Tokens hashed with SHA-256 before storage
- IP address logging for security audit
- Admin dashboard protected by separate bearer token
- CORS restrictions to prevent unauthorized domains

**Implementation:**
```python
# backend/src/solutions/resume_dashboard/nodes/auth.py
class TokenAuthNode:
    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
```

### 4. SQLite vs PostgreSQL

**Current:** SQLite with async support (aiosqlite)

**Why SQLite for MVP:**
- Zero configuration
- File-based (easy backups)
- Sufficient for demo traffic
- Built into Python

**Migration Path to Postgres:**
```python
# Already abstracted in DatabaseManager
# Change: DATABASE_URL=postgresql://...
# Schema compatible, just update connection string
```

**When to migrate:**
- Traffic > 1000 concurrent users
- Need for advanced indexing
- Multi-region deployment

### 5. Separate Docker Containers

**Frontend & Backend in separate containers:**

**Why?**
- **Independent scaling:** Can add more frontend replicas for traffic spikes
- **Development velocity:** Update UI without restarting backend
- **Technology isolation:** Node.js and Python don't conflict
- **Security:** Frontend can't directly access database

**Communication:**
- Frontend calls backend via Nginx reverse proxy
- CORS configured for cross-origin requests
- Environment variables control API endpoints

**Build Optimization:**
```dockerfile
# Multi-stage builds reduce image size
FROM node:18-alpine AS builder  # Build stage
FROM node:18-alpine AS runner   # Runtime stage (smaller)
```

### 6. Nginx Reverse Proxy

**Why not direct container exposure?**

**Benefits:**
- **SSL termination:** Single place for HTTPS certificates
- **Load balancing:** Can add backend replicas easily
- **Security:** Hides internal container IPs
- **Caching:** Static assets cached at Nginx layer
- **Compression:** Gzip responses automatically

**Configuration:**
```nginx
location /api/ {
    proxy_pass http://backend:9001;
}
location / {
    proxy_pass http://frontend:3000;
}
```

---

## Database Schema

### Tokens Table
```sql
CREATE TABLE tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT UNIQUE NOT NULL,
    company TEXT,
    company_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);
```

**Indexes:**
- `token_hash` (UNIQUE) - Fast authentication lookups
- `company` - Analytics queries by company
- `last_accessed` - Recent visitor queries

---

## Security Considerations

### Implemented
- ✅ Environment variables for secrets (no hardcoded keys)
- ✅ `.env` in `.gitignore` (never committed)
- ✅ Token hashing (SHA-256)
- ✅ CORS restrictions
- ✅ SSH key-based authentication
- ✅ AWS Security Group (IP whitelisting)
- ✅ HTTPS only (Let's Encrypt)

### Future Enhancements
- 🔲 Rate limiting (per IP/token)
- 🔲 SQL injection protection (parameterized queries already used)
- 🔲 DDoS protection (Cloudflare Pro)
- 🔲 Secrets rotation policy
- 🔲 Database encryption at rest

---

## Deployment Strategy

### Build Process

**Problem:** t2.micro (1GB RAM) crashes during Next.js builds

**Solution:** Build locally, transfer to EC2

```bash
# Local (MacBook - ARM64)
docker build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_API_URL=https://thisisjia.com \
  -t resume-frontend:latest .

# Save and compress
docker save resume-frontend:latest | gzip > frontend.tar.gz

# Transfer to EC2
scp frontend.tar.gz ubuntu@server:/tmp/
ssh ubuntu@server "docker load < /tmp/frontend.tar.gz"
```

### Zero-Downtime Updates

```bash
# Build new version
docker compose build backend

# Rolling restart
docker compose up -d --no-deps --build backend

# Nginx handles requests during restart
```

---

## Performance Optimizations

1. **Frontend:**
   - Next.js 15 with Turbopack (faster builds)
   - Static asset caching (Nginx)
   - Image optimization (Next.js built-in)

2. **Backend:**
   - Async database queries (aiosqlite)
   - Connection pooling
   - Response streaming for chat (SSE)

3. **Database:**
   - Indexes on frequently queried columns
   - Prepared statements (SQL injection prevention + speed)

---

## Cost Analysis

### Current Monthly Costs (AWS t2.micro)

| Service | Cost |
|---------|------|
| EC2 t2.micro (750hr free tier) | $0 (first year) → $8.50/month after |
| EBS Storage (8GB) | $0.80/month |
| Data Transfer (1GB out) | $0.09/GB |
| **Total** | **~$1/month** (first year) → **~$10/month** after |

### If using t2.medium instead (with local Ollama)

| Service | Cost |
|---------|------|
| EC2 t2.medium | $33.87/month |
| **Savings with Groq API** | **~$27/month** |

---

## Scalability Roadmap

### Current (MVP): Single EC2 Instance
- Traffic: <1000 visitors/month
- Latency: <500ms average

### Phase 2: Horizontal Scaling
```yaml
docker-compose.yml:
  backend:
    deploy:
      replicas: 3  # Multiple backend instances
```

### Phase 3: Cloud Migration
- **Database:** RDS PostgreSQL (managed)
- **Load Balancer:** AWS ALB
- **Autoscaling:** Based on CPU/memory
- **CDN:** CloudFront for static assets

---

## Developer Experience

### Local Development

```bash
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm run dev

# Full stack with Docker
docker compose up
```

### Testing Strategy

```bash
# Backend tests
pytest backend/tests/

# Type checking
mypy backend/src/

# Linting
ruff check backend/
```

---

## Lessons Learned

1. **Start small, scale smart:** SQLite → Postgres when needed
2. **Cloud APIs > Self-hosting:** Groq API saved $27/month vs Ollama
3. **Build locally for constrained environments:** t2.micro can't build Next.js
4. **Multi-agent systems >>> Single chatbot:** Better quality, easier maintenance
5. **Environment variables from day 1:** Don't hardcode secrets, even in private repos

---

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Redis caching layer
- [ ] Feedback collection with computer vision (MediaPipe)
- [ ] Live API integrations (market data, GitHub stats)
- [ ] A/B testing framework for UI experiments
- [ ] Analytics dashboard expansion (time-series charts)

---

## Contact

For access token or technical questions about this project, please reach out via [your contact method].

**Tech Stack Summary:** Python • FastAPI • Next.js • TypeScript • LangChain • Docker • AWS • Nginx
