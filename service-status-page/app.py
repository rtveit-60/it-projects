import os
import requests
import feedparser
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template
from requests.auth import HTTPBasicAuth

# Load environment variables from .env
load_dotenv() 

app = Flask(__name__)

# --- JIRA CONFIGURATION ---
LIVE_JIRA = False 
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "your-domain.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = "IT"

# --- FUTURE AWS SECRETS MANAGER PREP ---
# When you deploy to AWS, uncomment these imports and the function below.
# You will also need to add 'boto3' to your requirements.txt.
#
# import boto3
# import json
# from botocore.exceptions import ClientError
#
# def get_aws_secret(secret_name, region_name="us-east-1"):
#     """Fetches a secret from AWS Secrets Manager."""
#     session = boto3.session.Session()
#     client = session.client(service_name='secretsmanager', region_name=region_name)
#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#     except ClientError as e:
#         raise e
#
#     secret = get_secret_value_response['SecretString']
#     return json.loads(secret) # Returns the secret as a Python dictionary

# Import configuration
from data import (ADMIN_LINKS, RAW_TICKETS, ON_CALL_USER, MAINTENANCE_INFO, 
                  ATLASSIAN_TARGETS, GITHUB_WATCHLIST, 
                  INVENTORY_WATCHLIST, 
                  USE_JAMF, JAMF_URL, JAMF_USER, JAMF_PASS, 
                  USE_INTUNE, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)

# Service Order for UI
SERVICE_ORDER = ["GitHub", "Atlassian", "AWS EC2", "AWS S3", "AWS Lambda"]

def get_jira_tickets():
    """Mock for Jira tickets until LIVE_JIRA is True."""
    if not LIVE_JIRA: return RAW_TICKETS
    return RAW_TICKETS

# --- INVENTORY LOGIC (JAMF/INTUNE) ---
def get_jamf_counts():
    counts = {"MacBook Air 15\"": 0, "MacBook M4 Pro 16\"": 0}
    if not USE_JAMF: return counts
    try:
        auth_resp = requests.post(f"{JAMF_URL}/api/v1/auth/token", auth=(JAMF_USER, JAMF_PASS), timeout=2)
        token = auth_resp.json()['token']
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        resp = requests.get(f"{JAMF_URL}/JSSResource/computers", headers=headers, timeout=5)
        computers = resp.json().get('computers', [])
        for c in computers:
            detail_resp = requests.get(f"{JAMF_URL}/JSSResource/computers/id/{c['id']}", headers=headers)
            data = detail_resp.json()['computer']
            user = data['location']['username']
            model = data['hardware']['model']
            if not user: 
                if "Air" in model and "15" in model: counts["MacBook Air 15\""] += 1
                elif "Pro" in model and "16" in model: counts["MacBook M4 Pro 16\""] += 1
    except: print("Jamf API Error")
    return counts

def get_intune_counts():
    counts = {"HP G11 (16GB RAM)": 0, "HP G11 (48GB RAM)": 0}
    if not USE_INTUNE: return counts
    try:
        token_url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
        token_data = {'grant_type': 'client_credentials', 'client_id': AZURE_CLIENT_ID, 'client_secret': AZURE_CLIENT_SECRET, 'scope': 'https://graph.microsoft.com/.default'}
        token_r = requests.post(token_url, data=token_data, timeout=2)
        token = token_r.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        graph_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$filter=userId eq null&$select=model,totalPhysicalMemoryInBytes"
        resp = requests.get(graph_url, headers=headers, timeout=3)
        for d in resp.json().get('value', []):
            model = d.get('model', '').lower()
            ram_gb = int(d.get('totalPhysicalMemoryInBytes', 0) / (1024**3))
            if "g11" in model:
                if ram_gb <= 16: counts["HP G11 (16GB RAM)"] += 1
                elif ram_gb > 32: counts["HP G11 (48GB RAM)"] += 1
    except: print("Intune API Error")
    return counts

def get_inventory():
    processed_inv = []
    
    # 1. Fetch data from MDMs (if toggled on)
    jamf_data = get_jamf_counts()
    intune_data = get_intune_counts()
    
    for item in INVENTORY_WATCHLIST:
        current_count = 0
        name = item.get('name')
        
        # 2. Source Selection Logic
        if USE_JAMF and "MacBook" in name:
            current_count = jamf_data.get(name, 0)
        elif USE_INTUNE and "HP" in name:
            current_count = intune_data.get(name, 0)
        else:
            # FALLBACK: Explicitly pull the 'count' we just set in data.py
            current_count = item.get('count', 0)

        # DEBUG: This will show in your terminal every time the page loads
        print(f"DEBUG: Processing {name} - Count: {current_count}")

        # 3. UI Visual Logic
        if current_count == 0:
            status_class, status_text = "critical", "OUT OF STOCK"
        elif current_count <= item.get('threshold', 5):
            status_class, status_text = "warning", "LOW STOCK"
        else:
            status_class, status_text = "good", "IN STOCK"
            
        processed_inv.append({
            "name": name,
            "count": current_count,
            "class": status_class,
            "text": status_text
        })
        
    return processed_inv

def get_health_data():
    """Pulls health status for GitHub, AWS, and Atlassian."""
    results = []
    
    # GITHUB SCANNER
    try:
        gh_resp = requests.get("https://www.githubstatus.com/api/v2/summary.json", timeout=3)
        gh_data = gh_resp.json()
        gh_status, gh_class, gh_tags = "All Systems Operational", "good", []
        for component in gh_data.get('components', []):
            if component['name'] in GITHUB_WATCHLIST and component['status'] != 'operational':
                gh_tags.append(component['name'])
                if component['status'] == 'major_outage': gh_class, gh_status = 'critical', "Major Outage"
                elif component['status'] == 'partial_outage' and gh_class != 'critical': gh_class, gh_status = 'warning', "Partial Outage"
        results.append({
            "name": "GitHub", "status": gh_status, "class": gh_class,
            "logo": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "url": "https://www.githubstatus.com",
            "feed": [{"time": i['created_at'][11:16], "text": i['name']} for i in gh_data.get('incidents', [])[:3]],
            "tag": gh_tags if gh_tags else "Global"
        })
    except: results.append({"name": "GitHub", "status": "API Error", "class": "critical", "tag": "ERROR"})

    # AWS SCANNER
    aws_map = {"EC2": "ec2-us-east-1", "S3": "s3-us-east-1", "Lambda": "lambda-us-east-1"}
    for name, slug in aws_map.items():
        try:
            feed = feedparser.parse(f"https://status.aws.amazon.com/rss/{slug}.rss")
            is_normal, msgs = True, []
            if feed.entries:
                for entry in feed.entries[:3]:
                    if "resolved" not in entry.title.lower() and "informational" not in entry.title.lower():
                        is_normal = False
                    msgs.append({"time": entry.published[17:22], "text": entry.title})
            results.append({
                "name": f"AWS {name}", "status": "Operational" if is_normal else "Service Issue",
                "class": "good" if is_normal else "warning",
                "logo": "https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg",
                "url": "https://health.aws.amazon.com", "feed": msgs, "tag": "US-EAST-1"
            })
        except: continue

    # ATLASSIAN SCANNER
    atl_status = {"status": "Operational", "class": "good", "tags": [], "feed": []}
    for target in ATLASSIAN_TARGETS:
        try:
            resp = requests.get(target["api"], timeout=3)
            data = resp.json()
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

    results.sort(key=lambda x: SERVICE_ORDER.index(x['name']) if x['name'] in SERVICE_ORDER else 99)
    return results

@app.route('/')
def index():
    return render_template('index.html', 
                           on_call=ON_CALL_USER, 
                           maintenance=MAINTENANCE_INFO,
                           services=get_health_data(),
                           admin_links=ADMIN_LINKS,
                           inventory=get_inventory(),
                           ticket_feed={"tickets": get_jira_tickets()},
                           date=datetime.now().strftime('%A, %b %d %Y'),
                           last_updated=datetime.now().strftime('%H:%M:%S'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)