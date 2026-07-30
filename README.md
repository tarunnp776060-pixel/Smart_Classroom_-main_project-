# Real-Time Classroom Attentiveness Detection and Automated Attendance System

> **B.E. Final-Year Engineering Project**  
> **Department of Artificial Intelligence & Data Science**

A complete, AI-powered classroom monitoring application combining real-time face recognition for automated attendance with multi-factor visual attentiveness detection (Eye Aspect Ratio, 3D Head Pose estimation, and expression analysis).

---

## 🌟 Features Overview

1. **Teacher / Admin Authentication & Session Management**:
   - Secure login with pre-configured demo account (`admin` / `admin123`).
   - Create and manage classroom sessions (Subject Name, Class/Section, Date/Time).

2. **Student Directory & Face Profile Registration**:
   - Register students with ID, Roll Number, Department, Semester, and Email.
   - **Interactive Live Webcam Capture**: Capture student face images directly from webcam and compute 128-dimensional feature embeddings.
   - Profile Photo upload support with automated face landmark encoding generation.

3. **Real-Time Automated Attendance**:
   - Detects faces in live video streams.
   - Matches face feature embeddings against registered database encodings using Cosine Similarity.
   - Automatically marks student attendance for active class sessions.
   - Prevents duplicate attendance logging within the same session.
   - Labels unrecognized faces as `Unknown Student`.

4. **Multi-Factor Visual Attentiveness Detection**:
   - **Eye Tracking (EAR)**: Computes Eye Aspect Ratio from MediaPipe 468 3D landmarks to detect `Eyes Open`, `Blinking`, and `Eyes Closed / Drowsy`.
   - **3D Head Pose Estimation**: Maps facial keypoints to 3D canonical model and solves Perspective-n-Point (`cv2.solvePnP`) to compute Pitch, Yaw, and Roll Euler angles (`Facing Forward`, `Looking Left`, `Looking Right`, `Looking Up`, `Looking Down`).
   - **Expression Analysis**: Calculates mouth aspect ratio to flag yawning and disengagement.

5. **Explainable Attention Scoring Engine**:
   - Normalizes visual metrics into a **0 – 100 Attention Index**:
     \[ \text{Score} = 100 - P_{\text{eye}} - P_{\text{yaw}} - P_{\text{pitch}} - P_{\text{yawn}} \]
   - Classifies student attention state into:
     - 🟢 **Attentive** (Score $\ge 80$)
     - 🟠 **Partially Attentive** ($50 \le \text{Score} < 80$)
     - 🔴 **Inattentive** ($\text{Score} < 50$)

6. **Live Classroom HUD Monitoring & Dual Video Source**:
   - Real-time video player displaying bounding boxes, student names, attention badges, eye state, and head pose.
   - Toggle between **📷 Live Laptop Webcam** and **🎬 Demo Classroom Video Mode** for seamless viva evaluation.

7. **Executive Analytics Dashboard & Export Reports**:
   - Interactive Chart.js graphs (Attendance rates, Attentiveness distribution, Attention timeline trends, Student-wise comparisons).
   - Filterable attendance and attentiveness logs.
   - **CSV & Printable PDF Export** for institutional records.

8. **Viva & Project Architecture Page**:
   - Dedicated page explaining the end-to-end computer vision pipeline, data flow diagram, mathematical models, and ethical guidelines.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask, Flask-SQLAlchemy, Flask-Login
- **Computer Vision & AI**: OpenCV (`opencv-python`), MediaPipe (`mediapipe`), NumPy, SciPy (`solvePnP`)
- **Database**: SQLite (`instance/database.db`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Chart.js, FontAwesome 6

---

## 📁 Project Directory Structure

```
classroom_attentiveness_system/
│
├── app.py                     # Main Flask application entry point
├── config.py                  # App configuration & settings
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive project documentation
│
├── database/
│   ├── __init__.py
│   ├── database.py            # DB initialization & demo data seeder
│   └── models.py              # SQLAlchemy ORM database schemas
│
├── ai/
│   ├── __init__.py
│   ├── face_detection.py      # MediaPipe Face Detector
│   ├── face_recognition.py    # Face Embedding Extractor & Cosine Similarity Matcher
│   ├── eye_tracking.py        # Eye Aspect Ratio (EAR) computation
│   ├── head_pose.py           # 3D Head Pose Estimator (SolvePnP)
│   ├── expression.py          # Mouth openness & Yawning analyzer
│   ├── attention.py           # Explainable Attention Scoring Engine
│   └── pipeline.py            # Combined Real-Time Video Frame Processor & HUD Overlay
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                # Login, Logout, Session management
│   ├── students.py            # Student CRUD & webcam face capture endpoints
│   ├── attendance.py          # Attendance query & class session management
│   ├── monitoring.py          # Video stream feed (`/video_feed`) & live HUD stats API
│   ├── analytics.py           # Chart.js analytics API endpoints
│   └── reports.py             # Filterable reports & CSV export routes
│
├── templates/
│   ├── base.html              # Core layout (Sidebar, Navbar, Theme)
│   ├── login.html             # Teacher login page with demo prefill
│   ├── dashboard.html         # Executive monitoring dashboard
│   ├── monitoring.html        # Real-time classroom live monitor page
│   ├── students.html          # Student directory & registration modal
│   ├── student_detail.html    # Student profile & webcam face capture
│   ├── sessions.html          # Class session creation & control
│   ├── attendance.html        # Automated attendance logs table
│   ├── analytics.html         # Attentiveness analytics & charts
│   ├── reports.html           # Report generation & CSV export
│   └── architecture.html      # Final-Year Viva presentation & system pipeline
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern dark dashboard styling
│   └── js/
│       ├── monitoring.js      # Webcam stream controller & HUD stats poller
│       └── analytics.js       # Chart.js visualization renderer
│
├── dataset/
│   └── students/              # Registered student face images
│
└── instance/
    └── database.db            # SQLite Database file
```

---

## ⚡ Quick Setup & Installation Guide

### Step 1: Open Terminal in Project Directory
Navigate to the project root:
```bash
cd C:\Users\tarun\.gemini\antigravity\scratch\classroom_attentiveness_system
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Launch Application Server
```bash
python app.py
```

Open your web browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Demo Account Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Teacher / Admin** | `admin` | `admin123` |

*(The system automatically seeds demo students Alex Johnson, Priya Sharma, Rahul Verma, Emily Davis, and Mohammed Ali on first run).*

---

## 🧪 Testing the Complete Workflow (Viva Demonstration Instructions)

1. **Login**: Go to `http://127.0.0.1:5000/login` and click **Log In** (prefilled with `admin` / `admin123`).
2. **Class Session**: Navigate to **Class Sessions** and verify an active session is running (or create a new subject session like *Artificial Intelligence & Data Science*).
3. **Live Monitoring**:
   - Go to **Live Monitoring**.
   - Select **📷 Live Laptop Webcam** to test real-time monitoring with your camera, OR select **🎬 Demo Classroom Video Mode** if testing without a camera.
   - Observe real-time face bounding boxes, student identification tags, Eye Aspect Ratio status (`Eyes Open` / `Drowsy`), Head Pose orientation (`Facing Forward` / `Looking Left`), and Attention Score badges updating live!
4. **Automated Attendance Verification**:
   - Go to **Attendance Logs** to confirm attendance has been automatically recorded with date, time, and confidence score.
5. **Student Face Registration**:
   - Go to **Students Directory** -> Click **Register New Student**.
   - Open student profile -> Click **Capture Face Profile via Webcam** to register new face embeddings live.
6. **Analytics & Reports**:
   - Navigate to **Attention Analytics** to view interactive Chart.js charts.
   - Go to **Reports & Exports** -> Click **Export Attendance CSV** or **Export Attentiveness CSV**.
7. **Viva Presentation**:
   - Open **System Architecture** page to present the pipeline diagram and methodology to evaluators.

---

## ⚖️ Privacy and Ethical Considerations

- **Visual Estimation Disclaimer**: Attention scores are computer vision estimations based on eye closure and head orientation. They are designed for educational feedback and must not be used as the sole metric for grading or disciplinary action.
- **Data Protection**: Face feature embeddings are stored as mathematical arrays in SQLite. Raw video feeds are never saved to disk.
