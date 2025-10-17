# 🎉 START HERE

Welcome to your **Automated GitHub Pages Deployment API**!

This is your entry point. Follow these steps to get up and running in minutes.

---

## ✅ What You Have

A **production-ready API** that:

1. Accepts JSON POST requests with task specifications
2. Uses **OpenAI GPT-4** to generate code automatically
3. Creates **GitHub repositories** via API
4. Deploys to **GitHub Pages** automatically
5. Sends callback notifications
6. Handles both initial deployments (Round 1) and updates (Round 2)

**Everything is automated. Everything is documented. Everything is ready.**

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Run the Setup Script

```bash
python quickstart.py
```

This interactive script will:

- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Help you configure environment variables
- ✅ Optionally start the server

**That's it!** The script handles everything.

---

### Step 2: Get Your API Keys

You'll need:

1. **GitHub Personal Access Token**

   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (all checkboxes)
   - Copy the token (starts with `ghp_`)

2. **OpenAI API Key**

   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

3. **Secret Code**
   - The quickstart script can generate one for you
   - Or create your own: `openssl rand -base64 32`

---

### Step 3: Test It

Once the server is running:

```bash
# In a new terminal
python test_api.py
```

This runs a comprehensive test suite that verifies everything works.

---

## 📚 What to Read Next

### If you want to...

**Get started quickly**
→ You're done! The server is running. See "Using the API" below.

**Understand the API**
→ Read [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) - Complete API reference

**Deploy to production**
→ Read [`SETUP.md`](SETUP.md) - Deployment guides for various platforms

**Understand the architecture**
→ Read [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) - System design and structure

**Contribute or modify**
→ Read [`CONTRIBUTING.md`](CONTRIBUTING.md) - Development guidelines

**Quick reference**
→ Read [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - One-page cheat sheet

**Security concerns**
→ Read [`SECURITY.md`](SECURITY.md) - Security best practices

---

## 🎯 Using the API

### Example: Deploy a Weather App

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "secret": "YOUR_SECRET_FROM_ENV",
    "task": "weather-app-v1",
    "round": 1,
    "nonce": "request-001",
    "brief": "Create a weather app that displays current weather for any city",
    "checks": [
      "Has city search input",
      "Shows temperature and conditions",
      "Professional UI design",
      "Responsive layout"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

**Response:**

```json
{
  "status": "success",
  "message": "Repository created and deployed",
  "repo_url": "https://github.com/username/weather-app-v1-1729180000",
  "pages_url": "https://username.github.io/weather-app-v1-1729180000/",
  "commit_sha": "abc123..."
}
```

**Result:**

- ✅ New GitHub repo created
- ✅ Live website at the `pages_url`
- ✅ Professional README included
- ✅ MIT License included

---

## 🔄 Updating a Deployment (Round 2)

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "secret": "YOUR_SECRET",
    "task": "weather-app-v1",
    "round": 2,
    "nonce": "request-002",
    "brief": "Add 7-day forecast and weather icons",
    "checks": [
      "Shows 7-day forecast",
      "Weather icons displayed",
      "Updated README"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

Same `task` name, but `round: 2` updates the existing repo!

---

## 📁 Project Structure

```
TDS/
├── 📄 START_HERE.md          ← You are here
├── 📄 QUICK_REFERENCE.md     ← One-page cheat sheet
├── 📄 README.md              ← Complete documentation
├── 📄 SETUP.md               ← Setup & deployment guide
├── 📄 API_DOCUMENTATION.md   ← Full API reference
│
├── 🐍 app.py                 ← Main application (FastAPI)
├── 🐍 test_api.py            ← Test suite
├── 🐍 quickstart.py          ← Interactive setup
│
├── 🔧 requirements.txt       ← Python dependencies
├── 🔧 env.template           ← Environment config template
├── 🔧 .gitignore             ← Git ignore rules
│
├── 🐳 Dockerfile             ← Docker container
├── 🐳 docker-compose.yml     ← Docker Compose
│
└── 📚 More docs...
```

---

## 🔧 Configuration

Your `.env` file (created by quickstart):

```env
SECRET_CODE=your_secret_here
GITHUB_TOKEN=ghp_your_token
GITHUB_USERNAME=your_username
OPENAI_API_KEY=sk_your_key
```

**Security:**

- Never commit `.env` to git (it's in `.gitignore`)
- Use strong secrets (32+ characters)
- Rotate tokens regularly

---

## 🐛 Troubleshooting

### Server won't start?

```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check environment variables
cat .env
```

### API returns "Invalid secret"?

Make sure the `secret` in your request matches `SECRET_CODE` in `.env`.

### GitHub/OpenAI errors?

- Verify tokens are valid
- Check token permissions
- Ensure you have API credits

### More help?

See [`SETUP.md`](SETUP.md) troubleshooting section.

---

## 🚀 Deployment to Production

### Quick Deploy Options

**Railway / Render / Fly.io**

1. Connect your GitHub repo
2. Set environment variables
3. Deploy!

**Docker**

```bash
docker-compose up --build
```

**VPS (Ubuntu/Debian)**

```bash
# See SETUP.md for detailed instructions
./deploy.sh
```

Full deployment guides in [`SETUP.md`](SETUP.md).

---

## 📊 What Gets Generated

Each deployment creates a repository with:

### 1. index.html

- Complete web application
- HTML + CSS + JavaScript in one file
- No build process needed
- Works immediately on GitHub Pages

### 2. README.md

- Professional documentation
- Project summary
- Setup instructions
- Usage guide
- Code explanation
- License information

### 3. LICENSE

- MIT License
- Current year
- Ready for open source

**Example**: https://username.github.io/task-name-timestamp/

---

## ⚡ Performance

- **Round 1**: 15-30 seconds (create)
- **Round 2**: 10-20 seconds (update)
- **Concurrent**: Use multiple workers
- **Rate Limit**: 10 requests/minute (configurable)

---

## 🎯 Use Cases

✅ **Educational**: Automated assignment deployment  
✅ **Prototyping**: Rapid idea validation  
✅ **Testing**: Preview environments  
✅ **Documentation**: Auto-generated docs sites  
✅ **No-Code**: Visual builder backends

---

## 🔒 Security

✅ Secret-based authentication  
✅ No secrets in generated repos  
✅ Environment variable config  
✅ Input validation  
✅ Rate limiting support

See [`SECURITY.md`](SECURITY.md) for details.

---

## 🤝 Contributing

Want to improve this project?

1. Read [`CONTRIBUTING.md`](CONTRIBUTING.md)
2. Fork the repository
3. Make your changes
4. Submit a pull request

---

## 📞 Support

**Need help?**

1. Check [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) for common solutions
2. Read [`SETUP.md`](SETUP.md) for detailed setup help
3. Review [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) for API questions
4. Open an issue on GitHub

---

## ✨ Next Steps

Now that you're set up:

1. **Test the API** with `python test_api.py`
2. **Try a deployment** with the example above
3. **Read the API docs** to understand all features
4. **Deploy to production** when ready
5. **Build something awesome!**

---

## 📖 Documentation Overview

| Document                 | Length      | Purpose        |
| ------------------------ | ----------- | -------------- |
| **START_HERE.md**        | 1 page      | You are here!  |
| **QUICK_REFERENCE.md**   | 1 page      | Cheat sheet    |
| **SETUP.md**             | 10 min read | Setup guide    |
| **README.md**            | 30 min read | Complete docs  |
| **API_DOCUMENTATION.md** | 20 min read | API reference  |
| **PROJECT_OVERVIEW.md**  | 15 min read | Architecture   |
| **CONTRIBUTING.md**      | 10 min read | Dev guide      |
| **SECURITY.md**          | 10 min read | Security guide |

---

## 🎉 You're Ready!

Everything is set up and ready to go. The API is powerful, well-documented, and production-ready.

**Need the basics?** → [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)  
**Need the details?** → [`README.md`](README.md)  
**Need the API spec?** → [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md)

**Happy deploying! 🚀**

---

**Version**: 1.0.0  
**License**: MIT  
**Status**: Production Ready ✅
