
---

# Service Health Aggregator

A centralized monitoring tool to aggregate real-time status updates from **AWS (us-east-1)**, **GitHub**, and **Atlassian** into a single, normalized view.

## 🚀 Overview

In a modern enterprise environment, tracking multiple vendor dependencies is a manual chore. This project automates the polling of disparate data sources (JSON APIs and XML RSS feeds) and normalizes the data into a standard `OPERATIONAL`, `DEGRADED`, or `OUTAGE` state.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Libraries:** `requests` (JSON API handling), `feedparser` (RSS/XML parsing)
* **Architecture:** Modular fetcher design for easy scalability.

## 📁 Project Structure

```text
status-dashboard/
├── src/
│   └── main.py         # Main entry point and aggregator logic
├── .gitignore          # Prevents venv and cache from being uploaded
├── requirements.txt    # Project dependencies
└── README.md           # Documentation

```

## ⚙️ Setup & Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/status-dashboard.git
cd status-dashboard

```


2. **Create and activate a virtual environment:**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```



## 🖥️ Usage

To run the aggregator and see the current status of all configured services, execute:

```bash
python src/main.py

```

## 🛰️ Monitored Services

* **GitHub:** Main system status (JSON)
* **Atlassian:** Core product status (JSON)
* **AWS (us-east-1):**
* EC2
* S3
* Lambda



## 🛣️ Roadmap

* [ ] Add Microsoft Azure Public RSS support.
* [ ] Integrate Microsoft Graph API for M365 (Teams/Outlook) health.
* [ ] Build a Flask-based web frontend.
* [ ] Add Slack/Teams notifications for status changes.

## IT Services Health Dashboard: Roadmap to Production

### Phase 1: Stabilization & Hosting (Current Focus)

* **Containerization**: Create a `Dockerfile` to package the app for deployment on corporate clusters (e.g., Kubernetes or Docker Swarm).
* **Production Server**: Migrate from Flask's development server to a production WSGI server like **Waitress** or **Gunicorn**.
* **Data Persistence & Caching**: Implement a server-side cache (using `Flask-Caching`) to store status results for 5 minutes, preventing API rate-limiting issues.
* **SSL Integration**: Deploy behind a corporate reverse proxy (Nginx/F5) to ensure all traffic is encrypted via HTTPS.

### Phase 2: IT Admin & Internal Tooling

* **IT Admin Quick Links**: Add a dedicated sidebar or header section for one-click access to internal tools (e.g., vCenter, Active Directory portal, or Network monitors).
* **Jira Service Management Integration**: Connect to the Jira API to display a "Recent Tickets" feed, allowing staff to see if a global issue has already been logged.
* **Internal Service Probes**: Add health checks for internal corporate apps (e.g., HR Portal, Email Relay) by pinging internal endpoints.

### Phase 3: "Quality of Life" & Culture

* **Quote of the Day**: Implement a random quote generator or a "Company Announcement" ticker to keep the dashboard engaging for daily users.
* **Shift Handover Logs**: Add a small, read-only section pulling from an internal database showing which technician is currently "On-Call".
* **Dark/Light Mode Toggle**: Allow users to switch between the current "NOC" dark theme and a high-contrast light theme.

## 🛠️ Deployment Specs

| Component | Local Development | Corporate Production |
| --- | --- | --- |
| **Server** | `app.run(debug=True)` | Gunicorn / Waitress |
| **Data Fetch** | Real-time on Refresh | 5-Minute Cached Fetch |
| **Security** | HTTP (unsecured) | HTTPS / TLS 1.3 |
| **Logs** | Console Output | Centralized Logging (ELK/Splunk) |

---


