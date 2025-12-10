# 🎯 AI Portfolio Dashboard

**A production-grade, token-gated portfolio platform with multi-agent AI chat, live SQL demonstrations, and visitor analytics.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-thisisjia.com-blue?style=for-the-badge)](https://thisisjia.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

> **Live Demo:** [thisisjia.com](https://thisisjia.com)

---

## ✨ Key Features

### 🤖 Multi-Agent AI Chat
- **6 specialized LangGraph agents** for different question types
- Intelligent intent routing with confidence scoring
- Real-time streaming responses via Server-Sent Events (SSE)
- Context-aware conversations about technical skills, background, and projects

### 💾 Interactive SQL Demonstrations
- Live queries on real resume data (projects, skills, experience)
- Syntax-highlighted SQL with execution results
- Complex query examples (JOINs, aggregations, window functions)

### 📊 Admin Analytics Dashboard
- **Real-time visitor tracking** by company domain and access patterns
- Visit frequency, timestamps, and engagement metrics
- Secure bearer token authentication for admin-only access
- Professional data visualizations with trend analysis

### 🔐 Token-Based Access Control
- Company-specific authentication tokens
- SHA-256 hashing for secure token storage
- Domain validation and logging
- Session management with analytics integration

---

## 🏗️ Architecture

```
Internet → Nginx (SSL) → Frontend (Next.js :3000)
                      ↓
                   Backend (FastAPI :9001)
                      ↓
                   SQLite Database
```

**Stack:**
- **Frontend:** Next.js 15, React 19, TypeScript, TailwindCSS
- **Backend:** FastAPI, Python 3.12, LangChain/LangGraph
- **AI:** Groq API (llama-3.3-70b-versatile)
- **Database:** SQLite with async (aiosqlite)
- **Deploy:** Docker Compose, Nginx, AWS EC2

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Groq API Key ([free signup](https://console.groq.com))

### Setup

```bash
# 1. Clone repository
git clone https://github.com/thisisjia/ai-portfolio-dashboard.git
cd ai-portfolio-dashboard

# 2. Configure environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY and other settings

# 3. Start services
docker compose up -d

# 4. Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:9001
# API Docs: http://localhost:9001/docs
# Admin: http://localhost:9001/admin/analytics (requires Bearer token)
```

---

## 📁 Project Structure

```
├── backend/
│   ├── src/solutions/resume_dashboard/
│   │   ├── agents/        # 6 specialized LangGraph agents
│   │   ├── routes/        # API endpoints (chat, sql_demo, admin)
│   │   ├── nodes/         # LangGraph workflow nodes
│   │   ├── utils/         # Database & config
│   │   └── main.py        # FastAPI app
│   └── Dockerfile
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/        # React components
│   └── Dockerfile
├── nginx/
│   └── nginx.conf         # Reverse proxy config
├── docker-compose.yml
└── .env.example
```

---

## 🔐 Security Features

- ✅ Token hashing (SHA-256)
- ✅ CORS restrictions
- ✅ HTTPS with Let's Encrypt
- ✅ Environment-based secret management
- ✅ Admin dashboard with bearer token auth
- ✅ IP logging for security audit

---

## 🌐 Deployment

**Recommended:** AWS EC2 t3.small (2GB RAM minimum for builds)

```bash
# On local machine - build frontend for AMD64
docker buildx build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_API_URL=https://yourdomain.com \
  -t frontend:prod ./frontend

# Stream to server
docker save frontend:prod | ssh user@server docker load

# On server
docker compose --profile production up -d
```

---

## 📊 API Examples

### Authentication
```bash
curl -X POST https://thisisjia.com/auth/token \
  -H "Content-Type: application/json" \
  -d '{"token":"your-token","company_domain":"company.com"}'
```

### Chat
```bash
curl -X POST https://thisisjia.com/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"What are your technical skills?","session_id":"uuid","token":"your-token"}'
```

### Admin Analytics
```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  https://thisisjia.com/admin/analytics
```

Full API docs: [thisisjia.com/docs](https://thisisjia.com/docs)

---

## 🎯 What This Demonstrates

**Full-Stack Development:**
- Async Python backend (FastAPI)
- Modern React/TypeScript frontend
- Docker multi-container orchestration
- Production deployment (AWS, Nginx, SSL)

**AI/ML Engineering:**
- Multi-agent LangGraph architecture
- LLM prompt engineering
- Intent classification & routing
- Streaming responses

**System Design:**
- Token-based authentication
- Visitor analytics pipeline
- Database schema design
- API architecture

---

## 🧪 Development

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m solutions.resume_dashboard
pytest

# Frontend
cd frontend
npm install
npm run dev
npm run type-check
```

---

## 📧 Contact

**Jiajia M.**
- 🌐 [thisisjia.com](https://thisisjia.com)
- 💼 [LinkedIn](https://www.linkedin.com/in/mjiajia/)
- 🐙 [GitHub](https://github.com/thisisjia)
- 📧 m.jiajia@gmail.com

---

## 📝 License

MIT License - Feel free to use as reference for your own projects.

---

**Built to showcase modern full-stack AI engineering** 🚀
