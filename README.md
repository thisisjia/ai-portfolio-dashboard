# 🎯 Token-Gated Interactive Resume Dashboard

A full-stack AI-powered portfolio platform with multi-agent chat, live SQL demonstrations, and visitor analytics. Built to showcase modern software engineering practices.

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

---

## ✨ Key Features

- **🤖 Multi-Agent AI Chat** - 6 specialized LangChain agents with intelligent routing and confidence scoring
- **💾 Live SQL Demos** - Interactive database queries with syntax highlighting on real resume data
- **🔐 Token Authentication** - Company-specific access with domain tracking and SHA-256 hashing
- **📊 Admin Analytics** - Visitor tracking dashboard with access metrics and insights
- **⚡ Production Ready** - Dockerized deployment on AWS EC2 with Nginx and SSL

---

## 🏗️ Architecture

```
Internet → Cloudflare → Nginx (SSL) → Frontend (Next.js) + Backend (FastAPI) → SQLite → Groq API
```

**Tech Stack:**
- **Backend:** Python, FastAPI, LangChain, Groq API (llama-3.3-70b)
- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS
- **Infrastructure:** Docker, Nginx, AWS EC2, Let's Encrypt

📖 **[Read full architecture decisions →](ARCHITECTURE.md)**

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- [Groq API Key](https://console.groq.com/keys) (free tier available)

### Setup

```bash
# 1. Clone and configure
git clone https://github.com/yourusername/resume-dashboard.git
cd resume-dashboard
cp .env.example .env

# 2. Edit .env with your values
# GROQ_API_KEY=your_key_here
# ADMIN_TOKEN=your_secure_token

# 3. Run
docker compose up -d

# 4. Access at http://localhost:3000
```

### API Documentation
- Interactive docs: `http://localhost:9001/docs`
- Admin analytics: `http://localhost:9001/admin/analytics` (requires Bearer token)

---

## 🎯 What This Project Demonstrates

| Skill Area | Implementation |
|------------|----------------|
| **AI/ML** | Multi-agent LLM system with LangChain, prompt engineering, confidence-based routing |
| **Backend** | Async FastAPI, RESTful API design, SSE streaming, database design |
| **Frontend** | Next.js 15 with App Router, TypeScript, responsive UI, real-time updates |
| **DevOps** | Docker multi-stage builds, Nginx reverse proxy, AWS deployment, SSL/TLS |
| **Security** | Token auth, secret management, CORS, input validation, penetration testing awareness |
| **Architecture** | Microservices, separation of concerns, scalability patterns, cost optimization |

---

## 💡 Design Highlights

### Multi-Agent AI System
Instead of one generic chatbot, implemented 6 specialized agents (Help, Technical, Personal, Background, Interview, Router) for higher quality, contextually relevant responses.

### Cost Optimization
Switched from local Ollama (4GB RAM, $36/month t2.medium) to Groq API, enabling deployment on $10/month t2.micro - **70% cost savings**.

### Security-First
- Environment-based secrets (never hardcoded)
- Token hashing before storage
- Admin dashboard with bearer token protection
- HTTPS-only with automated cert renewal

### Production-Ready Patterns
- Separate Docker containers for isolation and scaling
- Async database operations
- Response streaming for better UX
- Comprehensive error handling

---

## 📁 Project Structure

```
resume-dashboard/
├── backend/src/solutions/resume_dashboard/
│   ├── agents/          # 6 specialized AI agents
│   ├── routes/          # API endpoints (chat, SQL demos, admin)
│   ├── nodes/           # LangGraph workflow components
│   └── utils/           # Database, config, validators
├── frontend/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   └── lib/             # API client and utilities
├── docker-compose.yml
├── ARCHITECTURE.md      # Detailed technical decisions
└── README.md
```

---

## 🧪 Development

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m solutions.resume_dashboard

# Frontend
cd frontend
npm install
npm run dev

# Tests
pytest backend/tests/
```

---

## 🌐 Deployment

Deployed on **AWS EC2 t2.micro** (free tier eligible) with Docker, Nginx, and Let's Encrypt SSL.

**Note:** Build Next.js frontend locally for t2.micro instances (1GB RAM insufficient for builds):
```bash
docker build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_API_URL=https://yourdomain.com \
  -t resume-frontend ./frontend
```

Full deployment guide in [ARCHITECTURE.md](ARCHITECTURE.md#deployment-strategy)

---

## 📈 Performance & Scale

- **API Response:** <200ms average
- **LLM First Token:** <2s (streaming)
- **Current Load:** Handles 1000+ visitors/month on t2.micro
- **Scalability:** Ready for horizontal scaling with load balancer

---

## 🔒 Security

✅ Environment variables for secrets
✅ SHA-256 token hashing
✅ CORS restrictions
✅ HTTPS only
✅ IP logging for audit
✅ Input validation & parameterized queries

---

## 📝 License

Portfolio demonstration project. Feel free to reference for your own projects.

---

## 📧 Contact

**Looking for a full-stack engineer?**

- 📧 Email: [your-email]
- 💼 LinkedIn: [your-linkedin]
- 🌐 Live Demo: [Contact for access token]

---

**Tech Stack:** Python • FastAPI • LangChain • Next.js • TypeScript • Docker • AWS • PostgreSQL-ready

**Built to demonstrate:** Full-stack development • AI/ML integration • Cloud architecture • Production best practices
