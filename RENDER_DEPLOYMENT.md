# GrowCalculator Migration to Render

## ✅ Migration Complete! Here's what to do next:

### Step 1: Prepare Your Repository

1. **Commit your changes to Git:**
```bash
git add .
git commit -m "Migrate to Render: Add main_render.py and render.yaml config"
git push origin main
```

### Step 2: Deploy to Render

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository** (GrowCaculator-main)
4. **Configure the service:**
   - **Name**: `growcalculator` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main_render:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Plan**: `Free`

### Step 3: Environment Variables (Optional)

If you're using Redis for shared results, add this in Render:
- **Key**: `REDIS_URL` 
- **Value**: Your Redis connection string (or leave empty to use in-memory storage)

For Discord webhooks (optional):
- **Key**: `DISCORD_WEBHOOK_URL`
- **Value**: Your Discord webhook URL

### Step 4: Deploy!

Click **"Create Web Service"** and Render will:
1. Build your app using `pip install -r requirements.txt`
2. Start it using the uvicorn command
3. Provide you with a live URL like: `https://growcalculator.onrender.com`

## 🔧 Files Created/Modified:

### New Files:
- ✅ `main_render.py` - Main entry point for Render
- ✅ `render.yaml` - Render configuration (optional, can use web interface instead)
- ✅ `RENDER_DEPLOYMENT.md` - This guide
- ✅ `test_render.py` - Local testing script

### Modified Files:
- ✅ `requirements.txt` - Updated with compatible versions + gunicorn

## 🚀 Key Differences from Vercel:

| Aspect | Vercel | Render |
|--------|---------|---------|
| Entry Point | `api/index.py` | `main_render.py` |
| Static Files | Auto-handled | Manual mount required |
| Environment | Serverless | Container-based |
| Cold Starts | Fast | ~15-30 seconds after inactivity |
| CPU Limits | Strict | More generous on free tier |

## 🎯 Benefits of Render:

- ✅ **No CPU throttling** like Vercel had
- ✅ **750 hours/month free tier** (enough for always-on small apps)
- ✅ **Native Python support** (no serverless adaptation needed)
- ✅ **Built-in PostgreSQL** option (if needed later)
- ✅ **Automatic SSL certificates**
- ✅ **Git-based deployments**

## 🔍 Troubleshooting:

### If build fails:
1. Check that `requirements.txt` has all needed dependencies
2. Verify your GitHub repo is public or connected properly
3. Check Render build logs for specific error messages

### If app won't start:
1. Verify the start command is: `uvicorn main_render:app --host 0.0.0.0 --port $PORT --workers 1`
2. Check that `main_render.py` exists in your repository root
3. Review Render runtime logs for errors

### If static files don't work:
1. Make sure your `static/` directory is in the repository
2. Verify the paths in your templates are correct (`/static/...`)

## 🧪 Local Testing:

Test locally before deploying:
```bash
# Test imports
python test_render.py

# Run the app locally  
python main_render.py
# Then visit: http://localhost:8000
```

## 🔄 Rolling Back (if needed):

If something goes wrong, you can:
1. Keep your Vercel deployment running temporarily
2. Fix issues on Render
3. Update DNS once Render is working perfectly

## 🎉 Success!

Once deployed, your app will be available at your Render URL with:
- All existing functionality preserved
- Better performance (no CPU throttling)  
- Free hosting without usage limits
- Automatic deployments on git push

**Your migration to Render is complete!** 🚀
