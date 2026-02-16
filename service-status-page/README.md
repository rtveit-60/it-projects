
---

# IT Services & Health Dashboard

A high-performance, hardware-inspired monitoring dashboard built with **Python (Flask)** and **Tailwind CSS**. This tool aggregates real-time status updates from **AWS**, **GitHub**, **Atlassian**, and internal **Jira** ticket streams into a normalized, "NOC-style" interface.

## 🚀 Overview

In a modern enterprise environment, tracking multiple vendor dependencies is a manual chore. This project automates the polling of disparate data sources (JSON APIs and XML RSS feeds) and normalizes the data into a standard 3D glass interface designed for "Always-On" monitoring.

## 🧱 Component Architecture & Style Guide

### 🎨 Design Philosophy

The dashboard is designed to look like a premium physical monitoring interface:

* **3D Glassmorphism:** Semi-transparent "floating" cards with backdrop blurring (`backdrop-filter: blur(12px)`).
* **Dynamic Accents:** Symmetrical 4px left-side color bars indicating system health.
* **High-Contrast Logic:** Bold italic typography paired with monospace "log-style" timestamps.
* **Deep Recess Sidebar:** An inset-shadow "well" for the ticket stream to create a sense of mechanical depth.

### 1. Symmetrical Header

* **Title:** `IT SERVICES & HEALTH DASHBOARD`.
* **Accents:** Dual symmetrical cards for **On-Call Duty** (Blue) and **Maintenance Window** (Dynamic: Green/Yellow/Red).
* **Status:** Left-side 4px border accents match the card's current urgency level.

### 2. Admin Toolbox

* **Layout:** A strict **4x2 grid** of 8 primary administrator tools (EntraID, Intune, etc.).
* **Styling:** Floating glass card with a solid **Blue** left-side accent.
* **Icons:** Full-color high-resolution brand favicons.

### 3. Service Stack (Vendor Tiles)

* **Layout:** Arranged in a vertical column for maximum readability and downward expansion.
* **Status Accents:** - **Green (`#10b981`):** Operational / Nominal.
* **Yellow (`#f59e0b`):** Degraded / Performance issues.
* **Flashing Red (`#ef4444`):** Active Service Outage / Critical Incident.


* **Timeline Logs:** Expandable "log-style" message boxes tucked below each vendor using a **Timeline Column** (Time + Bullet | Justified Text Body).
* **Fade-to-Black:** Collapsed logs feature a linear gradient fade at the bottom to maintain UI cleanliness.
* **Multi-Service Alert:** Red pulsing badge indicating the count of affected services (e.g., "3 Services Affected") for grouped vendors like Atlassian.

### 4. Ticket Sidebar

* **Inner Recess:** A darker, inset-shadow container (`sidebar-inner`) that separates tickets from the main UI background.
* **Ticket Status Logic:**
* **Blue:** In-Progress, Pending, Waiting for Customer.
* **Yellow:** Waiting for Support.
* **Green:** Done, Resolved.



## 🛠️ Tech Stack & Structure

| File | Role | Description |
| --- | --- | --- |
| `app.py` | **The Engine** | Flask server; handles API scraping (JSON/RSS) and data normalization. |
| `data.py` | **The Brain** | Stores Admin Links, Mock/Static Ticket data, and On-Call settings. |
| `index.html` | **The Face** | Jinja2 template using Tailwind CSS and the "3D Glass" custom styles. |
| `requirements.txt` | **The Toolbox** | Python dependencies (Flask, Requests, Feedparser). |

Data Separation Rule: > - Static metadata (On-Call names, coverage hours, Admin URLs) MUST reside in data.py.

index.html should only contain the logic for rendering these variables, never the raw text values.

## ⚙️ Setup & Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/status-dashboard.git
cd status-dashboard

```


2. **Create a virtual environment & Install:**
```bash
python -m venv venv
source venv/bin/activate  # (.\venv\Scripts\activate on Windows)
pip install -r requirements.txt

```


3. **Run the Dashboard:**
```bash
python app.py

```



## 🛣️ Roadmap

* [x] **Phase 1: Stabilization**: Move to symmetrical header accents and 4x2 Admin Grid.
* [x] **Phase 2: UI/UX**: Implement Timeline-style log messages with fade-to-black.
* [x] **Phase 3: Logic**: Multi-target Atlassian scanning with service counting.
* [ ] **Phase 4: Notifications**: Add Slack/Teams webhooks for status transitions.
* [ ] **Phase 5: Production**: Containerize via `Dockerfile` and deploy behind Nginx.

---

### **AI Interaction Rule (System Prompt)**

*When updating this project, the AI must strictly adhere to the established "3D Glassmorphism" aesthetic. Do not suggest migrations to React or modern JS frameworks. Maintain the single-column vertical service stack and the 4x2 Admin grid. Left-side accents must remain the primary status indicators.*

---

**Would you like me to generate a `Dockerfile` to match the roadmap in this README?**