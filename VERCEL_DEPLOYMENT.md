# 🚀 Vercel Deployment Guide for GrowCalculator

This guide will help you deploy the GrowCalculator FastAPI application to Vercel's serverless platform.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional but recommended):
   ```bash
   npm i -g vercel
   ```
3. **Git Repository**: Your code should be in a Git repository

## 🔧 Deployment Steps

### 1. **Prepare Your Repository**

Ensure your repository has the following Vercel-specific files:
- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function entry point
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification

### 2. **Deploy via Vercel Dashboard**

1. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your Git repository
   - Select the repository containing GrowCalculator

2. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: Leave as default (or specify if needed)
   - **Build Command**: Leave empty (not needed for Python)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

3. **Environment Variables** (if needed):
   - Add any environment variables your app requires
   - For this app, no additional environment variables are needed

4. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete

### 3. **Deploy via Vercel CLI**

```bash
# Install Vercel CLI if you haven't already
npm i -g vercel

# Navigate to your project directory
cd Website

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? [your-username]
# - Link to existing project? N
# - Project name? growcalculator (or your preferred name)
# - In which directory is your code located? ./
# - Want to override the settings? N
```

### 4. **Automatic Deployments**

Once connected, Vercel will automatically deploy:
- **Production**: Every push to your main branch
- **Preview**: Every pull request gets a preview deployment

## 🌐 **Accessing Your App**

After deployment, you'll get:
- **Production URL**: `https://your-project-name.vercel.app`
- **Preview URLs**: `https://your-project-name-git-branch-username.vercel.app`

## ⚠️ **Important Notes for Vercel**

### **Serverless Limitations**
- **No persistent storage**: Shared results are stored in memory and reset on each function invocation
- **Cold starts**: First request may be slower
- **Function timeout**: Maximum 30 seconds per request
- **Memory limits**: 1024MB per function

### **What Changes in Vercel**
1. **Database**: SQLite replaced with in-memory storage
2. **File system**: Read-only, no persistent writes
3. **Startup events**: Limited functionality
4. **Static files**: Served through custom endpoint

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Import Errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check that `api/index.py` has correct import paths

2. **Static Files Not Loading**:
   - Verify the static file handler in `api/index.py`
   - Check that static files are in the correct directory

3. **Function Timeout**:
   - Optimize your code for faster execution
   - Consider breaking complex operations into smaller functions

4. **Memory Issues**:
   - Reduce the size of data loaded into memory
   - Optimize image and data handling

### **Debugging**

1. **Check Vercel Logs**:
   - Go to your project dashboard
   - Click on a deployment
   - View function logs

2. **Local Testing**:
   ```bash
   # Test the Vercel function locally
   cd api
   python index.py
   ```

## 📊 **Performance Optimization**

### **For Vercel Serverless**

1. **Cold Start Reduction**:
   - Keep functions lightweight
   - Minimize imports and initialization

2. **Memory Management**:
   - Load data only when needed
   - Clear large objects after use

3. **Response Time**:
   - Optimize calculation algorithms
   - Cache frequently used data in memory

## 🔄 **Updating Your App**

### **Automatic Updates**
- Push changes to your main branch
- Vercel automatically deploys the new version

### **Manual Updates**
```bash
vercel --prod
```

## 📈 **Monitoring**

1. **Vercel Analytics**: Built-in performance monitoring
2. **Function Logs**: Real-time error tracking
3. **Performance Metrics**: Response times and error rates

## 🎯 **Best Practices**

1. **Keep Functions Lightweight**: Minimize startup time
2. **Handle Errors Gracefully**: Provide meaningful error messages
3. **Optimize Dependencies**: Only include necessary packages
4. **Test Locally**: Verify functionality before deploying
5. **Monitor Performance**: Use Vercel's built-in analytics

## 🆘 **Support**

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**Your GrowCalculator is now ready for Vercel deployment! 🚀**

The app will automatically scale based on demand and provide fast, reliable access to your plant value calculations from anywhere in the world.
