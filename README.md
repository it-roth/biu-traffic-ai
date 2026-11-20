# BIU Traffic AI (`biu-traffic-ai`)
### BELTEI International University • AI-Powered Traffic Law Enforcement System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1%20REST%20Framework-green.svg)](https://www.djangoproject.com/)
[![Vue 3](https://img.shields.io/badge/Vue.js-3.5%20%2B%20Vite-4FC08D.svg)](https://vuejs.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8%20%2B%20ByteTrack-orange.svg)](https://ultralytics.com/)
[![Neon Database](https://img.shields.io/badge/Database-Neon%20Serverless%20PostgreSQL-00E599.svg)](https://neon.tech/)
[![Hugging Face Spaces](https://img.shields.io/badge/Hugging%20Face-Spaces%20Docker-FFD21E.svg)](https://huggingface.co/spaces)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS%203-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)]()

---

## 📌 Executive Overview

**BIU Traffic AI** (`biu-traffic-ai`) is an enterprise-grade intelligent surveillance and law enforcement system developed at **BELTEI International University (BIU)**. The platform integrates computer vision deep learning pipelines (**YOLOv8** + **ByteTrack**) with Cambodian traffic law enforcement engines (**Sub-Decree No. 39 Articles 8 & 44**), delivering real-time vehicle telemetry, helmet compliance auditing, passenger overload detection, and evidence archiving for police officers and university campus security.

Designed for production deployment on **Hugging Face Spaces** (Docker containerized on port `7860`) backed by a **Neon Serverless PostgreSQL** database.

---

## 🏛️ System Architecture & Engineering Blueprint

### 1. End-to-End Architectural Dataflow

```mermaid
flowchart TD
    subgraph ClientLayer ["1. Presentation Layer (Vue 3 + Vite)"]
        UI["Web SPA Dashboard\n(Tailwind CSS + Lucide Icons)"]
        CamView["Live MJPEG Monitor\n(Standby-Safe Stream)"]
        ScanView["AI Traffic Scanner\n(Image & Video Uploads)"]
        AuditView["Citation Review & Audit Trail\n(Sub-Decree No. 39 Queue)"]
    end

    subgraph GatewayAuth ["2. API & Security Gateway (Django REST + SimpleJWT)"]
        CORS["CORS & Origin Validation\n(5173 / Localhost / Frontend URL)"]
        JWT["SimpleJWT Authenticator\n(7-Day Token Lifetime)"]
        CSRF["CSRF & WhiteNoise Static Server"]
    end

    subgraph CoreServices ["3. Application & Enforcement Core"]
        AuthSvc["Account & RBAC Service\n(Officer vs Admin)"]
        ScanSvc["Traffic Scan Orchestrator\n(Multipart Media Parser)"]
        StreamSvc["MJPEG Stream Broadcaster\n(Non-blocking Buffer Queue)"]
        LawEngine["Cambodian Law Rule Engine\n(Sub-Decree No. 39 Arts. 8 & 44)"]
    end

    subgraph AIEngine ["4. Computer Vision Deep Learning Pipeline"]
        CVSource["OpenCV Ingestion\n(DirectShow / Webcam / RTSP / Video)"]
        YOLO["YOLOv8 Detection Model\n(Weights: best.pt / yolov8s.pt)"]
        Tracker["ByteTrack Multi-Object Tracker\n(Persistent Vehicle IDs)"]
        Cropper["Auto-Evidence Cropper\n(Infraction Region Extraction)"]
    end

    subgraph DataPersistence ["5. Data Persistence & Caching Layer"]
        DB[(Neon PostgreSQL Serverless\nDATABASE_URL via dj_database_url)]
        RedisCache[(Redis 7.0 Cache\nLive Telemetry & Sessions)]
        MediaStore[("Media File System\n/media/uploads\n/media/annotated\n/media/crops")]
    end

    UI --> GatewayAuth
    CamView --> StreamSvc
    ScanView --> ScanSvc
    AuditView --> GatewayAuth

    GatewayAuth --> AuthSvc
    GatewayAuth --> ScanSvc
    GatewayAuth --> StreamSvc

    ScanSvc --> YOLO
    StreamSvc --> CVSource
    CVSource --> YOLO
    YOLO --> Tracker
    Tracker --> LawEngine
    LawEngine --> Cropper

    Cropper --> MediaStore
    LawEngine --> DB
    AuthSvc --> DB
    StreamSvc --> RedisCache
    ScanSvc --> MediaStore
```

---

## ⚖️ Cambodian Traffic Law Engine (Sub-Decree No. 39)

The AI engine automatically cross-references vision detections with Cambodia's **Sub-Decree No. 39 on Road Traffic Fines**:

| Infraction Type | Legal Basis | Standard Fine (KHR) | Approx. USD | System Action |
| :--- | :--- | :--- | :--- | :--- |
| **No Helmet** | Sub-Decree No. 39 • Article 8 | **60,000 KHR** | ~\$15 | Red HUD bounding box, auto-crop evidence |
| **Passenger Overload** | Sub-Decree No. 39 • Article 44 | **100,000 KHR** | ~\$25 | Flagged when riders $> 2$ on motorcycle |
| **Dual Infraction** | Articles 8 & 44 Combined | **160,000 KHR** | ~\$40 | Dual citation penalty, high-priority flag |
| **Compliant Passage** | Law Compliant | **0 KHR** | \$0 | Green HUD bounding box, logged as compliant |

---

## 📊 Dataset & AI Model Specifications

### Cambodian Road Traffic Dataset
* **Dataset Domain**: Phnom Penh metropolitan traffic corridors (Monivong Blvd, Russian Blvd, Norodom Blvd).
* **Target Classes (10 classes)**:
  1. `car` — Passenger automobiles, sedans, SUVs
  2. `motorcycle` — Two-wheeled motorbikes and scooters
  3. `auto_rickshaw` — Three-wheeled PassApp / Bajaj autorickshaws
  4. `remorque` — Traditional Khmer motorcycle-trailer tuk-tuks
  5. `truck` — Heavy commercial logistics vehicles
  6. `bus` — City transit and regional passenger buses
  7. `rider_helmet` — Motorcycle rider with compliant safety helmet
  8. `rider_no_helmet` — Motorcycle rider without safety helmet (Sub-Decree 39 Article 8 violation)
  9. `traffic_light_red` — Intersection traffic control signal (Stop)
  10. `traffic_light_green` — Intersection traffic control signal (Go)
* **Model Benchmark**:
  * Architecture: YOLOv8 Small (`yolov8s.pt` / `best.pt`)
  * Parameters: 3.01 Million Parameters (8.1 GFLOPs)
  * Evaluation: **`rider_no_helmet` mAP50 = 99.5%**
  * Tracker: ByteTrack Multi-Object Tracker with trajectory assignment

---

## 🚀 Production Deployment Guide

### Option 1: Hugging Face Spaces (Docker SDK)

1. **Create Space**:
   * Go to [Hugging Face Spaces](https://huggingface.co/spaces) → **Create new Space**.
   * Choose **Docker** as the Space SDK (Blank template).
   * Space Name: `biu-traffic-ai` (or your choice).

2. **Configure Environment Secrets & Variables**:
   In Space Settings → **Variables and Secrets**, add:

   | Variable / Secret Name | Type | Value / Description |
   |---|---|---|
   | `DATABASE_URL` | **Secret** | Neon PostgreSQL connection string (e.g. `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`) |
   | `SECRET_KEY` | **Secret** | Production Django secret key |
   | `DEBUG` | Variable | `False` |
   | `CORS_ALLOWED_ORIGINS` | Variable | `https://your-frontend-app.vercel.app,http://localhost:5173` |
   | `CORS_ALLOW_ALL_ORIGINS`| Variable | `True` (or `False` for strict origin pinning) |

3. **Deploy Repository**:
   * Push your backend repository (with `Dockerfile`, `requirements.txt`, and source files).
   * Hugging Face Spaces will automatically build the `Dockerfile`, install dependencies, run `collectstatic`, and start Gunicorn on port **7860**.

---

### Option 2: Neon Serverless PostgreSQL Setup

1. Create a free database instance on [Neon.tech](https://neon.tech/).
2. Copy your **Pooled Connection String**:
   ```text
   postgresql://[user]:[password]@[endpoint].neon.tech/[dbname]?sslmode=require
   ```
3. Set `DATABASE_URL` in your `.env` or deployment secrets. Django uses `dj_database_url` to automatically configure SSL-secured connections with connection pooling (`conn_max_age=600`).
4. Run migrations:
   ```bash
   python manage.py migrate
   ```

---

### Option 3: Local Development Setup

#### Backend (Django REST API)
```bash
cd backend

# Create & activate virtual environment
python -m venv django
.\django\Scripts\activate   # Windows
source django/bin/activate  # Linux/macOS

# Install dependencies (CPU PyTorch + OpenCV)
pip install -r requirements.txt

# Run migrations & start server
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

#### Frontend (Vue 3 + Vite)
```bash
cd frontend

# Install node packages
npm install

# Start Vite dev server
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 📡 REST API Reference

### Authentication
* `POST /api/auth/login/` — Authenticate officer and receive JWT access (7-day) & refresh tokens.
* `POST /api/auth/token/refresh/` — Obtain a fresh JWT access token.
* `GET  /api/auth/protected/` — Retrieve authenticated officer profile, role, and permissions.

### AI Traffic Inference
* `POST /api/scan/image/` — Upload an image for YOLOv8 detection, helmet verification, and law citation.
* `POST /api/scan/video/` — Upload a video for frame-by-frame ByteTrack tracking and violation extraction.
* `GET  /api/traffic/stream/` — Live multipart MJPEG video stream with real-time HUD overlays.
* `POST /api/traffic/stream/stop/` — Instant hardware camera release endpoint.
* `GET  /api/traffic/stats/` — Real-time telemetry aggregate (vehicle counts, compliance rate, active checkpoints).
* `GET  /api/violations/` — Paginated history of violation records with auto-cropped evidence URLs.

---

## 👥 Project Team & Contributors

### Final Capstone Submission — BELTEI International University (BIU)
**Faculty**: Information Technology & Science  
**Department**: Computer Science & Software Engineering  
**Academic Year**: 2025 – 2026  

| No. | Student Name | Student ID | Role & Responsibilities |
| :---: | :--- | :---: | :--- |
| **01** | `Leng Saroth` | `00057189` | **Team Lead & Computer Vision Engineer**<br>• YOLOv8 custom training & ByteTrack tracking pipeline<br>• Model optimization & Cambodian road dataset annotation |
| **02** | `[Student Name 2]` | `[ID: XXXXXXXX]` | **Full-Stack Backend Engineer**<br>• Django 6.1 REST Framework, SimpleJWT auth & Neon DB<br>• Video MJPEG streaming engine & Sub-Decree No. 39 law logic |
| **03** | `[Student Name 3]` | `[ID: XXXXXXXX]` | **Frontend Engineer & UI/UX Designer**<br>• Vue 3.5, Vite & Tailwind CSS command center<br>• Real-time HUD surveillance feed & bilingual Khmer/EN localization |
| **04** | `[Student Name 4]` | `[ID: XXXXXXXX]` | **DevOps & QA Engineer**<br>• Docker containerization, Hugging Face Spaces deployment<br>• End-to-end testing, evidence archiving & security audit |

### 🎓 Academic Supervision
* **Project Advisor**: `Dr.Chen Sovann`
* **Institution**: BELTEI International University • Campus 10, Phnom Penh, Kingdom of Cambodia

---

© 2026 BELTEI International University • Cambodia Traffic Law Enforcement System. All rights reserved.
