
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

---


