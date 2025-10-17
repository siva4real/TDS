# Automated GitHub Pages Deployment API

A production-ready API endpoint that automates the complete workflow of receiving task requests, generating code using AI, creating GitHub repositories, and deploying to GitHub Pages.

## Overview

This API accepts JSON POST requests containing task specifications, automatically generates minimal viable products using OpenAI's API, creates public GitHub repositories, and deploys them to GitHub Pages. It handles both initial deployments (Round 1) and subsequent updates (Round 2).

## Features

- **🔒 Secure Authentication**: Secret-based request verification
- **🤖 AI-Powered Code Generation**: Uses OpenAI GPT-4 to generate production-ready code
- **📦 Automated Repository Management**: Creates and manages GitHub repositories via API
- **🚀 GitHub Pages Deployment**: Automatically enables and deploys to GitHub Pages
- **📝 Professional Documentation**: Generates comprehensive README files
- **♻️ Update Support**: Handles Round 2 requests for modifications
- **📎 Attachment Processing**: Supports data URI attachments
- **✅ Validation**: Built-in request validation with Pydantic
- **🔄 Callback System**: Sends deployment details to evaluation URLs

## Architecture

```
Client Request (JSON)
    ↓
API Endpoint (/deploy)
    ↓
Secret Verification
    ↓
OpenAI Code Generation
    ↓
GitHub Repo Creation
    ↓
GitHub Pages Deployment
    ↓
Evaluation Callback
    ↓
Response to Client
```

## Setup

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with `repo` and `admin:org` permissions
- OpenAI API Key with GPT-4 access
- Domain or hosting for the API endpoint

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd TDS
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your actual credentials:

   ```env
   SECRET_CODE=your_secure_secret_code
   GITHUB_TOKEN=ghp_your_github_token
   GITHUB_USERNAME=your_github_username
   OPENAI_API_KEY=sk_your_openai_api_key
   ```

5. **Verify configuration:**
   ```bash
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✓ Config loaded')"
   ```

### Running the API

#### Development Mode

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Gunicorn (Recommended for Production)

```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Usage

### Endpoint

```
POST /deploy
Content-Type: application/json
```

### Request Format

#### Round 1 (Initial Deployment)

```json
{
  "email": "student@example.com",
  "secret": "your_secret_code",
  "task": "captcha-solver-v1",
  "round": 1,
  "nonce": "ab12-cd34-ef56",
  "brief": "Create a captcha solver that handles ?url=https://.../image.png. Default to attached sample.",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
    }
  ]
}
```

#### Round 2 (Update Existing Deployment)

```json
{
  "email": "student@example.com",
  "secret": "your_secret_code",
  "task": "captcha-solver-v1",
  "round": 2,
  "nonce": "gh78-ij90-kl12",
  "brief": "Add error handling and improve UI with dark mode support",
  "checks": [
    "Dark mode toggle implemented",
    "Error handling for invalid URLs",
    "Loading states displayed"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": []
}
```

### Response Format

#### Success Response (HTTP 200)

```json
{
  "status": "success",
  "message": "Repository created and deployed",
  "repo_url": "https://github.com/username/captcha-solver-v1-1697500000",
  "pages_url": "https://username.github.io/captcha-solver-v1-1697500000/",
  "commit_sha": "abc123def456..."
}
```

#### Error Responses

**Invalid Secret (HTTP 403):**

```json
{
  "detail": "Invalid secret code"
}
```

**Server Error (HTTP 500):**

```json
{
  "detail": "Error processing request: <error message>"
}
```

**Round 2 Without Round 1 (HTTP 404):**

```json
{
  "detail": "Repository not found. Must complete round 1 first."
}
```

### Evaluation Callback

The API automatically sends the following JSON to the `evaluation_url`:

```json
{
  "email": "student@example.com",
  "task": "captcha-solver-v1",
  "round": 1,
  "nonce": "ab12-cd34-ef56",
  "repo_url": "https://github.com/username/captcha-solver-v1-1697500000",
  "commit_sha": "abc123def456...",
  "pages_url": "https://username.github.io/captcha-solver-v1-1697500000/"
}
```

## Testing

### Health Check

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "status": "ok",
  "message": "Automated GitHub Pages Deployment API"
}
```

### Test Round 1 Request

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_code",
    "task": "test-app-1",
    "round": 1,
    "nonce": "test-nonce-123",
    "brief": "Create a simple hello world page",
    "checks": ["Has index.html", "Has README.md"],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

### Test Round 2 Request

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_code",
    "task": "test-app-1",
    "round": 2,
    "nonce": "test-nonce-456",
    "brief": "Add a button that changes background color",
    "checks": ["Button exists", "Background changes on click"],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

## Code Explanation

### Core Components

#### 1. FastAPI Application (`app.py`)

The main application file contains:

- **Request Models**: Pydantic models for validation

  - `TaskRequest`: Validates incoming JSON requests
  - `Attachment`: Handles data URI attachments
  - `EvaluationResponse`: Formats callback data

- **Main Endpoint** (`/deploy`):
  - Verifies secret code
  - Routes to Round 1 or Round 2 handlers
  - Returns JSON responses

#### 2. Round 1 Handler (`handle_round_1`)

**Workflow:**

1. Generates unique repository name from task
2. Processes attachments (data URIs)
3. Calls OpenAI API for code generation
4. Creates GitHub repository
5. Enables GitHub Pages
6. Sends evaluation callback
7. Stores repository info for Round 2

**Key Features:**

- Idempotent: Returns existing repo if already created
- Error handling: Fallback templates if AI fails
- Automatic MIT license inclusion

#### 3. Round 2 Handler (`handle_round_2`)

**Workflow:**

1. Retrieves existing repository info
2. Generates updated code with OpenAI
3. Updates repository files
4. Sends evaluation callback

**Key Features:**

- Validates Round 1 completion
- Updates existing files or creates new ones
- Preserves repository URL and Pages URL

#### 4. Code Generation (`generate_code_with_ai`)

**Process:**

1. Constructs detailed prompt with brief, checks, and attachments
2. Calls OpenAI GPT-4 API
3. Parses generated files using markers
4. Falls back to default templates on failure

**Generated Files:**

- `index.html`: Complete web application
- `README.md`: Professional documentation
- `LICENSE`: MIT license

#### 5. GitHub Integration

**Functions:**

- `create_github_repo`: Creates public repository and commits files
- `update_github_repo`: Updates existing files or creates new ones
- `enable_github_pages`: Enables Pages via REST API

**Security:**

- Uses PyGithub library for authentication
- Never commits secrets to repositories
- All repos are public by default

#### 6. Storage System

Currently uses in-memory dictionary (`repo_storage`):

```python
{
  "email:task": {
    "repo_name": "...",
    "repo_url": "...",
    "pages_url": "...",
    "created_at": "..."
  }
}
```

**Production Recommendation**: Replace with database (PostgreSQL, MongoDB, Redis)

### Security Considerations

1. **Secret Verification**: Every request must include valid secret
2. **Environment Variables**: Sensitive data never hardcoded
3. **No Secrets in Git**: Generated repos contain no API keys
4. **Public Repositories**: All created repos are public
5. **Input Validation**: Pydantic validates all inputs
6. **Error Handling**: Detailed errors logged, generic errors returned

### Design Decisions

1. **Single File HTML**: No build process required, immediate functionality
2. **Minimal Dependencies**: Faster load times, easier maintenance
3. **AI-Powered Generation**: Adapts to any task specification
4. **Idempotent Operations**: Safe to retry Round 1 requests
5. **Async Operations**: Non-blocking HTTP calls for performance
6. **Fallback Templates**: Ensures success even if AI fails

## Deployment

### Docker Deployment (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV PORT=8000
EXPOSE $PORT

CMD uvicorn app:app --host 0.0.0.0 --port $PORT
```

Build and run:

```bash
docker build -t deployment-api .
docker run -p 8000:8000 --env-file .env deployment-api
```

### Cloud Platforms

#### Railway / Render / Fly.io

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

#### AWS EC2 / DigitalOcean

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Setup application
cd /opt
git clone <repo-url> deployment-api
cd deployment-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/deployment-api.service
```

Service file:

```ini
[Unit]
Description=Deployment API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/deployment-api
Environment="PATH=/opt/deployment-api/venv/bin"
EnvironmentFile=/opt/deployment-api/.env
ExecStart=/opt/deployment-api/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable deployment-api
sudo systemctl start deployment-api
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/HTTPS

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Monitoring and Logs

### View Logs

```bash
# Development
# Logs appear in terminal

# Production (systemd)
sudo journalctl -u deployment-api -f

# Docker
docker logs -f <container-id>
```

### Health Monitoring

Use the root endpoint for health checks:

```bash
curl http://localhost:8000/
```

Set up monitoring with tools like:

- UptimeRobot
- Pingdom
- DataDog
- New Relic

## Troubleshooting

### Common Issues

**Issue**: "Invalid secret code"

- **Solution**: Verify `SECRET_CODE` in `.env` matches request

**Issue**: "Server configuration incomplete"

- **Solution**: Check all environment variables are set

**Issue**: GitHub API rate limit

- **Solution**: Use authenticated token, upgrade to higher rate limits

**Issue**: OpenAI API timeout

- **Solution**: Increase timeout, check API key validity

**Issue**: GitHub Pages not accessible (404)

- **Solution**: Wait 2-5 minutes for Pages to deploy, verify repo is public

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Current Performance

- **Round 1**: ~15-30 seconds

  - OpenAI API: 5-15 seconds
  - GitHub repo creation: 5-10 seconds
  - GitHub Pages enable: 2-5 seconds

- **Round 2**: ~10-20 seconds
  - OpenAI API: 5-15 seconds
  - GitHub repo update: 3-5 seconds

### Optimization Strategies

1. **Caching**: Cache AI responses for similar tasks
2. **Async Processing**: Use background tasks for long operations
3. **Database**: Replace in-memory storage with Redis/PostgreSQL
4. **CDN**: Use CDN for static assets
5. **Load Balancing**: Multiple API instances behind load balancer

## Limitations

1. **Storage**: In-memory storage lost on restart (use database for production)
2. **Rate Limits**: Subject to GitHub and OpenAI API limits
3. **Concurrent Requests**: Limited by single-process uvicorn (use workers)
4. **File Size**: Data URI attachments limited by request size
5. **GitHub Pages**: 1 GB storage limit per repository

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Redis caching for AI responses
- [ ] WebSocket support for real-time progress
- [ ] Admin dashboard for monitoring
- [ ] Rollback functionality
- [ ] Custom domain support for Pages
- [ ] Multi-language code generation
- [ ] Template library for common tasks
- [ ] Analytics and usage tracking
- [ ] API key management system

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Contact: [your-email@example.com]

## Acknowledgments

- FastAPI for the excellent web framework
- OpenAI for GPT-4 API
- PyGithub for GitHub API integration
- The open-source community

---

**Built with ❤️ for automated deployments**
