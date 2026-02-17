import os
import requests
import feedparser
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template
from requests.auth import HTTPBasicAuth

# --- INITIALIZATION ---
load_dotenv()  # Injects variables from .env into the environment
app = Flask(__name__)

# ==========================================
# SECRETS MANAGEMENT (FUTURE PROOFING)
# ==========================================
# This block is staged for AWS deployment. 
# To use: Remove triple quotes, install 'boto3', and configure IAM.
"""
import boto3
import json
from botocore.exceptions import ClientError

def get_aws_secret(secret_name, region_name="us-east-1"):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    return json.loads(get_secret_value_response['SecretString'])
"""

# ==========================================
# DATA IMPORTS & CONFIGURATION
# ==========================================
from data import (
    ADMIN_LINKS, RAW_TICKETS, ON_CALL_USER, MAINTENANCE_INFO, 
    ATLASSIAN_TARGETS, GITHUB_WATCHLIST, INVENTORY_WATCHLIST, 
    MS_RSS_TARGETS, 
    USE_JAMF, JAMF_URL, JAMF_USER, JAMF_PASS, 
    USE_INTUNE, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
)

# SERVICE_ORDER: Governs the vertical hierarchy of tiles in the grid.
# Grouped by provider: GitHub/Atlassian -> AWS -> Microsoft.
SERVICE_ORDER = [
    "GitHub", "Atlassian", 
    "AWS EC2", "AWS S3", "AWS Lambda", 
    "Microsoft 365", "Microsoft Teams", "Azure Status"
]

# Toggle for Live Tickets (Requires valid Jira API token in .env)
LIVE_JIRA = False 

# ==========================================
# SECTION 1: HARDWARE & TICKETS
# ==========================================

def get_jira_tickets():
    """Handles logic for live Jira tickets vs mock display."""
    # Note: When LIVE_JIRA is True, this function should be updated 
    # with the requests logic for JIRA_DOMAIN and JIRA_API_TOKEN.
    return RAW_TICKETS

def get_jamf_counts():
    """
    Retrieves unassigned Mac counts via Jamf Pro.
    Uses Advanced Search ID 5 to fetch all model data in a single request.
    """
    counts = {"MacBook Air 15\"": 0, "MacBook M4 Pro 16\"": 0}
    if not USE_JAMF: return counts
    
    try:
        # Step 1: Request Bearer Token for Auth (Standard Jamf Pro API flow)
        auth_resp = requests.post(f"{JAMF_URL}/api/v1/auth/token", auth=(JAMF_USER, JAMF_PASS), timeout=3)
        token = auth_resp.json()['token']
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        
        # Step 2: Query Search ID 5 (Configured for 'Unassigned Macs')
        # This is significantly faster than querying individual computer IDs.
        url = f"{JAMF_URL}/JSSResource/advancedcomputersearches/id/5"
        resp = requests.get(url, headers=headers, timeout=5)
        computers = resp.json().get('advanced_computer_search', {}).get('computers', [])
        
        # Step 3: Increment counts based on model strings
        for c in computers:
            model = c.get('Model', '')
            if "Air" in model and "15" in model: counts["MacBook Air 15\""] += 1
            elif "Pro" in model and "16" in model: counts["MacBook M4 Pro 16\""] += 1
    except Exception as e:
        print(f"Jamf Error: {e}")
    return counts

def get_intune_counts():
    """
    Retrieves unassigned PC counts via MS Graph (Intune).
    Includes RAM Binning to differentiate 16GB vs 48GB hardware models.
    """
    counts = {"HP G11 (16GB RAM)": 0, "HP G11 (48GB RAM)": 0}
    if not USE_INTUNE: return counts
    
    try:
        # Step 1: Get Token from Microsoft Identity Platform (Azure AD)
        token_data = {
            'grant_type': 'client_credentials', 
            'client_id': AZURE_CLIENT_ID, 
            'client_secret': AZURE_CLIENT_SECRET, 
            'scope': 'https://graph.microsoft.com/.default'
        }
        token_resp = requests.post(f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token", data=token_data, timeout=3)
        token = token_resp.json().get("access_token")
        
        # Step 2: Query Managed Devices (userId eq null = unassigned)
        headers = {'Authorization': f'Bearer {token}'}
        endpoint = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$filter=userId eq null&$select=model,totalPhysicalMemoryInBytes"
        resp = requests.get(endpoint, headers=headers, timeout=5)
        
        # Step 3: RAM Binning (Handling byte-to-GB variance)
        for d in resp.json().get('value', []):
            model = d.get('model', '').lower()
            ram_gb = round(int(d.get('totalPhysicalMemoryInBytes', 0)) / (1024**3), 1)
            if "g11" in model:
                if 14.0 <= ram_gb <= 18.0: counts["HP G11 (16GB RAM)"] += 1
                elif 44.0 <= ram_gb <= 52.0: counts["HP G11 (48GB RAM)"] += 1
    except Exception as e:
        print(f"Intune Error: {e}")
    return counts

def get_inventory():
    """Collates API and Mock data for the Inventory grid UI."""
    processed_inv = []
    jamf_data = get_jamf_counts()
    intune_data = get_intune_counts()
    
    for item in INVENTORY_WATCHLIST:
        name = item.get('name')
        
        # Logic: If automation is ON, use API data. If OFF, use count from data.py.
        if USE_JAMF and "MacBook" in name:
            count = jamf_data.get(name, 0)
        elif USE_INTUNE and "HP" in name:
            count = intune_data.get(name, 0)
        else:
            count = item.get('count', 0) 

        # Visual status logic (Determines tile color and text)
        if count == 0:
            status_cls, status_txt = "critical", "OUT OF STOCK"
        elif count <= item.get('threshold', 5):
            status_cls, status_txt = "warning", "LOW STOCK"
        else:
            status_cls, status_txt = "good", "IN STOCK"
            
        processed_inv.append({
            "name": name, "count": count, "class": status_cls, "text": status_txt
        })
    return processed_inv

# ==========================================
# SECTION 2: HEALTH SCANNERS (RSS & API)
# ==========================================

def get_ms_health():
    """
    Parses Microsoft RSS feeds for Office 365, Teams, and Azure.
    Maps generic RSS updates to 'All Systems Operational' or escalating alert levels.
    """
    results = []
    for t in MS_RSS_TARGETS:
        try:
            feed = feedparser.parse(t['url'])
            status_text = "All Systems Operational"
            status_class = "good"
            msgs = []

            if feed.entries:
                for entry in feed.entries[:2]:
                    title = entry.title.lower()
                    
                    # Logic: Determine severity based on RSS title keywords
                    if "resolved" not in title:
                        if any(k in title for k in ["outage", "interruption", "major", "critical"]):
                            status_text, status_class = "Major Outage", "critical"
                        elif any(k in title for k in ["degradation", "issue", "investigating", "incident"]):
                            if status_class != "critical": # Don't downgrade critical if already set
                                status_text, status_class = "Service Degradation", "warning"
                        
                    msgs.append({
                        "time": entry.published[17:22] if 'published' in entry else "--:--", 
                        "text": entry.title
                    })
            
            results.append({
                "name": t['name'], "status": status_text, "class": status_class, 
                "logo": t['logo'], "url": "https://status.office.com", 
                "feed": msgs, "tag": "Global"
            })
        except: continue
    return results

def get_health_data():
    """Master function to aggregate all service statuses into the dashboard."""
    results = []
    
    # --- GITHUB (JSON API) ---
    try:
        gh_data = requests.get("https://www.githubstatus.com/api/v2/summary.json", timeout=3).json()
        status, css, tags = "All Systems Operational", "good", []
        for comp in gh_data.get('components', []):
            if comp['name'] in GITHUB_WATCHLIST and comp['status'] != 'operational':
                tags.append(comp['name'])
                if comp['status'] == 'major_outage': css, status = 'critical', "Major Outage"
                elif comp['status'] == 'partial_outage' and css != 'critical': css, status = 'warning', "Partial Outage"
        results.append({
            "name": "GitHub", "status": status, "class": css, 
            "logo": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", 
            "url": "https://www.githubstatus.com", "tag": tags if tags else "Global",
            "feed": [{"time": i['created_at'][11:16], "text": i['name']} for i in gh_data.get('incidents', [])[:3]]
        })
    except: pass

    # --- AWS (RSS Feeds) ---
    aws_map = {"EC2": "ec2-us-east-1", "S3": "s3-us-east-1", "Lambda": "lambda-us-east-1"}
    for name, slug in aws_map.items():
        try:
            feed = feedparser.parse(f"https://status.aws.amazon.com/rss/{slug}.rss")
            st_txt, st_cls, msgs = "Operational", "good", []
            if feed.entries:
                for entry in feed.entries[:3]:
                    if "resolved" not in entry.title.lower() and "informational" not in entry.title.lower():
                        st_cls, st_txt = "warning", "Service Issue"
                    msgs.append({"time": entry.published[17:22], "text": entry.title})
            results.append({
                "name": f"AWS {name}", "status": st_txt, "class": st_cls, 
                "logo": "https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg", 
                "url": "https://health.aws.amazon.com", "feed": msgs, "tag": "US-EAST-1"
            })
        except: continue

    # --- ATLASSIAN (Statuspage APIs) ---
    atl_status = {"status": "Operational", "class": "good", "tags": [], "feed": []}
    for target in ATLASSIAN_TARGETS:
        try:
            data = requests.get(target["api"], timeout=3).json()
            if data.get('incidents'):
                inc = data['incidents'][0]
                atl_status["status"] = "Active Incident"
                atl_status["class"] = "critical" if inc['impact'] in ['major', 'critical'] else "warning"
                atl_status["tags"].append(target["name"].upper())
                atl_status["feed"].append({"time": datetime.now().strftime('%H:%M'), "text": f"[{target['name'].upper()}] {inc['name']}"})
        except: continue
    
    results.append({
        "name": "Atlassian", "status": atl_status["status"], "class": atl_status["class"], 
        "logo": "https://cdn.worldvectorlogo.com/logos/atlassian.svg", "url": "https://status.atlassian.com", 
        "feed": atl_status["feed"], "tag": atl_status["tags"]
    })

    # --- MICROSOFT (RSS Feeds) ---
    results.extend(get_ms_health())

    # --- FINAL SORTING BY SERVICE_ORDER ---
    results.sort(key=lambda x: SERVICE_ORDER.index(x['name']) if x['name'] in SERVICE_ORDER else 99)
    return results

# ==========================================
# SECTION 3: ROUTES
# ==========================================

@app.route('/')
def index():
    """Constructs the dashboard payload and renders the template."""
    return render_template(
        'index.html', 
        on_call=ON_CALL_USER, 
        maintenance=MAINTENANCE_INFO,
        services=get_health_data(),
        admin_links=ADMIN_LINKS,
        inventory=get_inventory(),
        ticket_feed={"tickets": get_jira_tickets()},
        date=datetime.now().strftime('%A, %b %d %Y'),
        last_updated=datetime.now().strftime('%H:%M:%S')
    )

if __name__ == '__main__':
    # Runs the local development server
    app.run(debug=True, port=5000)