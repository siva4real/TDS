# Security Policy

## Supported Versions

We take security seriously. The following versions are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

### DO NOT

- Open a public GitHub issue for security vulnerabilities
- Discuss the vulnerability publicly before it's fixed
- Exploit the vulnerability beyond confirming its existence

### DO

1. **Email the details** to: security@yourdomain.com (or open a private security advisory on GitHub)
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. **Wait** for acknowledgment (within 48 hours)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next release cycle

## Security Best Practices

### For API Operators

#### 1. Secret Management

**DO:**

- Use strong, random secrets (min 32 characters)
- Rotate secrets regularly (every 90 days)
- Store secrets in environment variables or secret management systems
- Use different secrets for development and production

**DON'T:**

- Commit secrets to version control
- Share secrets via email or chat
- Use simple or predictable secrets
- Reuse secrets across environments

```bash
# Generate strong secret
openssl rand -base64 32
```

#### 2. API Keys

**GitHub Token:**

- Use fine-grained personal access tokens
- Grant only necessary permissions (`repo`, `read:org`)
- Set expiration dates
- Rotate regularly

**OpenAI API Key:**

- Set usage limits
- Monitor usage regularly
- Use separate keys for dev/prod
- Implement rate limiting

#### 3. Network Security

**Use HTTPS:**

```nginx
# Force HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... rest of config
}
```

**Implement Rate Limiting:**

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;
limit_req zone=api_limit burst=5 nodelay;
```

**Use Firewall:**

```bash
# Only allow specific ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

#### 4. Server Hardening

**Keep System Updated:**

```bash
sudo apt update && sudo apt upgrade -y
```

**Disable Root Login:**

```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
```

**Run as Non-Root User:**

```ini
# deployment-api.service
User=www-data
Group=www-data
```

**Set File Permissions:**

```bash
chmod 600 .env
chmod 755 app.py
chmod 644 requirements.txt
```

### For API Users

#### 1. Protect Your Secret

```python
# ✓ Good: Use environment variables
import os
secret = os.getenv("API_SECRET")

# ✗ Bad: Hardcode in code
secret = "my_secret_code"  # Never do this!
```

#### 2. Validate Responses

```python
def deploy_safely(data):
    try:
        response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()

        # Validate response structure
        result = response.json()
        required_fields = ["status", "repo_url", "pages_url"]
        if not all(field in result for field in required_fields):
            raise ValueError("Invalid response structure")

        # Validate URLs
        if not result["repo_url"].startswith("https://github.com/"):
            raise ValueError("Invalid repo URL")

        return result
    except Exception as e:
        # Log error securely (don't expose secrets)
        logger.error(f"Deployment failed: {type(e).__name__}")
        raise
```

#### 3. Secure Callback Endpoints

```python
from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    # Verify the request is from your API
    # (Implement signature verification if available)

    # Validate JSON structure
    if not request.is_json:
        abort(400, "Invalid content type")

    data = request.json
    required_fields = ["email", "task", "round", "nonce",
                       "repo_url", "commit_sha", "pages_url"]

    if not all(field in data for field in required_fields):
        abort(400, "Missing required fields")

    # Process securely
    # ...

    return {"status": "received"}, 200
```

## Known Security Considerations

### 1. In-Memory Storage

**Issue**: Repository mappings are stored in memory and lost on restart.

**Impact**: Medium - No data persistence

**Mitigation**:

- Implement database storage (planned for v2.0)
- Use Redis for session management
- Implement backup/restore functionality

### 2. No Built-In Rate Limiting (Application Level)

**Issue**: Application doesn't implement per-user rate limiting.

**Impact**: Medium - Potential for abuse

**Mitigation**:

- Use Nginx/API Gateway rate limiting (documented)
- Implement API key system (planned)
- Monitor usage and block abusive IPs

### 3. GitHub Token Exposure Risk

**Issue**: If server is compromised, GitHub token could be accessed.

**Impact**: High - Could affect GitHub repositories

**Mitigation**:

- Use environment variables (not files)
- Set proper file permissions (600)
- Use minimal token permissions
- Rotate tokens regularly
- Use GitHub's fine-grained tokens

### 4. AI-Generated Code

**Issue**: AI-generated code is not audited before deployment.

**Impact**: Medium - Could contain vulnerabilities

**Mitigation**:

- Generated code is client-side only (HTML/CSS/JS)
- No server-side execution
- No database access
- Public repositories (subject to scrutiny)
- Consider implementing code scanning (planned)

### 5. Data URI Processing

**Issue**: Large attachments could cause memory issues.

**Impact**: Low - Could slow down API

**Mitigation**:

- Implement size limits (10MB max)
- Validate MIME types
- Use streaming for large files (planned)

## Security Checklist

Before deploying to production:

### Infrastructure

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Firewall configured (only necessary ports open)
- [ ] SSH hardened (key-based auth, no root login)
- [ ] System packages updated
- [ ] Backups configured

### Application

- [ ] All environment variables set correctly
- [ ] `.env` file permissions set to 600
- [ ] Secret is strong and random (32+ characters)
- [ ] API keys are valid and not shared
- [ ] Rate limiting configured
- [ ] Monitoring and alerting set up

### GitHub

- [ ] Token has minimal required permissions
- [ ] Token expiration set
- [ ] 2FA enabled on GitHub account
- [ ] Using fine-grained token (not classic)

### OpenAI

- [ ] Usage limits set
- [ ] Separate key for production
- [ ] Monitoring enabled
- [ ] Billing alerts configured

### Monitoring

- [ ] Log aggregation configured
- [ ] Error alerting set up
- [ ] Uptime monitoring enabled
- [ ] Security scanning enabled
- [ ] Regular security audits scheduled

## Security Contacts

- **Security Issues**: security@yourdomain.com
- **General Support**: support@yourdomain.com
- **GitHub Security Advisories**: [Enable on your repository]

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who help improve our security:

- [Your Name] - [Vulnerability Type] - [Date]

Thank you for helping keep this project secure! 🔒
