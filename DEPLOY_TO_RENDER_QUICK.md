# Quick Deploy to Render - TL;DR

## 🚀 5-Minute Deployment

### 1️⃣ Push to GitHub (if not already done)

```bash
git init
git add .
git commit -m "Ready for Render deployment"
git remote add origin https://github.com/YOUR_USERNAME/your-repo-name.git
git push -u origin main
```

### 2️⃣ Deploy on Render

1. Go to https://render.com → Sign in with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: Free
5. Click **"Create Web Service"**

### 3️⃣ Done! ✅

- Wait 2-3 minutes for deployment
- Your URL: `https://YOUR-APP-NAME.onrender.com`
- Test: `curl https://YOUR-APP-NAME.onrender.com/`

## 📊 Monitor Your API

- **Logs**: Dashboard → Your Service → Logs tab
- See all debug messages in real-time with emojis 🎉

## 🔄 Update Your API

```bash
git add .
git commit -m "Updates"
git push
```

Render auto-deploys in ~2 minutes.

---

**Need detailed instructions?** See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
