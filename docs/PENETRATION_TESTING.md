# 🔒 Penetration Testing Guide

Security testing checklist and scripts for the Resume Dashboard.

---

## 📋 Pre-Test Checklist

- [ ] Testing on staging/local environment (NOT production)
- [ ] Have written permission if testing external systems
- [ ] Backups created before destructive tests
- [ ] Test credentials ready (not production credentials)

---

## 🎯 Test Categories

### 1. Authentication & Authorization

#### Test 1.1: Token Authentication Bypass
```bash
# Test: Can we access without token?
curl https://thisisjia.com/api/chat/message

# Expected: 401 Unauthorized or token required error
```

#### Test 1.2: Invalid Token Handling
```bash
# Test: What happens with invalid token?
curl -X POST https://thisisjia.com/auth/token \
  -H "Content-Type: application/json" \
  -d '{"token": "invalid_token", "company_domain": "test.com"}'

# Expected: {"authenticated": false, "error": "Invalid token"}
```

#### Test 1.3: SQL Injection in Token
```bash
# Test: SQL injection attempt
curl -X POST https://thisisjia.com/auth/token \
  -H "Content-Type: application/json" \
  -d '{"token": "' OR '1'='1", "company_domain": "test.com"}'

# Expected: Authentication fails (parameterized queries protect against this)
```

#### Test 1.4: Admin Token Brute Force
```bash
# Test: Can we brute force admin token?
for i in {1..100}; do
  curl -s -H "Authorization: Bearer admin$i" \
    https://thisisjia.com/admin/analytics \
    -w "\n%{http_code}\n"
done

# Expected: All return 403 Forbidden
# Warning: Should implement rate limiting to block this
```

---

### 2. Admin Dashboard Security

#### Test 2.1: Admin Access Without Token
```bash
# Test: Can we access admin without Bearer token?
curl https://thisisjia.com/admin/analytics

# Expected: 403 Unauthorized
```

#### Test 2.2: Admin Access With Wrong Token
```bash
# Test: Wrong admin token
curl -H "Authorization: Bearer wrongtoken" \
  https://thisisjia.com/admin/analytics

# Expected: 403 Unauthorized
```

#### Test 2.3: Admin Access With Correct Token
```bash
# Test: Valid admin token (use your real token)
curl -H "Authorization: Bearer adminjia0902" \
  https://thisisjia.com/admin/analytics

# Expected: 200 OK with analytics HTML
```

---

### 3. Input Validation & Injection

#### Test 3.1: XSS in Company Domain
```bash
# Test: Cross-site scripting attempt
curl -X POST https://thisisjia.com/auth/token \
  -H "Content-Type: application/json" \
  -d '{"token": "world", "company_domain": "<script>alert(1)</script>"}'

# Expected: Sanitized or rejected
```

#### Test 3.2: SQL Injection in Chat
```bash
# Test: SQL injection in chat message
curl -X POST https://thisisjia.com/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "'; DROP TABLE projects; --",
    "token": "world",
    "session_id": "test123"
  }'

# Expected: Query fails safely, no database modification
```

#### Test 3.3: NoSQL Injection
```bash
# Test: Object injection
curl -X POST https://thisisjia.com/auth/token \
  -H "Content-Type: application/json" \
  -d '{"token": {"$ne": null}, "company_domain": "test.com"}'

# Expected: Type error or validation failure
```

---

### 4. CORS & Origin Validation

#### Test 4.1: Cross-Origin Request
```bash
# Test: Request from unauthorized origin
curl -X POST https://thisisjia.com/api/chat/message \
  -H "Origin: https://evil.com" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "token": "world"}'

# Expected: CORS error (blocked by ALLOWED_ORIGINS)
```

#### Test 4.2: Allowed Origin
```bash
# Test: Request from allowed origin
curl -X POST https://thisisjia.com/api/chat/message \
  -H "Origin: https://thisisjia.com" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "token": "world"}'

# Expected: 200 OK
```

---

### 5. File & Path Traversal

#### Test 5.1: Directory Traversal
```bash
# Test: Can we access files outside web root?
curl https://thisisjia.com/../../../etc/passwd
curl https://thisisjia.com/..%2F..%2F..%2Fetc%2Fpasswd

# Expected: 404 Not Found
```

#### Test 5.2: Sensitive File Access
```bash
# Test: Can we access sensitive files?
curl https://thisisjia.com/.env
curl https://thisisjia.com/backend/.env
curl https://thisisjia.com/.git/config

# Expected: All return 404 (Nginx blocks these)
```

---

### 6. Rate Limiting & DoS

#### Test 6.1: API Rate Limiting
```bash
# Test: Rapid requests (basic DoS)
for i in {1..1000}; do
  curl -s https://thisisjia.com/api/chat/message \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "spam", "token": "world"}' &
done

# Expected: Should implement rate limiting (currently not implemented)
# Warning: This could crash the server - test on local only!
```

#### Test 6.2: Large Payload
```bash
# Test: Send huge message
python3 << 'EOF'
import requests
large_msg = "A" * 1000000  # 1MB message
r = requests.post("https://thisisjia.com/api/chat/message",
    json={"message": large_msg, "token": "world"})
print(r.status_code)
EOF

# Expected: 413 Payload Too Large or validation error
```

---

### 7. Information Disclosure

#### Test 7.1: Error Messages
```bash
# Test: Do error messages leak info?
curl https://thisisjia.com/nonexistent
curl -X POST https://thisisjia.com/api/chat/message

# Expected: Generic errors, no stack traces or DB info
```

#### Test 7.2: API Endpoints Discovery
```bash
# Test: Can we find hidden endpoints?
curl https://thisisjia.com/docs
curl https://thisisjia.com/api/docs
curl https://thisisjia.com/swagger
curl https://thisisjia.com/openapi.json

# Expected: /docs should be accessible (FastAPI feature)
# Consider: Disable in production or add auth
```

#### Test 7.3: Security Headers
```bash
# Test: Are security headers present?
curl -I https://thisisjia.com

# Should have:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Strict-Transport-Security: max-age=31536000
```

---

### 8. SSL/TLS Security

#### Test 8.1: SSL Certificate Validation
```bash
# Test: Valid SSL certificate
openssl s_client -connect thisisjia.com:443 -servername thisisjia.com

# Expected: Valid certificate, no warnings
```

#### Test 8.2: Weak Ciphers
```bash
# Test: Check for weak SSL ciphers
nmap --script ssl-enum-ciphers -p 443 thisisjia.com

# Expected: Only strong ciphers (TLS 1.2+)
```

#### Test 8.3: HTTP Strict Transport Security
```bash
# Test: HSTS header present
curl -I https://thisisjia.com | grep -i strict

# Expected: Strict-Transport-Security header present
```

---

### 9. Session Management

#### Test 9.1: Session Fixation
```bash
# Test: Can we set our own session ID?
curl -X POST https://thisisjia.com/auth/token \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=attacker_session" \
  -d '{"token": "world", "company_domain": "test.com"}'

# Expected: Server generates its own session ID
```

#### Test 9.2: Session Hijacking
```bash
# Test: Can we reuse someone else's session?
# (Need valid session_id from network traffic)
curl https://thisisjia.com/api/chat/message \
  -H "Cookie: session_id=stolen_session_id"

# Expected: Session validation or timeout
```

---

### 10. Network Scans

#### Test 10.1: Port Scanning
```bash
# Test: What ports are open?
nmap -sV 47.129.65.64

# Expected: Only 22 (SSH), 80 (HTTP), 443 (HTTPS)
# SSH should be restricted to your IP
```

#### Test 10.2: Service Enumeration
```bash
# Test: What services are running?
nmap -sV -O 47.129.65.64

# Expected: Nginx, OpenSSH, no other exposed services
```

---

## 🛡️ Automated Security Scanners

### OWASP ZAP (Zed Attack Proxy)
```bash
# Install OWASP ZAP
brew install --cask owasp-zap  # macOS
# or download from https://www.zaproxy.org/

# Run automated scan
zap-cli quick-scan https://thisisjia.com
```

### SQLMap (SQL Injection Testing)
```bash
# Install SQLMap
pip install sqlmap

# Test token endpoint for SQL injection
sqlmap -u "https://thisisjia.com/auth/token" \
  --method POST \
  --data '{"token":"test","company_domain":"test.com"}' \
  --batch

# Expected: No SQL injection vulnerabilities found
```

### Nikto (Web Server Scanner)
```bash
# Install Nikto
brew install nikto  # macOS

# Scan web server
nikto -h https://thisisjia.com

# Review findings and fix issues
```

---

## 📊 Results Template

### Test Summary
| Test Category | Tests Run | Passed | Failed | Severity |
|---------------|-----------|--------|--------|----------|
| Authentication | 4 | 4 | 0 | - |
| Admin Access | 3 | 3 | 0 | - |
| Input Validation | 3 | 2 | 1 | Medium |
| CORS | 2 | 2 | 0 | - |
| File Access | 2 | 2 | 0 | - |
| Rate Limiting | 2 | 0 | 2 | **HIGH** |
| Info Disclosure | 3 | 2 | 1 | Low |
| SSL/TLS | 3 | 3 | 0 | - |
| Session Mgmt | 2 | 2 | 0 | - |
| Network | 2 | 2 | 0 | - |

### Critical Findings

**HIGH: No Rate Limiting**
- **Issue:** Unlimited API requests possible
- **Impact:** DDoS vulnerability
- **Fix:** Implement rate limiting (e.g., 100 req/min per IP)

**MEDIUM: API Docs Exposed**
- **Issue:** `/docs` endpoint accessible without auth
- **Impact:** Information disclosure
- **Fix:** Add authentication or disable in production

---

## 🔧 Recommended Fixes

### 1. Add Rate Limiting
```python
# backend/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat/message")
@limiter.limit("60/minute")
async def chat_message(...):
    ...
```

### 2. Secure API Docs
```python
# backend/main.py
from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_docs(admin_token: str = Header(None)):
    if admin_token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(403, "Unauthorized")
    return get_swagger_ui_html(...)
```

### 3. Add Security Headers
```nginx
# nginx/nginx.conf
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 4. Input Sanitization
```python
# Add input validation
from pydantic import BaseModel, validator

class ChatMessage(BaseModel):
    message: str

    @validator('message')
    def validate_message(cls, v):
        if len(v) > 5000:
            raise ValueError('Message too long')
        # Add HTML/script tag filtering if needed
        return v.strip()
```

---

## 📚 Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Web Security Testing**: https://owasp.org/www-project-web-security-testing-guide/
- **Penetration Testing Tools**: https://www.kali.org/tools/
- **Bug Bounty Programs**: HackerOne, Bugcrowd (for learning)

---

## ⚠️ Legal Disclaimer

**Only test systems you own or have explicit written permission to test.**

Unauthorized penetration testing is illegal and can result in criminal charges.

---

**Last Updated:** 2025-12-08
**Tested By:** [Your Name]
**Environment:** Production (thisisjia.com)
