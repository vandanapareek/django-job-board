# 🚀 Django Job Board - Free Deployment Guide

## 📋 Prerequisites

1. **Git Repository**: Your project should be in a Git repository (GitHub, GitLab, etc.)
2. **Python Knowledge**: Basic understanding of Python/Django
3. **Account**: Sign up for one of the free platforms below

---

## 🆓 **Option 1: Railway (Recommended)**

### Why Railway?
- ✅ **$5 free credit monthly** (enough for small projects)
- ✅ **PostgreSQL included**
- ✅ **Easy deployment** (similar to Heroku)
- ✅ **Automatic HTTPS**
- ✅ **Custom domains**

### Step-by-Step Deployment:

#### 1. Prepare Your Project
```bash
# Make sure all files are committed to Git
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Sign Up & Deploy
1. **Visit**: [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Railway will auto-detect Django**

#### 3. Configure Environment Variables
In Railway dashboard, add these environment variables:
```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app
```

#### 4. Add PostgreSQL Database
1. **Click "New"** → **"Database"** → **"PostgreSQL"**
2. **Railway will automatically set DATABASE_URL**

#### 5. Deploy
1. **Railway will automatically deploy**
2. **Visit your app URL**: `https://your-app-name.railway.app`

---

## 🆓 **Option 2: Render**

### Why Render?
- ✅ **Free static sites**
- ✅ **Limited free web services**
- ✅ **PostgreSQL available**
- ✅ **Easy setup**

### Step-by-Step Deployment:

#### 1. Sign Up
1. **Visit**: [render.com](https://render.com)
2. **Sign up** with GitHub

#### 2. Create Web Service
1. **Click "New"** → **"Web Service"**
2. **Connect your GitHub repo**
3. **Configure settings**:
   - **Name**: `jobboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn jobboard.wsgi:application`

#### 3. Add Environment Variables
```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
```

#### 4. Add PostgreSQL Database
1. **Click "New"** → **"PostgreSQL"**
2. **Copy the DATABASE_URL** to environment variables

#### 5. Deploy
1. **Click "Create Web Service"**
2. **Wait for deployment**
3. **Visit your app**: `https://your-app-name.onrender.com`

---

## 🆓 **Option 3: PythonAnywhere**

### Why PythonAnywhere?
- ✅ **Free Python hosting**
- ✅ **Django support**
- ✅ **Easy setup**
- ✅ **Good for beginners**

### Step-by-Step Deployment:

#### 1. Sign Up
1. **Visit**: [pythonanywhere.com](https://pythonanywhere.com)
2. **Create free account**

#### 2. Upload Your Code
1. **Go to "Files" tab**
2. **Upload your project** or use Git
3. **Extract files** to `/home/yourusername/jobboard`

#### 3. Create Virtual Environment
```bash
# In PythonAnywhere bash console
cd jobboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Configure Web App
1. **Go to "Web" tab**
2. **Click "Add a new web app"**
3. **Choose "Django"**
4. **Set source code**: `/home/yourusername/jobboard`
5. **Set working directory**: `/home/yourusername/jobboard`

#### 5. Configure WSGI File
Edit the WSGI file to point to your project:
```python
import os
import sys

path = '/home/yourusername/jobboard'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'jobboard.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 6. Set Environment Variables
In the web app configuration:
```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
```

#### 7. Deploy
1. **Click "Reload"**
2. **Visit**: `https://yourusername.pythonanywhere.com`

---

## 🆓 **Option 4: Fly.io**

### Why Fly.io?
- ✅ **3 free VMs**
- ✅ **Global deployment**
- ✅ **PostgreSQL available**
- ✅ **Good performance**

### Step-by-Step Deployment:

#### 1. Install Fly CLI
```bash
# macOS
brew install flyctl

# Or download from: https://fly.io/docs/hands-on/install-flyctl/
```

#### 2. Sign Up
```bash
fly auth signup
```

#### 3. Create App
```bash
cd jobboard
fly launch
```

#### 4. Configure Database
```bash
fly postgres create
fly postgres attach <database-name>
```

#### 5. Deploy
```bash
fly deploy
```

---

## 🔧 **Post-Deployment Setup**

### 1. Run Migrations
```bash
# For Railway/Render (via dashboard console)
python manage.py migrate

# For PythonAnywhere (via bash console)
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Create Sample Data
```bash
python manage.py create_sample_data
```

### 4. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 🛠️ **Troubleshooting**

### Common Issues:

#### 1. **Static Files Not Loading**
- Make sure `STATIC_ROOT` is set
- Run `python manage.py collectstatic`
- Check `whitenoise` is in `MIDDLEWARE`

#### 2. **Database Connection Error**
- Check `DATABASE_URL` environment variable
- Ensure PostgreSQL is running
- Verify database credentials

#### 3. **500 Server Error**
- Check logs in platform dashboard
- Verify `SECRET_KEY` is set
- Check `ALLOWED_HOSTS` includes your domain

#### 4. **Media Files Not Working**
- For production, consider using AWS S3 or similar
- Or configure platform-specific file storage

---

## 🔒 **Security Checklist**

- ✅ **SECRET_KEY** is set and secure
- ✅ **DEBUG=False** in production
- ✅ **ALLOWED_HOSTS** is configured
- ✅ **HTTPS** is enabled
- ✅ **Database** is secure
- ✅ **Static files** are served properly

---

## 📊 **Cost Comparison**

| Platform | Free Tier | Database | Custom Domain | Ease of Use |
|----------|-----------|----------|---------------|-------------|
| **Railway** | $5/month | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Render** | Limited | ✅ | ✅ | ⭐⭐⭐⭐ |
| **PythonAnywhere** | Free | ❌ | ❌ | ⭐⭐⭐⭐⭐ |
| **Fly.io** | 3 VMs | ✅ | ✅ | ⭐⭐⭐ |

---

## 🎯 **Recommendation**

**For beginners**: Start with **Railway** - it's the most Heroku-like experience with a generous free tier.

**For learning**: Try **PythonAnywhere** - it's completely free and great for Django.

**For performance**: Use **Fly.io** - it's fast and has good free limits.

---

## 🚀 **Next Steps**

1. **Choose a platform** from above
2. **Follow the deployment guide**
3. **Set up your database**
4. **Configure environment variables**
5. **Deploy and test**
6. **Share your live app!**

Your Django Job Board will be live on the internet! 🌐
