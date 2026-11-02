# SkillExchange - Peer-to-Peer Skill Sharing & Task Booking Platform

**Thiagarajar College of Engineering**  
*Department of Information Technology*  
*Course: Web Technology (22IT550)*

**Developed by:**
* Pravin K S (2403917720521061)
* Vinothkumar G (2403917720521090)
* Vignesh E (2403917720521087)

---

## Overview
**SkillExchange** is a full-stack peer-to-peer web platform where users can learn skills through 1-on-1 tutoring sessions or hire skilled peers to complete tasks directly. Every user can both offer skills and request appointments, creating a collaborative, commission-free learning environment.

---

## Technology Stack
* **Frontend**: AngularJS 1.8.2 Single-Page Application (SPA) with CSS3, Bootstrap Icons, responsive design
* **Backend**: Django 6.1.2 with REST JSON endpoints
* **Security**: `bcrypt` salted password hashing, server-side self-booking prevention
* **Database**: MongoDB Community Server (`skillswap_db`) via `PyMongo` 4.19
* **Inspection**: MongoDB Compass

---

## Getting Started

### 1. Prerequisites
* Python 3.10+
* MongoDB running locally on port `27017`

### 2. Install Dependencies
```bash
pip install django pymongo bcrypt
```

### 3. Initialize Demo Data
Populate users, skill listings, and initial appointments matching the presentation screenshots:
```bash
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillexchange.settings'); django.setup(); from core.seed_data import seed_database; print(seed_database())"
```
*(Or simply open `http://127.0.0.1:8000/api/seed/` in your browser)*

### 4. Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Then navigate to **`http://127.0.0.1:8000/`** in your browser.

---

## 🔑 Demo Accounts

| Name | Role | Email | Password |
|---|---|---|---|
| **Alex Rivera** | UI Designer / Sound Provider | `alex@example.com` | `demo123` |
| **pravin** | Python / Backend Provider | `pravin@gmail.com` | `pravin123` |
| **vignesh** | Guitar / Frontend Provider | `vignesh@gmail.com` | `vignesh123` |
| **Sarah Chen** | Senior Product Designer | `sarah@example.com` | `demo123` |
| **Marcus Vance** | Audio Engineer & Producer | `marcus@example.com` | `demo123` |

---

## Project Structure
```text
Code/
├── manage.py                     # Django management script
├── skillexchange/
│   ├── settings.py               # Django configuration & MongoDB settings
│   ├── urls.py                   # Root URL dispatcher
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── views.py                  # REST API views & SPA render view
│   ├── urls.py                   # API routes
│   ├── db.py                     # MongoDB PyMongo connection & serializers
│   └── seed_data.py              # Sample users, skills, and appointments
├── templates/
│   └── index.html                # Single-Page Application template (AngularJS + Django verbatim)
├── static/
│   ├── css/
│   │   └── style.css             # Platform styling matching design screenshots
│   └── js/
│       ├── angular.min.js        # Offline-ready AngularJS 1.8.2 bundle
│       └── app.js                # AngularJS application controller & API calls
└── run_test_plan.py              # Automated test suite for T1-T8
```

---

## Verification & Test Suite
To execute the automated verification test suite (T1 - T8):
```bash
python run_test_plan.py
```
Expected output:
* `T1`: Registration with bcrypt password hashing
* `T2`: Valid & invalid login authentication
* `T3`: Category filtering and keyword search
* `T4`: Publishing a new skill listing
* `T5`: Booking an appointment session (Status: Pending)
* `T6`: Self-booking protection (HTTP 400 rejection)
* `T7`: Provider acceptance of appointment (Status: Confirmed)
* `T8`: Session completion (Status: Completed)
