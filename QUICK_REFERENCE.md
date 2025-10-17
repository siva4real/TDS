# Quick Reference Card

One-page reference for the Automated GitHub Pages Deployment API.

---

## 🚀 Installation (3 Commands)

```bash
python quickstart.py        # Interactive setup
# OR manually:
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env.template .env && nano .env
```

---

## ⚙️ Configuration (.env file)

```env
SECRET_CODE=your_secret_code_here
GITHUB_TOKEN=ghp_your_github_token
GITHUB_USERNAME=your_username
OPENAI_API_KEY=sk-your_openai_key
```

**Get tokens:**

- GitHub: https://github.com/settings/tokens (repo scope)
- OpenAI: https://platform.openai.com/api-keys

---

## 🏃 Running the Server

```bash
# Development (auto-reload)
uvicorn app:app --reload

# Production (4 workers)
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker
docker-compose up --build

# Using deploy script
./deploy.sh
```

**Default URL**: http://localhost:8000

---

## 📡 API Endpoints

### Health Check

```bash
GET /
Response: {"status": "ok", "message": "..."}
```

### Deploy

```bash
POST /deploy
Content-Type: application/json

{
  "email": "user@example.com",
  "secret": "your_secret",
  "task": "my-app",
  "round": 1,
  "nonce": "unique-id",
  "brief": "Create a...",
  "checks": ["Has X", "Has Y"],
  "evaluation_url": "https://...",
  "attachments": []
}
```

---

## 🔧 Testing

```bash
# Run test suite
python test_api.py

# Manual health check
curl http://localhost:8000/

# Manual deploy test
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","secret":"YOUR_SECRET","task":"test","round":1,"nonce":"test123","brief":"Create hello world","checks":["Has index"],"evaluation_url":"https://httpbin.org/post","attachments":[]}'
```

---

## 📊 Response Codes

| Code | Meaning                 |
| ---- | ----------------------- |
| 200  | Success                 |
| 403  | Invalid secret          |
| 404  | Round 2 without Round 1 |
| 422  | Validation error        |
| 429  | Rate limited            |
| 500  | Server error            |

---

## 🔄 Workflow

```
Request → Validate → AI Generate → GitHub Create → Pages Deploy → Callback → Response
  (0s)      (1s)        (10-15s)       (5-10s)        (2-5s)       (1s)     (0s)
                        Total: 15-30 seconds
```

---

## 📁 Generated Repository

```
your-repo-name/
├── index.html    # Complete web app (HTML+CSS+JS)
├── README.md     # Professional documentation
└── LICENSE       # MIT License
```

**Deployed at**: `https://USERNAME.github.io/REPO-NAME/`

---

## 🐛 Troubleshooting

| Problem                           | Solution                                  |
| --------------------------------- | ----------------------------------------- |
| "Invalid secret"                  | Check SECRET_CODE in .env matches request |
| "Server configuration incomplete" | Set all 4 env variables                   |
| ModuleNotFoundError               | Run `pip install -r requirements.txt`     |
| Port 8000 in use                  | Use different port: `--port 8001`         |
| GitHub API error                  | Check token permissions (repo scope)      |
| OpenAI API error                  | Verify key and credits                    |
| Pages 404                         | Wait 2-5 minutes for deployment           |

---

## 🔒 Security Essentials

```bash
# Generate strong secret
openssl rand -base64 32

# Set .env permissions
chmod 600 .env

# Use HTTPS in production
# Configure rate limiting
# Rotate tokens regularly
```

---

## 📚 Documentation

| File                   | Purpose        |
| ---------------------- | -------------- |
| `README.md`            | Complete guide |
| `SETUP.md`             | Quick setup    |
| `API_DOCUMENTATION.md` | API reference  |
| `PROJECT_OVERVIEW.md`  | Architecture   |
| `SECURITY.md`          | Security guide |

---

## 🛠️ Common Commands

```bash
# Activate venv
source venv/bin/activate              # Linux/Mac
venv\Scripts\activate                 # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app:app --reload

# Run tests
python test_api.py

# View logs (systemd)
sudo journalctl -u deployment-api -f

# Restart service
sudo systemctl restart deployment-api
```

---

## 🌐 Deployment Checklist

- [ ] Set strong SECRET_CODE
- [ ] Configure all environment variables
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test API endpoint
- [ ] Test callback URL
- [ ] Set up rate limiting
- [ ] Enable logging

---

## 📞 Quick Links

- **Docs**: `README.md`
- **Setup**: `SETUP.md`
- **API**: `API_DOCUMENTATION.md`
- **Tests**: `python test_api.py`
- **Health**: http://localhost:8000/

---

## 💡 Example Request (cURL)

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@example.com",
    "secret": "YOUR_SECRET",
    "task": "weather-app-v1",
    "round": 1,
    "nonce": "req-001",
    "brief": "Create a weather app that shows current weather",
    "checks": [
      "Has city search",
      "Shows temperature",
      "Professional UI"
    ],
    "evaluation_url": "https://example.com/callback",
    "attachments": []
  }'
```

---

## 💡 Example Request (Python)

```python
import requests

response = requests.post("http://localhost:8000/deploy", json={
    "email": "dev@example.com",
    "secret": "YOUR_SECRET",
    "task": "weather-app-v1",
    "round": 1,
    "nonce": "req-001",
    "brief": "Create a weather app that shows current weather",
    "checks": ["Has city search", "Shows temperature"],
    "evaluation_url": "https://example.com/callback",
    "attachments": []
})

result = response.json()
print(f"Deployed: {result['pages_url']}")
```

---

## 🎯 Key Features

- ✅ AI-powered code generation (GPT-4)
- ✅ Automatic GitHub repo creation
- ✅ Automatic GitHub Pages deployment
- ✅ Professional documentation
- ✅ Round 1 & 2 support
- ✅ Data URI attachments
- ✅ Callback notifications
- ✅ Error handling & fallbacks

---

## 📊 Performance

- **Round 1**: 15-30 seconds
- **Round 2**: 10-20 seconds
- **Concurrent**: Use multiple workers
- **Rate Limit**: 10 req/min default

---

## 🏗️ Tech Stack

- FastAPI + Uvicorn
- OpenAI GPT-4
- GitHub API + Pages
- Pydantic validation
- Docker support

---

**Version**: 1.0.0  
**License**: MIT  
**Status**: Production Ready ✅
