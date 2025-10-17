# Project Overview

## Automated GitHub Pages Deployment API

A production-ready API that automates the entire workflow from receiving task requests to deploying live websites on GitHub Pages.

---

## 📁 Project Structure

```
TDS/
├── Core Application
│   ├── app.py                      # Main FastAPI application (700+ lines)
│   ├── requirements.txt            # Python dependencies
│   └── .gitignore                  # Git ignore rules
│
├── Configuration
│   ├── env.template                # Environment variables template
│   ├── .env                        # Your actual config (create from template)
│   ├── Dockerfile                  # Docker containerization
│   └── docker-compose.yml          # Docker Compose setup
│
├── Deployment
│   ├── deploy.sh                   # Multi-mode deployment script
│   ├── deployment-api.service      # Systemd service file
│   └── nginx.conf                  # Nginx reverse proxy config
│
├── Documentation
│   ├── README.md                   # Main documentation (1000+ lines)
│   ├── SETUP.md                    # Quick setup guide
│   ├── API_DOCUMENTATION.md        # Complete API reference
│   ├── CONTRIBUTING.md             # Contribution guidelines
│   ├── CHANGELOG.md                # Version history
│   ├── SECURITY.md                 # Security policy
│   └── PROJECT_OVERVIEW.md         # This file
│
├── Tools & Scripts
│   ├── quickstart.py               # Interactive setup script
│   └── test_api.py                 # Comprehensive test suite
│
└── Legal
    └── LICENSE                     # MIT License
```

---

## 🎯 What This API Does

### Input (JSON POST Request)

```json
{
  "email": "user@example.com",
  "secret": "your_secret",
  "task": "my-app",
  "round": 1,
  "brief": "Create a weather app",
  "checks": ["Shows weather", "Has search"],
  "evaluation_url": "https://callback.com"
}
```

### Process

1. **Validates** request and authenticates with secret
2. **Generates** code using OpenAI GPT-4
3. **Creates** GitHub repository
4. **Deploys** to GitHub Pages
5. **Notifies** your callback URL

### Output

```json
{
  "status": "success",
  "repo_url": "https://github.com/user/my-app-123",
  "pages_url": "https://user.github.io/my-app-123/",
  "commit_sha": "abc123..."
}
```

### Result

- ✅ Live website at GitHub Pages URL
- ✅ Public GitHub repository with code
- ✅ Professional README
- ✅ MIT License included

---

## 🚀 Quick Start (3 Steps)

### 1. Setup

```bash
python quickstart.py
```

This interactive script will:

- Create virtual environment
- Install dependencies
- Configure environment variables
- Optionally start the server

### 2. Configure

Edit `.env` with your credentials:

```env
SECRET_CODE=your_secret
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=yourusername
OPENAI_API_KEY=sk-...
```

### 3. Run

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Start server
uvicorn app:app --reload
```

---

## 🔑 Key Features

### Security

- ✅ Secret-based authentication
- ✅ No secrets in generated repos
- ✅ Environment variable configuration
- ✅ Input validation with Pydantic
- ✅ Rate limiting support

### Automation

- ✅ AI-powered code generation (GPT-4)
- ✅ Automatic GitHub repo creation
- ✅ Automatic GitHub Pages deployment
- ✅ Professional documentation generation
- ✅ Callback notification system

### Robustness

- ✅ Comprehensive error handling
- ✅ Fallback templates if AI fails
- ✅ Request timeout handling
- ✅ Retry logic support
- ✅ Detailed logging

### Flexibility

- ✅ Round 1: Create new deployments
- ✅ Round 2: Update existing deployments
- ✅ Data URI attachment support
- ✅ Custom evaluation callbacks
- ✅ Configurable generation prompts

---

## 📚 Documentation Guide

| Document                 | Purpose                | When to Read            |
| ------------------------ | ---------------------- | ----------------------- |
| **README.md**            | Complete documentation | First time setup        |
| **SETUP.md**             | Quick setup guide      | Getting started         |
| **API_DOCUMENTATION.md** | API reference          | Building integrations   |
| **PROJECT_OVERVIEW.md**  | Project summary        | Understanding structure |
| **CONTRIBUTING.md**      | Contribution guide     | Want to contribute      |
| **SECURITY.md**          | Security policy        | Production deployment   |
| **CHANGELOG.md**         | Version history        | Updates and changes     |

---

## 🛠️ Technology Stack

### Backend

- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **httpx** - Async HTTP client

### Integrations

- **OpenAI API** - GPT-4 for code generation
- **GitHub API** - Repository management via PyGithub
- **GitHub Pages** - Static site hosting

### Deployment

- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Systemd** - Service management
- **Gunicorn** - Production WSGI server

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT APPLICATION                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ POST /deploy (JSON)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI ENDPOINT                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Validate Request (Pydantic)                       │  │
│  │ 2. Verify Secret Code                                │  │
│  │ 3. Route to Round Handler                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────┐           ┌─────────┐
    │ Round 1 │           │ Round 2 │
    │ Handler │           │ Handler │
    └────┬────┘           └────┬────┘
         │                     │
         │  Both follow same   │
         │  core workflow:     │
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSING PIPELINE                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ STEP 1: Process Attachments                         │   │
│  │ • Decode data URIs                                   │   │
│  │ • Extract content and metadata                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ STEP 2: Generate Code (OpenAI API)                  │   │
│  │ • Construct detailed prompt                          │   │
│  │ • Call GPT-4                                         │   │
│  │ • Parse generated files                              │   │
│  │ • Fallback to templates if needed                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ STEP 3: GitHub Operations                           │   │
│  │ Round 1: • Create repository                         │   │
│  │          • Commit files                              │   │
│  │          • Enable GitHub Pages                       │   │
│  │ Round 2: • Update existing files                     │   │
│  │          • Create new commit                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ STEP 4: Callback Notification                       │   │
│  │ • Prepare response data                              │   │
│  │ • POST to evaluation_url                             │   │
│  │ • Log result                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ JSON Response
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT RECEIVES                          │
│  • Repository URL                                            │
│  • GitHub Pages URL                                          │
│  • Commit SHA                                                │
│  • Success status                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 API Statistics

### Request Processing Time

- **Round 1 (Create)**: 15-30 seconds
  - OpenAI generation: 5-15s
  - GitHub operations: 5-10s
  - Pages deployment: 2-5s
- **Round 2 (Update)**: 10-20 seconds
  - OpenAI generation: 5-15s
  - GitHub update: 3-5s

### Resource Requirements

- **Memory**: ~200MB base + ~50MB per request
- **CPU**: Minimal (mostly I/O bound)
- **Network**: Depends on attachment sizes
- **Storage**: Negligible (in-memory only)

### Rate Limits

- **API**: 10 requests/minute per IP (configurable)
- **OpenAI**: Depends on your plan
- **GitHub**: 5000 requests/hour with token

---

## 🧪 Testing

### Automated Tests

```bash
python test_api.py
```

Tests included:

- ✅ Health check
- ✅ Invalid secret rejection
- ✅ Round 1 deployment
- ✅ Round 2 updates
- ✅ Error handling

### Manual Testing

```bash
# Health check
curl http://localhost:8000/

# Deploy test
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

## 🚀 Deployment Options

### 1. Development (Local)

```bash
uvicorn app:app --reload
```

### 2. Production (Gunicorn)

```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. Docker

```bash
docker-compose up --build
```

### 4. Cloud Platforms

- **Railway**: One-click deploy
- **Render**: Auto-deploy from GitHub
- **Fly.io**: Global edge deployment
- **AWS/GCP/Azure**: Manual setup

### 5. VPS (DigitalOcean, Linode, etc.)

```bash
# Copy deployment-api.service to /etc/systemd/system/
# Copy nginx.conf to /etc/nginx/sites-available/
sudo systemctl enable deployment-api
sudo systemctl start deployment-api
```

---

## 🔒 Security Checklist

Before going to production:

- [ ] Change default SECRET_CODE
- [ ] Use strong, random secrets (32+ chars)
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (UFW/iptables)
- [ ] Set proper file permissions (.env = 600)
- [ ] Use environment variables (never hardcode)
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Backup strategy

---

## 📈 Roadmap

### Version 1.0 (Current)

- ✅ Core API functionality
- ✅ OpenAI integration
- ✅ GitHub integration
- ✅ Round 1 & 2 support
- ✅ Comprehensive documentation

### Version 1.1 (Planned)

- [ ] Database integration (PostgreSQL)
- [ ] Redis caching
- [ ] Enhanced error recovery
- [ ] API usage analytics

### Version 2.0 (Future)

- [ ] WebSocket real-time updates
- [ ] Admin dashboard
- [ ] Template library
- [ ] Multi-language support
- [ ] Custom domains for Pages

---

## 💡 Use Cases

### Educational Platforms

- Automated assignment grading
- Student project deployment
- Learning management systems

### Development Tools

- Rapid prototyping
- Demo site generation
- Documentation sites

### No-Code Solutions

- Visual website builders
- Form-to-website converters
- Template marketplaces

### Testing & QA

- A/B testing deployments
- Preview environments
- Automated testing suites

---

## 🤝 Support

### Getting Help

1. Check **SETUP.md** for setup issues
2. Read **API_DOCUMENTATION.md** for API questions
3. Review **SECURITY.md** for security concerns
4. Open an issue on GitHub

### Contributing

See **CONTRIBUTING.md** for guidelines on:

- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style guidelines

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file

**TL;DR**: Free to use, modify, and distribute. No warranty.

---

## 🙏 Credits

Built with:

- **FastAPI** by Sebastián Ramírez
- **OpenAI** GPT-4 API
- **GitHub** API and Pages
- **Python** ecosystem

---

## 📞 Contact

- **Issues**: GitHub Issues
- **Security**: See SECURITY.md
- **Email**: support@yourdomain.com

---

**Last Updated**: October 17, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
