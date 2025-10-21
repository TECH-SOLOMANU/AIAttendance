# 🎯 AI Attendance System

A complete face recognition-based attendance system built with Flask, OpenCV, and MongoDB.

## ✨ Features

- 👤 **Student Registration** with face capture
- 🔍 **Automatic Face Recognition** for attendance
- 🚫 **Duplicate Prevention** (by roll number and face matching)
- 📊 **Excel/CSV Export** (Students, Attendance, Daily Reports)
- 🌐 **Modern Web Interface** with real-time camera
- 💾 **MongoDB Integration** with local fallback

## 🚀 Deployment Options

### Option 1: Railway (Recommended - Free Tier)

1. **Create a Railway account** at [railway.app](https://railway.app)

2. **Set up MongoDB Atlas** (Free):
   - Go to [mongodb.com/atlas](https://mongodb.com/atlas)
   - Create free cluster
   - Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/ai_attendance`

3. **Deploy to Railway**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Deploy
   railway deploy
   ```

4. **Set Environment Variables in Railway**:
   - `MONGODB_URI`: Your Atlas connection string
   - `DATABASE_NAME`: ai_attendance
   - `PORT`: 5000

### Option 2: Render (Free Tier)

1. **Fork this repo** to your GitHub
2. **Go to [render.com](https://render.com)** and connect GitHub
3. **Create Web Service**:
   - Root Directory: `/`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `gunicorn --chdir backend app:app`
4. **Set Environment Variables**:
   - `MONGODB_URI`: Your Atlas connection string
   - `DATABASE_NAME`: ai_attendance

### Option 3: DigitalOcean App Platform

1. **Connect GitHub repo** to DigitalOcean
2. **App Spec**:
   ```yaml
   name: ai-attendance
   services:
   - name: web
     source_dir: /
     build_command: pip install -r backend/requirements.txt
     run_command: gunicorn --chdir backend app:app
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
   ```

## 🔧 Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd AiAttendance
   ```

2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run locally**:
   ```bash
   cd backend
   python app.py
   ```

4. **Open browser**: http://localhost:5000

## 📝 Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=ai_attendance

# Server
PORT=5000
FLASK_ENV=production

# CORS
CORS_ORIGINS=*
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Face Detection**: OpenCV
- **Frontend**: HTML/CSS/JavaScript
- **Export**: Pandas, OpenPyXL
- **Deployment**: Gunicorn

## 📋 API Endpoints

- `GET /` - Main interface
- `POST /register` - Register new student
- `POST /recognize` - Mark attendance
- `GET /export/students/<format>` - Export students data
- `GET /export/attendance/<format>` - Export attendance records
- `GET /export/daily-report/<date>/<format>` - Export daily report

## 🔐 Security Notes

- Change default MongoDB credentials
- Use environment variables for sensitive data
- Enable MongoDB authentication in production
- Consider adding rate limiting for API endpoints

## 📱 Browser Compatibility

- Chrome/Edge (Recommended)
- Firefox
- Safari
- Requires camera permissions

## 🎉 Usage

1. **Register Students**: Use webcam to capture student photos with roll numbers
2. **Mark Attendance**: Students look at camera for automatic recognition
3. **Export Data**: Download attendance reports in Excel/CSV format
4. **View Results**: Real-time feedback for successful registrations/attendance

## 🐛 Troubleshooting

- **Camera not working**: Check browser permissions
- **Face not detected**: Ensure good lighting and clear face view
- **Database connection**: Verify MongoDB URI and network access
- **Export not working**: Check pandas/openpyxl installation

## 📄 License

MIT License - feel free to modify and distribute!

---

Built with ❤️ for efficient attendance management