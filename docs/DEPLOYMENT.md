# 🚀 Resume Dashboard Deployment Guide

Complete guide for deploying your Token-Gated Resume Dashboard to production.

---

## Quick Start Options

Choose your deployment method:

1. **[AWS EC2 with Docker](#aws-ec2-deployment)** (Recommended) - Full control, ~$40/month
2. **[Platform-as-a-Service](#paas-deployment)** (Easiest) - Vercel + Railway, mostly free

---

# AWS EC2 Deployment

Complete walkthrough for deploying to AWS EC2 with Docker, Nginx, and SSL.

## Prerequisites

- AWS Account (Free tier eligible - 12 months free)
- Domain name (e.g., thisisjia.com) via Cloudflare (~$10/year) or AWS Route 53
- SSH key pair for EC2 access
- 2-3 hours for complete setup

## Architecture

```
Internet → DNS (Cloudflare) → AWS EC2
                                ├─ Nginx (SSL termination, reverse proxy)
                                ├─ Frontend (Next.js - port 3000)
                                ├─ Backend (FastAPI - port 9001)
                                └─ Database (SQLite)
```

---

## Part 1: AWS EC2 Setup

### 1.1 Launch EC2 Instance

1. Go to [AWS Console](https://console.aws.amazon.com/) → EC2 → **Launch Instance**

2. **Configure**:
   - **Name**: `resume-dashboard`
   - **AMI**: Ubuntu 22.04 LTS (Free tier eligible)
   - **Instance type**: `t2.small` or `t3.small` (minimum 2GB RAM for builds)
     - t2.micro (1GB) is too small for Next.js builds
   - **Key pair**: Create new or select existing
   - **Storage**: 30 GB (free tier max)

3. **Security Group Rules** (IMPORTANT):
   ```
   SSH  (22)   - Your IP only
   HTTP (80)   - 0.0.0.0/0 (anywhere)
   HTTPS (443) - 0.0.0.0/0 (anywhere)
   ```

4. **Launch** and note your **Public IPv4 address**

### 1.2 Connect to Instance

```bash
chmod 400 ~/Downloads/your-key.pem
ssh -i ~/Downloads/your-key.pem ubuntu@YOUR_EC2_IP
```

---

## Part 2: Server Setup

### 2.1 Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Log out and back in for group changes
exit
# Reconnect
ssh -i ~/Downloads/your-key.pem ubuntu@YOUR_EC2_IP

# Verify
docker --version
docker compose version
```

### 2.2 Clone Repository

```bash
# Install git
sudo apt install git -y

# Clone your repo
cd ~
git clone https://github.com/YOUR_USERNAME/resume-dashboard.git
cd resume-dashboard
```

---

## Part 3: Configuration

### 3.1 Environment Variables

Edit `.env` file:

```bash
nano .env
```

Update for production:

```env
# Domain Configuration
DOMAIN_URL=https://thisisjia.com
ALLOWED_ORIGINS=https://thisisjia.com,http://localhost:3000

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Backend
PYTHONPATH=/app/src
PYTHONUNBUFFERED=1
DATABASE_PATH=/app/data/resume.db
DATABASE_URL=sqlite:///./data/resume.db

# Frontend
NEXT_PUBLIC_API_URL=https://thisisjia.com
NODE_ENV=production
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENVIRONMENT=production

# LLM Configuration
USE_LOCAL_LLM=false
LLM_MODEL=llama-3.3-70b-versatile

# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Admin Security
ADMIN_TOKEN=your_secure_admin_token_here
```

**IMPORTANT**:
- Replace `GROQ_API_KEY` with your actual API key
- Change `ADMIN_TOKEN` to a secure random string
- Update `DOMAIN_URL` and `NEXT_PUBLIC_API_URL` to your domain

---

## Part 4: DNS Configuration

### Using Cloudflare (Recommended)

1. Go to [Cloudflare](https://dash.cloudflare.com/)
2. Select your domain → **DNS** → **Records**
3. Add A record:
   ```
   Type: A
   Name: @ (or subdomain)
   IPv4 address: YOUR_EC2_PUBLIC_IP
   Proxy status: DNS only (gray cloud)
   TTL: Auto
   ```

4. Wait 5-10 minutes for DNS propagation

5. Verify:
   ```bash
   nslookup thisisjia.com
   # Should show your EC2 IP
   ```

---

## Part 5: Deployment

### 5.1 Initial Build (Local Machine)

**IMPORTANT**: Build frontend locally to avoid overloading the server.

On your local machine:

```bash
# Build frontend image for AMD64 platform
docker buildx build --platform linux/amd64 \
  -t resume-dashboard-frontend:prod \
  -f frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=https://thisisjia.com \
  --load frontend

# Stream image to server
docker save resume-dashboard-frontend:prod | \
  ssh -i ~/Downloads/your-key.pem ubuntu@YOUR_EC2_IP "docker load"
```

### 5.2 Start Services (On Server)

```bash
# SSH into server
ssh -i ~/Downloads/your-key.pem ubuntu@YOUR_EC2_IP
cd ~/resume-dashboard

# Tag the loaded image
docker tag resume-dashboard-frontend:prod resume-dashboard-frontend:latest

# Start with production profile (includes nginx + SSL)
docker compose --profile production up -d

# Check status
docker compose --profile production ps

# View logs
docker compose logs -f
```

### 5.3 SSL Certificate Setup

```bash
# Get SSL certificate
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  -d thisisjia.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email

# Restart nginx
docker compose restart nginx
```

**Alternative (if webroot fails)**:
```bash
# Stop nginx temporarily
docker compose stop nginx

# Run standalone
docker compose run --rm certbot certonly \
  --standalone \
  -d thisisjia.com \
  --email your-email@example.com \
  --agree-tos

# Restart services
docker compose --profile production up -d
```

---

## Part 6: Verification

### 6.1 Health Checks

```bash
# Backend health
curl https://thisisjia.com/health
# Expected: {"status":"healthy"}

# Check all containers
docker compose --profile production ps
# All should show "Up"
```

### 6.2 Test in Browser

Visit `https://thisisjia.com`:
- ✅ SSL padlock appears
- ✅ Token auth page loads
- ✅ Chat functionality works
- ✅ Admin analytics accessible

---

## Part 7: Maintenance

### Daily Operations

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx

# Restart services
docker compose restart backend
docker compose restart frontend

# Full restart
docker compose --profile production down
docker compose --profile production up -d
```

### Update Application

```bash
cd ~/resume-dashboard

# Pull latest code
git pull origin main

# Rebuild (on local machine, then stream to server)
# OR build on server if you have enough resources:
docker compose build backend
# For frontend, use the local build + stream method

# Restart
docker compose --profile production up -d
```

### SSL Certificate Renewal

Add to crontab:
```bash
crontab -e
# Add:
0 0 */3 * * docker compose run --rm certbot renew && docker compose restart nginx
```

---

## Part 8: Security

### Firewall Setup

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Security Best Practices

1. **Restrict SSH access** to your IP only (in AWS Security Group)
2. **Change admin token** regularly
3. **Keep system updated**: `sudo apt update && sudo apt upgrade`
4. **Monitor logs** for suspicious activity
5. **Backup database** regularly

---

## Troubleshooting

### Frontend Container Fails

**Issue**: Container keeps restarting with "exec format error"
- **Cause**: ARM64 image on AMD64 server
- **Fix**: Build locally with `--platform linux/amd64` and stream to server

### CORS Errors

**Issue**: Frontend can't reach backend
- Check `ALLOWED_ORIGINS` in `.env`
- Verify `NEXT_PUBLIC_API_URL` is correct
- Rebuild frontend if URL changed

### 502 Bad Gateway

**Issue**: Nginx can't reach backend/frontend
```bash
# Check container status
docker compose ps

# Check logs
docker compose logs backend
docker compose logs frontend

# Restart services
docker compose restart
```

### SSL Certificate Issues

```bash
# Check certificate
sudo certbot certificates

# Force renewal
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d thisisjia.com \
  --force-renewal
```

### Out of Memory

```bash
# Check memory
free -h

# Add swap space (2GB)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

# PaaS Deployment

Quick deployment to Platform-as-a-Service providers (easier but less control).

## Option: Vercel (Frontend) + Railway (Backend)

### Frontend → Vercel

1. Push to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project
3. Select your repo, set root to `frontend`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = Your Railway backend URL
5. Deploy!

### Backend → Railway

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select repo, set root to `backend`
4. Railway auto-detects Python
5. Get your backend URL from Railway dashboard
6. Update Vercel frontend with this URL

### Costs
- Vercel: Free for personal use
- Railway: Free tier (500 hours/month)
- **Total**: Can run completely free!

---

## Cost Breakdown

### AWS EC2 Deployment
- **t2.small/t3.small**: ~$15-20/month
- **Storage (30GB)**: ~$3/month
- **Data transfer**: ~$1-5/month
- **Domain (Cloudflare)**: $10/year
- **Total**: ~$20-30/month

### Free Tier
- First 12 months: t2.micro free (but not enough for builds)
- After free tier: Switch to t3.small (~$15/month)

---

## Quick Reference Commands

```bash
# SSH into server
ssh -i ~/Downloads/your-key.pem ubuntu@YOUR_EC2_IP

# Check status
docker compose --profile production ps

# View logs
docker compose logs -f

# Restart all
docker compose --profile production down
docker compose --profile production up -d

# Update application
git pull && docker compose build && docker compose --profile production up -d

# Check SSL certificate
docker compose run --rm certbot certificates

# Monitor resources
docker stats
free -h
df -h
```

---

## Support

### Common Commands

| Task | Command |
|------|---------|
| View logs | `docker compose logs -f backend` |
| Restart service | `docker compose restart backend` |
| Check health | `curl https://thisisjia.com/health` |
| Update app | `git pull && docker compose build` |
| Renew SSL | `docker compose run --rm certbot renew` |

### Resources

- [Docker Docs](https://docs.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Cloudflare Docs](https://developers.cloudflare.com/)

---

## Next Steps

After deployment:

1. ✅ Test all functionality thoroughly
2. ✅ Add domain to resume and LinkedIn
3. ✅ Set up billing alerts in AWS
4. ✅ Schedule regular backups
5. ✅ Monitor logs for errors
6. ✅ Share with potential employers!

---

**Your resume dashboard is now live!** 🎉

Visit `https://thisisjia.com` and start impressing recruiters with your AI-powered portfolio.
