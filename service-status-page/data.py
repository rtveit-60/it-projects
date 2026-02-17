import os

# ==========================================
# 1. SECRETS & CREDENTIALS (ENV VARIABLES)
# ==========================================
# JAMF (Apple)
JAMF_URL = "https://your-instance.jamfcloud.com"
JAMF_USER = os.getenv("JAMF_USER")
JAMF_PASS = os.getenv("JAMF_PASS")

# INTUNE (Windows)
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "your-tenant-id")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "your-client-id")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

# JIRA / ATLASSIAN
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "your-domain.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# AUTOMATION TOGGLES
USE_JAMF = True if (JAMF_USER and JAMF_PASS) else False
USE_INTUNE = True if AZURE_CLIENT_SECRET else False


# ==========================================
# 2. ADMINISTRATOR TOOLBOX LINKS
# ==========================================
ADMIN_LINKS = [
    {"name": "EntraID", "url": "https://entra.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=entra.microsoft.com&sz=64"},
    {"name": "Intune", "url": "https://intune.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=intune.microsoft.com&sz=64"},
    {"name": "365 Admin", "url": "https://admin.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=admin.microsoft.com&sz=64"},
    {"name": "MyApps", "url": "https://myapps.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=myapps.microsoft.com&sz=64"},
    {"name": "Google Admin", "url": "https://admin.google.com", "icon": "https://www.google.com/s2/favicons?domain=admin.google.com&sz=64"},
    {"name": "vCenter", "url": "https://vcenter.local", "icon": "https://www.google.com/s2/favicons?domain=vmware.com&sz=64"},
    {"name": "CDW", "url": "https://www.cdw.com", "icon": "https://www.google.com/s2/favicons?domain=cdw.com&sz=64"},
    {"name": "Apple Business Manager", "url": "https://business.apple.com", "icon": "https://www.google.com/s2/favicons?domain=apple.com&sz=64"}
]


# ==========================================
# 3. MOCK DATA & WATCHLISTS
# ==========================================

# --- HARDWARE INVENTORY WATCHLIST ---
# MOCK DATA APPLIED: 2 > 10, 1 at 4, 1 at 0
INVENTORY_WATCHLIST = [
    {"name": "HP G11 (16GB RAM)", "count": 12, "threshold": 5, "category": "Workstations"},
    {"name": "HP G11 (48GB RAM)", "count": 15, "threshold": 5, "category": "Workstations"},
    {"name": "MacBook Air 15\"", "count": 4, "threshold": 5, "category": "Laptops"},
    {"name": "MacBook M4 Pro 16\"", "count": 0, "threshold": 2, "category": "Laptops"}
]

# --- GITHUB COMPONENT WATCHLIST ---
GITHUB_WATCHLIST = [
    "Git Operations", "API Requests", "Actions", "Pull Requests", "Issues", "Copilot", "Pages"
]

# --- ATLASSIAN API TARGETS ---
ATLASSIAN_TARGETS = [
    {"name": "Jira Software", "api": "https://jira-software.status.atlassian.com/api/v2/summary.json"},
    {"name": "Jira Service Management", "api": "https://jsm.status.atlassian.com/api/v2/summary.json"},
    {"name": "Jira Work Management", "api": "https://jwm.status.atlassian.com/api/v2/summary.json"},
    {"name": "Confluence", "api": "https://confluence.status.atlassian.com/api/v2/summary.json"},
    {"name": "Atlassian Rovo", "api": "https://rovo.status.atlassian.com/api/v2/summary.json"}
]

# --- ON-CALL USER ---
ON_CALL_USER = {
    "name": "Alex Mercer",
    "email": "amercer@company.com",
    "avatar": "https://i.pravatar.cc/150?u=alex", 
    "status": "On-Shift",
    "hours": "6PM-8PM Mon-Fri / 9AM-1PM Sat"
}

# --- MAINTENANCE INFO ---
MAINTENANCE_INFO = {
    "title": "Core Firewall Firmware Upgrade",
    "id": "CR-4402",
    "window_str": "Sat 10:00 PM - 2:00 AM CST",
    "status": "scheduled" 
}

# --- JIRA TICKET FEED (8 Tickets) ---
RAW_TICKETS = [
    {"id": "INC-1002", "summary": "VPN Certificate Expired", "description": "GlobalProtect connectivity issue.", "status": "In Progress", "assigned_to": "Jordan Smith", "time": "14:22"},
    {"id": "REQ-3380", "summary": "New Hire Onboarding - Marketing", "description": "Hardware and account setup.", "status": "Pending", "assigned_to": "Alex Mercer", "time": "12:05"},
    {"id": "INC-1005", "summary": "Keyboard Malfunction", "description": "Stuck keys on front desk unit.", "status": "Done", "assigned_to": "Unassigned", "time": "Feb 14"},
    {"id": "INC-0998", "summary": "Guest Wifi Access", "description": "Temporary credentials for auditor.", "status": "Resolved", "assigned_to": "Jordan Smith", "time": "Feb 14"},
    {"id": "INC-1010", "summary": "Outlook Search Indexed Corrupt", "description": "Rebuilding local .ost index.", "status": "In Progress", "assigned_to": "Alex Mercer", "time": "09:15"},
    {"id": "REQ-3392", "summary": "License Upgrade: Adobe CC", "description": "Requesting 2 new seats.", "status": "Waiting for Support", "assigned_to": "Unassigned", "time": "08:45"},
    {"id": "INC-1012", "summary": "Conf Room B AV Offline", "description": "HDMI switcher power cycle.", "status": "Pending", "assigned_to": "Jordan Smith", "time": "08:10"},
    {"id": "INC-1014", "summary": "MFA Loop on EntraID", "description": "Verification loop after reset.", "status": "Waiting for Support", "assigned_to": "Unassigned", "time": "07:30"}
]

# --- MICROSOFT RSS TARGETS ---
MS_RSS_TARGETS = [
    {"name": "Microsoft 365", "url": "https://status.office.com/en-us/rss", "logo": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg"},
    {"name": "Microsoft Teams", "url": "https://status.office.com/en-us/rss", "logo": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Microsoft_Office_Teams_%282018%E2%80%93present%29.svg"},
    {"name": "Azure Status", "url": "https://azurestatus.microsoft.com/en-us/status/feed/", "logo": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Microsoft_Azure_Logo.svg"}
]