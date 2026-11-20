---
language:
- km
- en
license: mit
tags:
- yolo
- yolov8
- object-detection
- traffic-enforcement
- smart-city
- cambodia
- beltei-international-university
metrics:
- map50
model-index:
- name: cambodia-traffic-yolov8
  results:
  - task:
      type: object-detection
      name: Traffic Safety & Helmet Law Enforcement
    dataset:
      name: Cambodian Road & Helmet Dataset (Phnom Penh)
      type: custom
    metrics:
    - type: map50
      value: 0.995
      name: mAP@0.5 (No-Helmet Detection)
---

# 🚦 BIU Cambodia Traffic Law Enforcement Model (YOLOv8)

**Developer:** Leng Saroth (`it-roth`)  
**Project Advisor:** Dr. Chen Sovann  
**Academic Institution:** [BELTEI International University](https://www.beltei.edu.kh), Phnom Penh, Cambodia  
**Task:** Real-time Traffic Surveillance & Cambodian Sub-Decree No. 39 Enforcement  

---

## 📌 Model Overview

This model is a custom fine-tuned **YOLOv8 Nano** architecture specialized for high-density Cambodian urban traffic flow (Phnom Penh). It detects vehicle categories and verifies motorcycle safety compliance pursuant to **Royal Government of Cambodia Sub-Decree No. 39 on Road Traffic Fines**:
* **Article 8:** Mandatory helmet usage for all motorcycle drivers and passengers (**Fine: 60,000 KHR**).
* **Article 44:** Prohibition of motorcycle passenger overloading (>2 adults) (**Fine: 100,000 KHR**).

### 🎯 Key Performance Metrics
* **Rider Without Helmet (`rider_no_helmet`) mAP@50:** **0.995 (99.5%)**
* **Model Size:** 6.23 MB (`best.pt`)
* **Inference Speed:** ~24 ms on CPU / ~4 ms on GPU

---

## 🛠️ Quick Start (Python & Ultralytics)

```bash
pip install ultralytics
```

```python
from ultralytics import YOLO

# Load the weights
model = YOLO('best.pt')

# Run inference on traffic photo or video
results = model.predict(source='traffic_scene.jpg', conf=0.35)

# Show detection results with bounding boxes
results[0].show()
```

---

## 📊 Classes & Detection Targets
1. `rider_with_helmet` — Compliant motorcyclist
2. `rider_no_helmet` — Infraction flagged for police citation
3. `motorcycle` — Two-wheeled vehicles
4. `auto_rickshaw` — PassApp / Bajaj 3-wheelers
5. `remorque` — Traditional Khmer motorbike-trailer tuk-tuk
6. `car` — Passenger cars & SUVs
7. `truck` — Heavy logistics & delivery trucks
8. `bus` — Public transit buses

---

## 📜 Citation & Credits
* Developed as part of the **BIU Traffic AI** Bachelor's Senior Capstone Project at BELTEI International University.
* Lead CV Engineer: **Leng Saroth** (`ID: 00057189`)
* Academic Advisor: **Dr. Chen Sovann**
