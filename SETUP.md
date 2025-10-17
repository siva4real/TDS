# Quick Setup Guide

This guide will help you get the API up and running in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] GitHub Personal Access Token (with `repo` permissions)
- [ ] OpenAI API Key
- [ ] Git installed (optional, for deployment tracking)

## Step-by-Step Setup

### 1. Get Your API Keys

#### GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (all), `admin:org` → `read:org`
4. Generate and copy the token (starts with `ghp_`)

#### OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key (starts with `sk-`)

### 2. Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd TDS

# Create environment file
cp env.template .env

# Edit .env with your actual values
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

Update `.env` with your values:

```env
SECRET_CODE=my_super_secret_code_123
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_USERNAME=your_github_username
OPENAI_API_KEY=sk-your_actual_key_here
```

### 3. Install Dependencies

#### Option A: Using the deployment script (Recommended)

```bash
# On macOS/Linux
chmod +x deploy.sh
./deploy.sh

# On Windows (use Git Bash or WSL)
bash deploy.sh
```

#### Option B: Manual installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Start the Server

#### Development Mode (with auto-reload)

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Docker (if you prefer)

```bash
docker-compose up --build
```

### 5. Test the API

Open a new terminal and run:

```bash
# Activate the virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the test suite
python test_api.py
```

Or test manually with curl:

```bash
# Health check
curl http://localhost:8000/

# Test deployment (replace YOUR_SECRET with your actual secret)
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "YOUR_SECRET",
    "task": "test-app",
    "round": 1,
    "nonce": "test-123",
    "brief": "Create a simple hello world page",
    "checks": ["Has index.html"],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

## Verification Steps

✅ **Server Started**: You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **Health Check**: Visit http://localhost:8000/ in your browser

- Expected: `{"status":"ok","message":"Automated GitHub Pages Deployment API"}`

✅ **Environment Variables**: Check they're loaded:

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('SECRET_CODE:', bool(os.getenv('SECRET_CODE'))); print('GITHUB_TOKEN:', bool(os.getenv('GITHUB_TOKEN')))"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"

- **Fix**: Make sure virtual environment is activated and run `pip install -r requirements.txt`

### "Invalid secret code" when testing

- **Fix**: Make sure the `secret` in your test request matches `SECRET_CODE` in `.env`

### "Server configuration incomplete"

- **Fix**: Verify all 4 environment variables are set in `.env`:
  - SECRET_CODE
  - GITHUB_TOKEN
  - GITHUB_USERNAME
  - OPENAI_API_KEY

### GitHub API errors

- **Fix**: Verify your GitHub token has `repo` permissions
- **Fix**: Check token hasn't expired at https://github.com/settings/tokens

### OpenAI API errors

- **Fix**: Verify your API key is valid
- **Fix**: Check you have credits at https://platform.openai.com/usage

### Port 8000 already in use

- **Fix**: Use a different port: `uvicorn app:app --port 8001`
- **Fix**: Find and kill the process using port 8000

## Next Steps

1. **Deploy to Production**: See README.md for deployment guides
2. **Set up Monitoring**: Configure health checks and alerts
3. **Configure Domain**: Set up a custom domain with HTTPS
4. **Add Database**: Replace in-memory storage with PostgreSQL/Redis

## Quick Reference

### Start Server

```bash
# Development
uvicorn app:app --reload

# Production
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Stop Server

- Press `Ctrl + C` in the terminal

### View Logs

- Logs appear in the terminal where the server is running

### Update Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### Restart After Code Changes

- Development mode: Automatic
- Production mode: Restart the server

## Support

If you're stuck:

1. Check the full README.md for detailed documentation
2. Review error messages carefully
3. Verify all environment variables
4. Test API keys manually (GitHub API, OpenAI API)
5. Open an issue on GitHub with error details

---

**Setup time: ~5 minutes** ⏱️

Need help? Open an issue or contact support.
