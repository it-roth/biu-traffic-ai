# BIU Traffic AI (`biu-traffic-ai`)
### BELTEI International University • AI-Powered Traffic Law Enforcement System

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1%20REST%20Framework-green.svg)](https://www.djangoproject.com/)
[![Vue 3](https://img.shields.io/badge/Vue.js-3.5%20%2B%20Vite-4FC08D.svg)](https://vuejs.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8%20%2B%20ByteTrack-orange.svg)](https://ultralytics.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS%203-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-BIU%20Academic-red.svg)]()

---

## 📌 Overview

**BIU Traffic AI** (`biu-traffic-ai`) is an enterprise-grade intelligent surveillance and law enforcement system developed at **BELTEI International University (BIU)**. The platform integrates computer vision deep learning pipelines (**YOLOv8** + **ByteTrack**) with Cambodian traffic law enforcement engines (**Sub-Decree No. 39 Articles 8 & 44**), delivering real-time vehicle telemetry, helmet compliance auditing, passenger overload detection, and evidence archiving for police officers and university campus security.

---

## 🏛️ System Architecture & Directory Structure

```text
biu-traffic-ai/
├── backend/                             # Django REST Framework Backend
│   ├── manage.py
│   ├── requirements.txt                 # Backend dependencies
│   ├── config/                          # Project configuration & settings
│   │   ├── settings.py                  # JWT (7-day), Redis sessions & CORS
│   │   ├── urls.py                      # Root URL routing & media endpoints
│   │   └── wsgi.py
│   ├── api/                             # AI Enforcement & Traffic Engine
│   │   ├── ai_engine.py                 # Cambodian traffic rule engine & YOLOv8
│   │   ├── inference.py                 # Live camera MJPEG streaming & HUD overlay
│   │   ├── models.py                    # ViolationRecord & TrafficViolation models
│   │   ├── serializers.py               # REST API serializers
│   │   └── views.py                     # Scan endpoints & live stats API
│   ├── accounts/                        # Authentication & RBAC
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── views.py                     # JWT Login, Register & Protected Profile
│   ├── weights/                         # Specialized AI model weights
│   │   └── best.pt                      # Custom helmet detection model
│   └── media/                           # Persisted media storage
│       ├── uploads/                     # Original police camera sources
│       ├── annotated/                   # YOLO annotated outputs
│       └── crops/                       # Auto-cropped evidence snapshots
│
├── frontend/                            # Vue 3 Single Page Application
│   ├── package.json                     # Frontend configuration (biu-traffic-ai)
│   ├── vite.config.js                   # Vite bundler configuration
│   ├── tailwind.config.js               # BELTEI dark theme styling
│   └── src/
│       ├── App.vue                      # Root layout
│       ├── router/index.js              # Navigation & auth route guards
│       ├── services/api.js              # Axios client with auto-token refresh
│       ├── components/
│       │   ├── Sidebar.vue              # Enterprise navigation (Operations vs Audit)
│       │   └── TopHeader.vue            # Breadcrumbs, quick search, 文A EN/KM toggle
│       └── views/
│           ├── Login.vue                # Officer & Admin authentication
│           ├── Register.vue             # Personnel registration
│           ├── Dashboard.vue            # Executive Command Center (CP-01 to CP-04)
│           ├── TrafficScanView.vue      # AI Scanner (1-Click Test feeds)
│           ├── LiveCameraView.vue       # Standby-safe surveillance streaming
│           ├── HistoryView.vue          # Audit Trail & Media Gallery
│           └── ViolationsView.vue       # Citation Queue (Sub-Decree No. 39)
│
├── deployment/                          # Containerization & Infrastructure
│   ├── docker-compose.yml               # PostgreSQL 18 & Redis 7 services
│   └── Dockerfile
│
├── yolo26s.pt                           # COCO vehicle scene model
├── yolov8n.pt                           # High-speed lightweight model
└── README.md                            # Comprehensive project documentation
```

---

## 🚀 Core Features

### 1. Operations Command Center
* **Executive Dashboard (`/dashboard`)**:
  * Live KPI widgets: Total scans, tracked cars, tracked motorcycles, helmet compliance rate, and flagged infractions.
  * Active patrol checkpoint telemetry across Phnom Penh (**CP-01 Monivong Blvd**, **CP-02 Russian Blvd**, **CP-03 Norodom Blvd**, **CP-04 BELTEI Campus 10**).
  * Real-time calculation of official citations under Sub-Decree No. 39 in Cambodian Riel (KHR) and USD.
  * AI pipeline health monitoring (YOLOv8x Vehicle Detector, YOLOv8 Helmet Specialist, ByteTrack Multi-Object Tracker, Cambodian Law Engine).

### 2. AI Traffic Scanner (`/scan`)
* **Multi-Format Processing**: Supports high-resolution imagery (`.jpg`, `.png`, `.webp`) and full-motion surveillance video (`.mp4`, `.avi`, `.mov`).
* **1-Click Test Feeds**: Integrated quick-loaders (`Sample 1: Monivong Traffic`, `Sample 2: Checkpoint Flow`) allowing immediate testing without manual file selection.
* **Side-by-Side Verification**: Inspect clean raw camera input alongside color-coded YOLOv8 bounding boxes.
* **Auto-Cropped Evidence Snapshots**: Automated sub-region cropping isolating infraction targets with fine details, legal citations, and confidence badges.
* **Cinema Lightbox Modal**: High-definition image modal with interactive zoom ($50\% - 300\%$) and keyboard hotkeys (`+`, `-`, `Esc`).

### 3. Live Camera Surveillance Feed (`/camera`)
* **Standby-Safe Video Engine**: Feed remains in standby mode on navigation ("don't stream immediately") until the operator explicitly clicks **Start Live Camera Feed**.
* **30 FPS Real-Time HUD Overlay**: Streams real-time MJPEG with live vehicle tracking bounding boxes and telemetry.
* **Hardware Resilience**: Automatically falls back to local video surveillance loops or animated CCTV HUD telemetry if physical webcams are offline or busy.

### 4. Audit Log & History (`/history`)
* **Dual Inspection Modes**: Switch effortlessly between the **Audit Table** (tabular officer view) and the **Media Gallery** (visual card layout).
* **Search & Filter**: Filter by media type (Images / Videos) and infraction status (All, Violations Only, Compliant).
* **Pagination**: Server-side pagination with seamless state retention.

### 5. Violation Records & Citation Queue (`/violations`)
* Dedicated law enforcement review queue indexing infractions with legal basis, timestamps, vehicle breakdowns, and fine calculations.

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

## 🛠️ Technology Stack

* **Backend**: Python 3.12+, Django 6.1, Django REST Framework, SimpleJWT (7-day access token lifetime, 30-day refresh lifetime).
* **Computer Vision**: Ultralytics YOLOv8, OpenCV 4.10, ByteTrack Multi-Object Tracking.
* **Frontend**: Vue 3.5 (Composition API `<script setup>`), Vite 8, Tailwind CSS 3, Axios with automatic token refresh interceptor.
* **Storage & Caching**: SQLite 3 (Development), PostgreSQL 18 (Production), Redis 7 (Session & Cache).
* **Localization**: Bilingual support (English & Khmer - 文A EN | ខ្មែរ).

---

## ⚙️ Installation & Setup Guide

### Prerequisites
* **Python** 3.12 or newer
* **Node.js** 20+ and **npm**
* **Git**

---

### 1. Clone & Enter Project

```bash
git clone https://github.com/your-org/biu-traffic-ai.git
cd biu-traffic-ai
```

---

### 2. Backend Setup (Django)

```bash
cd backend

# Create virtual environment
python -m venv django

# Activate virtual environment
# Windows:
.\django\Scripts\activate
# Linux/macOS:
source django/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create initial admin account (or use default)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

The Django REST API runs at `http://localhost:8000`.

---

### 3. Frontend Setup (Vue 3 + Vite)

In a separate terminal:

```bash
cd biu-traffic-ai/frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```

The web application opens at `http://localhost:5173`.

---

### 4. Production Infrastructure (Docker Compose)

To launch production-ready PostgreSQL and Redis services:

```bash
cd biu-traffic-ai/deployment
docker compose up -d
```

---

## 📡 REST API Reference

### Authentication
* `POST /api/auth/login/` — Authenticate officer and receive JWT access & refresh tokens.
* `POST /api/auth/token/refresh/` — Obtain a fresh JWT access token via refresh token.
* `GET  /api/auth/protected/` — Retrieve authenticated officer profile, role, and permissions.

### AI Traffic Inference
* `POST /api/scan/image/` — Upload an image for YOLOv8 detection, helmet verification, and law citation.
* `POST /api/scan/video/` — Upload a video for frame-by-frame ByteTrack tracking and violation extraction.
* `GET  /api/traffic/stream/` — Live multipart MJPEG video stream with real-time HUD overlays.
* `GET  /api/traffic/stats/` — Real-time telemetry aggregate (vehicle counts, compliance rate, active checkpoints).
* `GET  /api/violations/` — Paginated history of violation records with auto-cropped evidence URLs.

---

## 🛡️ Security & Authentication

* **Access Control**: All operational pages (`/dashboard`, `/scan`, `/camera`, `/history`, `/violations`) are guarded by client-side navigation guards and server-side JWT authentication.
* **Token Resilience**: Access tokens are configured with a 7-day lifetime to prevent mid-operation disconnects, backed by silent refresh via Axios response interceptors.
* **Data Privacy**: Infraction crops are stored strictly in protected media volumes with structured access URLs.

---

## 👥 Contributors & Acknowledgements

* **BELTEI International University (BIU)** — Faculty of Information Technology & Science.
* Developed for Cambodia Road Safety Law Enforcement and Campus Security Automation.

© 2026 BELTEI International University • Cambodia Traffic Law Enforcement System
