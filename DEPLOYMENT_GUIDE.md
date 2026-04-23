# 🚀 PyMultiGuard Web App - Deployment Guide

## ✅ What You Have Now

### Web Application (Frontend + Backend)
- **Backend:** `app.py` (Flask Python server)
- **Frontend:** `templates/index.html` + `static/css/style.css` + `static/js/main.js`
- **Deployment:** Ready for Render (free hosting)

---

## 🌐 How to Deploy (Get a Link for Your Teacher)

### Option 1: Render.com (Recommended - FREE)

#### Step 1: Create GitHub Repository
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "PyMultiGuard web application"

# Create repository on GitHub.com
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/pymultiguard.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy on Render

1. **Go to:** https://render.com
2. **Sign up** with GitHub account (free)
3. **Click:** "New +" → "Web Service"
4. **Connect** your GitHub repository
5. **Configure:**
   - Name: `pymultiguard`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance Type: `Free`

6. **Add Environment Variables** (IMPORTANT!):
   - `EMAIL_ADDRESS` = your-email@gmail.com
   - `EMAIL_PASSWORD` = your-app-password
   - `IMAP_HOST` = imap.gmail.com
   - `IMAP_PORT` = 993
   - `OPENAI_API_KEY` = gsk_your_groq_key
   - `OPENAI_BASE_URL` = https://api.groq.com/openai/v1
   - `MODEL_NAME` = llama-3.1-8b-instant

7. **Click:** "Create Web Service"

8. **Wait** 5-10 minutes for deployment

9. **Get your URL:** `https://pymultiguard.onrender.com`

10. **Share this URL with your teacher!**

---

### Option 2: PythonAnywhere (Alternative - FREE)

#### Step 1: Sign Up
1. Go to: https://www.pythonanywhere.com
2. Create free account
3. Click "Web" tab

#### Step 2: Upload Code
1. Click "Files" tab
2. Upload all your files:
   - `app.py`
   - `requirements.txt`
   - `templates/` folder
   - `static/` folder
   - All `.py` modules

#### Step 3: Configure
1. Click "Web" tab
2. "Add a new web app"
3. Choose "Flask"
4. Python version: 3.10
5. Set path to `app.py`

#### Step 4: Install Dependencies
1. Click "Consoles" tab
2. Start Bash console
3. Run:
```bash
pip install -r requirements.txt
```

#### Step 5: Set Environment Variables
1. Click "Web" tab
2. Scroll to "Environment variables"
3. Add all your `.env` variables

#### Step 6: Reload
1. Click "Reload" button
2. Your URL: `https://YOUR_USERNAME.pythonanywhere.com`

---

### Option 3: Railway (Alternative - FREE)

1. Go to: https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables
6. Deploy!
7. Get URL: `https://pymultiguard.up.railway.app`

---

## 🎯 Quick Test (Before Deploying)

### Test Locally First:
```bash
# Start the server
python app.py

# Open browser
http://localhost:5000

# Click "Analyze Emails"
# Verify it works!
```

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] `.env` file has correct credentials
- [ ] All dependencies in `requirements.txt`
- [ ] Test locally: `python app.py` works
- [ ] You have 5+ unread emails in Gmail
- [ ] Groq API key is valid (starts with `gsk_`)
- [ ] Gmail App Password is correct (not regular password)

---

## 🎤 For Your Teacher

**Send this message with the link:**

> "Hello Professor,
> 
> Here is my Information Security project - PyMultiGuard Email Security Analyzer:
> 
> **Live Demo:** https://pymultiguard.onrender.com
> 
> This is a web application that analyzes emails for security threats. It provides:
> - Spam detection using AI
> - Sender intelligence (company lookup)
> - Data collection analysis (what they know about you)
> - Email source tracking (how they got your email)
> - Link safety analysis (phishing detection)
> 
> Please click "Analyze Emails" to see the live analysis.
> 
> Note: First load may take 30-60 seconds as the free server wakes up.
> 
> Thank you!"

---

## ⚠️ Important Notes

### Free Tier Limitations:

**Render.com:**
- ✅ Free forever
- ⚠️ Server sleeps after 15 min inactivity
- ⚠️ First load takes 30-60 seconds (cold start)
- ✅ 750 hours/month free

**PythonAnywhere:**
- ✅ Free forever
- ✅ Always on (no cold start)
- ⚠️ Limited CPU time
- ⚠️ Must reload every 3 months

**Railway:**
- ✅ $5 free credit/month
- ✅ Fast deployment
- ⚠️ Credit runs out after heavy use

### Security:

**NEVER commit `.env` file to GitHub!**
- It contains your passwords
- Add it to `.gitignore`
- Set environment variables on hosting platform

---

## 🐛 Troubleshooting

### "Application Error" on Render
**Problem:** Server crashed

**Solutions:**
1. Check Render logs (click "Logs" tab)
2. Verify environment variables are set
3. Make sure `requirements.txt` has all dependencies
4. Check Gmail credentials are correct

### "502 Bad Gateway"
**Problem:** Server not responding

**Solutions:**
1. Wait 60 seconds (cold start)
2. Check if deployment finished
3. Restart the service

### "No emails found"
**Problem:** Can't connect to Gmail

**Solutions:**
1. Verify `EMAIL_ADDRESS` environment variable
2. Verify `EMAIL_PASSWORD` is App Password (not regular password)
3. Check `IMAP_HOST` = imap.gmail.com
4. Check `IMAP_PORT` = 993

### "API Error"
**Problem:** Groq API not working

**Solutions:**
1. Verify `OPENAI_API_KEY` starts with `gsk_`
2. Check you have free tier credits
3. Verify `OPENAI_BASE_URL` = https://api.groq.com/openai/v1

---

## 📦 Files Needed for Deployment

Make sure these files exist:

```
pymultiguard-1/
├── app.py                          # Flask backend
├── requirements.txt                # Dependencies
├── Procfile                        # Deployment config
├── render.yaml                     # Render config
├── templates/
│   └── index.html                  # Frontend HTML
├── static/
│   ├── css/
│   │   └── style.css              # Styling
│   └── js/
│       └── main.js                # Frontend logic
├── groq_spam_classifier.py        # AI module
├── sender_intelligence.py         # Intelligence module
├── data_collection_analyzer.py    # Privacy module
├── email_source_analyzer.py       # Source tracking
├── link_safety_analyzer.py        # Link analysis
├── imap_reader.py                 # Gmail connection
├── security/                       # Security modules
│   ├── encryption.py
│   ├── pii_anonymizer.py
│   └── audit_logger.py
└── .gitignore                     # Don't commit secrets
```

---

## 🎓 Presentation Tips

### When Showing to Teacher:

1. **Open the URL** in browser
2. **Explain:** "This is a live web application deployed on Render"
3. **Click:** "Analyze Emails" button
4. **Wait:** 30-60 seconds for analysis
5. **Show:** Color-coded results
6. **Highlight:** 4 unique intelligence features
7. **Explain:** "Anyone can access this URL - no installation needed"

### Key Talking Points:

- "This is a full-stack web application"
- "Frontend: HTML/CSS/JavaScript"
- "Backend: Python Flask"
- "Deployed on cloud hosting (Render)"
- "Real-time email analysis with AI"
- "Production-ready with security features"

---

## ✅ Success Criteria

You'll know deployment worked when:

- ✓ You can open the URL in browser
- ✓ Page loads with PyMultiGuard interface
- ✓ "Analyze Emails" button works
- ✓ Results appear after 30-60 seconds
- ✓ All 4 intelligence sections show data
- ✓ Teacher can access the same URL

---

## 🚀 Next Steps

1. **Test locally:** `python app.py`
2. **Create GitHub repo** and push code
3. **Deploy on Render** (follow steps above)
4. **Get your URL:** `https://pymultiguard.onrender.com`
5. **Test the live URL** yourself first
6. **Share with teacher**

---

**You're almost there! Just deploy and you'll have a live URL to share! 🎉**

**Information Security Class Project - 2026**
