
# 🛠️ IT Service Status Dashboard

A real-time, lightweight internal dashboard for IT Teams to monitor service health, hardware inventory, and active support tickets. Built with Python (Flask) and integrates with Jamf Pro, Microsoft Intune, and Jira.

## 🚀 Features
* **Service Health:** Live monitoring of GitHub, AWS (EC2, S3, Lambda), and Atlassian services via RSS and Status APIs.
* **Inventory Watchlist:** Real-time stock counts for critical hardware (Mac/PC) pulled directly from MDM platforms.
* **Ticket Feed:** A unified sidebar showing the latest 8 IT support incidents and requests.
* **Admin Toolbox:** Quick-access links to critical administrative portals (EntraID, Intune, Apple Business, etc.).
* **On-Call & Maintenance:** Clear visibility into who is currently on-shift and upcoming scheduled maintenance windows.

---

## 🛠️ Tech Stack
* **Backend:** Python 3.10+ / Flask
* **APIs:** Jamf Pro (Classic & Pro API), Microsoft Graph (Intune), Atlassian Status API
* **Frontend:** HTML5, CSS3 (Modern Responsive Grid)

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/service-status-dashboard.git](https://github.com/your-username/service-status-dashboard.git)
cd service-status-dashboard

2. Install Dependencies
Bash
pip install -r requirements.txt

3. Environment Configuration
Copy the template and fill in your specific credentials.

Bash
cp .env.example .env

Edit .env to include your:

Jamf API Credentials

Azure/Intune App Registration Details (Client ID, Secret, Tenant ID)

Atlassian API Token & Domain

4. Running Locally
Bash
python app.py

The dashboard will be available at http://127.0.0.1:5000.

🔒 Security Model
Secret Isolation: All passwords and API keys are stored in a local .env file and ignored by Git via .gitignore.

Principle of Least Privilege: API accounts should be configured as Read-Only users.

Cloud Ready: app.py includes a staged framework for AWS Secrets Manager, allowing for a seamless transition from .env files to encrypted cloud vaults for production deployment.

📋 MDM Configuration Requirements
Jamf Pro
To use live inventory, create an Advanced Computer Search in Jamf:

Name: Dashboard-Inventory

Criteria: Username | is | blank

Display: Include Model in the output columns.

ID: Ensure the search_id in app.py matches the ID of this search (default is 5).

Microsoft Intune
Register an application in the Azure Portal with the following permission:

DeviceManagementManagedDevices.Read.All (Application Permission)

👤 Author
Matt - Initial Work & Architecture



## 🎨 UI & Styling Guide

To maintain the visual integrity of the dashboard, follow these formatting rules when updating `data.py` or `app.py`.

### 1. Status Colors (CSS Classes)
The dashboard uses three primary status classes to drive the color-coded UI. Use these keys in your logic:

| Class | Color | Usage |
| :--- | :--- | :--- |
| `good` | Green | Systems operational, high stock levels. |
| `warning` | Amber | Partial outages, low stock (below threshold). |
| `critical` | Red | Major outages, zero stock, high-priority incidents. |

### 2. Inventory Logic
When adding a new hardware item to `INVENTORY_WATCHLIST` in `data.py`, ensure the following dictionary structure:
```python
{
    "name": "Model Name",
    "count": 0,          # Current mock stock
    "threshold": 5,      # Level at which color shifts to 'warning'
    "category": "Type"   # e.g., 'Laptops' or 'Workstations'
}
3. Ticket Status Mapping
The sidebar UI styles tickets based on the status string. To ensure badges render correctly, use these exact strings:

Green Badge: Resolved, Done

Blue Badge: In Progress

Gray Badge: Pending, Waiting for Support

4. Admin Icons
Admin links use Google Favicon Services for high-resolution icons. To add a new link, follow this URL format:
https://www.google.com/s2/favicons?domain=YOURDOMAIN.com&sz=64


---


