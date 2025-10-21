#!/bin/bash

echo "🚀 AI Attendance System - Quick Deploy Script"
echo "============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - AI Attendance System"
fi

echo ""
echo "🎯 Choose your deployment platform:"
echo "1. Railway (Free - Recommended)"
echo "2. Render (Free)"
echo "3. Heroku (Paid)"
echo "4. Manual Setup Instructions"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚄 Railway Deployment Selected"
        echo ""
        echo "📋 Steps to deploy on Railway:"
        echo "1. Install Railway CLI: npm install -g @railway/cli"
        echo "2. Login: railway login"
        echo "3. Deploy: railway deploy"
        echo "4. Set environment variables in Railway dashboard:"
        echo "   - MONGODB_URI: your_atlas_connection_string"
        echo "   - DATABASE_NAME: ai_attendance"
        echo ""
        echo "🔗 Visit: https://railway.app"
        ;;
    2)
        echo "🎨 Render Deployment Selected"
        echo ""
        echo "📋 Steps to deploy on Render:"
        echo "1. Push code to GitHub"
        echo "2. Connect GitHub to Render.com"
        echo "3. Create Web Service with these settings:"
        echo "   - Build Command: pip install -r backend/requirements.txt"
        echo "   - Start Command: gunicorn --chdir backend app:app"
        echo "4. Set environment variables:"
        echo "   - MONGODB_URI: your_atlas_connection_string"
        echo "   - DATABASE_NAME: ai_attendance"
        echo ""
        echo "🔗 Visit: https://render.com"
        ;;
    3)
        echo "🟣 Heroku Deployment Selected"
        echo ""
        echo "📋 Steps to deploy on Heroku:"
        echo "1. Install Heroku CLI"
        echo "2. heroku login"
        echo "3. heroku create your-app-name"
        echo "4. git push heroku main"
        echo "5. heroku config:set MONGODB_URI=your_connection_string"
        echo ""
        echo "🔗 Visit: https://heroku.com"
        ;;
    4)
        echo "📖 Manual Setup Instructions"
        echo ""
        echo "🛠️ Server Requirements:"
        echo "- Python 3.8+"
        echo "- MongoDB or MongoDB Atlas"
        echo "- Nginx (optional, for reverse proxy)"
        echo ""
        echo "📦 Installation:"
        echo "1. pip install -r backend/requirements.txt"
        echo "2. Set environment variables"
        echo "3. gunicorn --chdir backend app:app --bind 0.0.0.0:5000"
        echo ""
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

echo ""
echo "📝 Don't forget to:"
echo "✅ Set up MongoDB Atlas (free tier available)"
echo "✅ Configure environment variables"
echo "✅ Test camera permissions in browser"
echo "✅ Verify face detection works in production"
echo ""
echo "🎉 Your AI Attendance System is ready to deploy!"