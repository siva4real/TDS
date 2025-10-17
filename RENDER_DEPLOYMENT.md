# Deploying to Render - Step by Step Guide

This guide will walk you through deploying your GitHub Pages Deployment API to Render.

## Prerequisites

✅ Your code is ready with hardcoded credentials (temporary)
✅ You have a GitHub account
✅ You have a Render account (free tier works fine)

---

## Step 1: Push Your Code to GitHub

1. **Initialize Git** (if not already done):

   ```bash
   git init
   git add .
   git commit -m "Initial commit - API ready for deployment"
   ```

2. **Create a new GitHub repository**:

   - Go to https://github.com/new
   - Name it something like `github-pages-deployment-api`
   - Choose **Private** (since you have hardcoded credentials)
   - Don't initialize with README (you already have one)
   - Click "Create repository"

3. **Push your code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/github-pages-deployment-api.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 2: Sign Up / Log In to Render

1. Go to https://render.com
2. Click **"Get Started"** or **"Sign In"**
3. Sign in with your GitHub account (recommended)
4. Authorize Render to access your repositories

---

## Step 3: Create a New Web Service

1. From your Render Dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**

3. **Connect Your Repository**:

   - If you see your repository listed, click **"Connect"**
   - If not, click **"Configure account"** and grant access to the repository

4. **Configure the Service**:

   **Basic Settings:**

   - **Name**: `github-pages-api` (or your preferred name)
   - **Region**: Choose the one closest to you (e.g., Oregon, Frankfurt, Singapore)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`

   **Build & Deploy:**

   - **Build Command**:

     ```
     pip install -r requirements.txt
     ```

   - **Start Command**:
     ```
     python app.py
     ```

   **Instance Type:**

   - Select **"Free"** (or choose a paid plan if you prefer)
   - Note: Free instances may spin down after inactivity

5. **Advanced Settings** (scroll down or click "Advanced"):

   - **Environment Variables**: None needed (your credentials are hardcoded)
   - **Auto-Deploy**: Keep it ON (deploys automatically on git push)

6. Click **"Create Web Service"**

---

## Step 4: Wait for Deployment

1. Render will now:

   - Pull your code from GitHub
   - Install dependencies
   - Start your application

2. **Monitor the deployment**:

   - You'll see a live log stream
   - Look for messages like:
     ```
     ✓ GitHub client initialized
     ✓ OpenAI client initialized
     🚀 STARTING SERVER
     ```

3. **Deployment complete** when you see:
   - Status changes to **"Live"** (green dot)
   - You'll get a URL like: `https://github-pages-api.onrender.com`

---

## Step 5: Test Your Deployment

1. **Copy your Render URL** (shown at the top of the dashboard)

2. **Test the health endpoint**:

   ```bash
   curl https://YOUR-APP-NAME.onrender.com/
   ```

   Should return:

   ```json
   { "status": "ok", "message": "Automated GitHub Pages Deployment API" }
   ```

3. **Test a full deployment** (using your test script or curl):
   ```bash
   curl -X POST https://YOUR-APP-NAME.onrender.com/deploy \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "secret": "myappsecret123123",
       "task": "test-deployment",
       "round": 1,
       "nonce": "test123",
       "brief": "Test deployment to verify API is working",
       "checks": ["Works correctly", "Returns proper response"],
       "evaluation_url": "https://webhook.site/your-unique-url",
       "attachments": []
     }'
   ```

---

## Step 6: View Logs

To see your debug messages in action:

1. In Render dashboard, click on your service
2. Go to the **"Logs"** tab
3. You'll see all the detailed debug output:

   ```
   🚀 NEW REQUEST RECEIVED
   📧 Email: test@example.com
   📝 Task: test-deployment
   🔢 Round: 1
   ...
   ```

4. You can filter logs:
   - **Live logs**: See real-time updates
   - **Historical logs**: Review past requests
   - Use the search box to find specific events

---

## Troubleshooting

### Issue: Service fails to start

**Check:**

- Look at the build logs for errors
- Make sure `requirements.txt` is in the root directory
- Verify Python version compatibility

### Issue: API returns 500 error

**Check:**

- View the Logs tab for error messages
- Verify credentials are correct in `app.py`
- Check GitHub token hasn't expired

### Issue: Free instance is slow or times out

**Solution:**

- Free instances spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Consider upgrading to a paid plan for always-on service

### Issue: Can't see detailed logs

**Solution:**

- Make sure you're on the "Logs" tab in Render dashboard
- The logs show all the debug messages we added
- Use the log level filter if needed

---

## Important Security Notes

⚠️ **Your credentials are hardcoded in the code!**

Since your repo is **private**, it's okay for now, but for production:

1. **Never commit credentials to a public repo**
2. **Use Render's Environment Variables instead**:

   - Go to your service → Environment tab
   - Add each secret as an environment variable
   - Update `app.py` to use `os.getenv()` again

3. **Rotate your secrets regularly**:
   - GitHub tokens can be regenerated
   - OpenAI keys can be rotated
   - Update the hardcoded values when needed

---

## Next Steps

✅ Your API is now live on Render!
✅ You can share the URL with your application
✅ Monitor requests in real-time through logs
✅ Auto-deploys happen when you push to GitHub

**Your API URL**: `https://YOUR-APP-NAME.onrender.com`

**Endpoints**:

- `GET /` - Health check
- `POST /deploy` - Main deployment endpoint

---

## Updating Your Deployment

To update your API:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update API with new features"
   git push
   ```
3. Render automatically detects the push and redeploys
4. Watch the logs to see the new deployment happening
5. Once "Live", your changes are active!

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Status Page**: https://status.render.com

---

_Happy Deploying! 🚀_
