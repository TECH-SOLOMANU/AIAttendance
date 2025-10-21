# 📄 Product Requirement Document (PRD)

**Project Title:** AI-Based Attendance System Using Face Recognition
**Tech Stack:** HTML, CSS, Python (Flask), MongoDB

---

## 1. Problem Statement

* Manual attendance wastes 5–10 minutes of class time.
* Proxy attendance is common, reducing accuracy.
* Teachers don’t have a simple digital solution to manage attendance and generate reports.

---

## 2. Objectives

* Automate attendance using face recognition.
* Eliminate proxy attendance.
* Generate daily/monthly reports automatically.
* Provide a simple web-based system (works on any laptop with webcam).

---

## 3. Scope

* Web application accessible via browser.
* Works with any standard laptop/desktop camera.
* Student face registration + live recognition.
* Data stored in MongoDB.
* Admin dashboard for teachers to download reports.

---

## 4. Key Features

1. **Student Registration** – Capture face & store encodings with roll number & name.
2. **Face Recognition** – Detect faces in live webcam feed, match with database.
3. **Attendance Marking** – Update MongoDB with student status (present/absent).
4. **Reports** – Generate CSV/PDF reports per date.
5. **Web UI** – Teacher-friendly interface with HTML/CSS.

---

## 5. Functional Requirements

* **Input:** Webcam image/video.
* **Processing:**

  * OpenCV detects face.
  * Face encodings compared with registered database.
  * If match ≥ threshold → mark as present.
* **Output:** Attendance records in MongoDB + downloadable reports.

---

## 6. Non-Functional Requirements

* Accuracy ≥ 90% with multiple encodings per student.
* Low latency (<2 sec recognition).
* Secure DB storage.
* Works offline (local MongoDB).

---

## 7. System Architecture

```
Frontend (HTML/CSS/JS) → Flask Backend (Python + OpenCV + Face Recognition) → MongoDB  
```

---

## 8. Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (Flask)
* **Database:** MongoDB
* **Libraries:** OpenCV, face_recognition, pymongo

---

## 9. Success Metrics

* Reduce attendance time from 10 min → <1 min.
* 90%+ recognition accuracy.
* 100% elimination of proxy attendance.

---
