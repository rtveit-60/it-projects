import requests
import feedparser
from datetime import datetime
from flask import Flask, render_template
from requests.auth import HTTPBasicAuth

# Import configuration from data.py
# ADDED: GITHUB_WATCHLIST to the imports
from data import ADMIN_LINKS, RAW_TICKETS, ON_CALL_USER, MAINTENANCE_INFO, ATLASSIAN_TARGETS, GITHUB_WATCHLIST

app = Flask(__name__)

# --- JIRA CONFIGURATION ---
LIVE_JIRA = False 
JIRA_DOMAIN = "your-domain.atlassian.net"
JIRA_EMAIL = "your-email@company.com"
JIRA_API_TOKEN = "your-token"
JIRA_PROJECT_KEY = "IT"

SERVICE_ORDER = ["GitHub", "Atlassian", "AWS EC2", "AWS S3", "AWS Lambda"]

def get_jira_tickets():
    if not LIVE_JIRA: return RAW_TICKETS
    return RAW_TICKETS

def get_health_data():
    results = []
    
    # --- 1. GITHUB MULTI-COMPONENT SCANNER ---
    try:
        # We fetch the full summary which includes all components
        gh_resp = requests.get("https://www.githubstatus.com/api/v2/summary.json", timeout=3)
        gh_data = gh_resp.json()
        
        # Default 'Good' State
        gh_status = "All Systems Operational"
        gh_class = "good"
        gh_tags = []
        
        # Scan specifically for components in our Watchlist
        for component in gh_data.get('components', []):
            if component['name'] in GITHUB_WATCHLIST and component['status'] != 'operational':
                gh_tags.append(component['name'])
                
                # Determine Severity
                if component['status'] == 'major_outage':
                    gh_class = 'critical'
                    gh_status = "Major Outage"
                elif component['status'] == 'partial_outage' and gh_class != 'critical':
                    gh_class = 'warning'
                    gh_status = "Partial Outage"
                elif component['status'] == 'degraded_performance' and gh_class != 'critical':
                    gh_class = 'warning'
                    gh_status = "Degraded"

        # Fallback: If a watched component isn't listed but the global flag is red
        if not gh_tags and gh_data.get('status', {}).get('indicator') != 'none':
             gh_status = gh_data.get('status', {}).get('description')
             gh_class = "warning"
             gh_tags = ["Global Issue"]

        results.append({
            "name": "GitHub",
            "status": gh_status,
            "class": gh_class,
            "logo": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "url": "https://www.githubstatus.com",
            "feed": [{"time": i['created_at'][11:16], "text": i['name']} for i in gh_data.get('incidents', [])[:3]],
            "tag": gh_tags if gh_tags else "Global"
        })
    except:
        results.append({"name": "GitHub", "status": "API Error", "class": "critical", "tag": "ERROR"})

    # --- 2. AWS SCANNER (RSS) ---
    aws_map = {"EC2": "ec2-us-east-1", "S3": "s3-us-east-1", "Lambda": "lambda-us-east-1"}
    for name, slug in aws_map.items():
        try:
            feed = feedparser.parse(f"https://status.aws.amazon.com/rss/{slug}.rss")
            is_normal = True
            msgs = []
            if feed.entries:
                for entry in feed.entries[:3]:
                    if "resolved" not in entry.title.lower() and "informational" not in entry.title.lower():
                        is_normal = False
                    msgs.append({"time": entry.published[17:22], "text": entry.title})
            results.append({
                "name": f"AWS {name}",
                "status": "Operational" if is_normal else "Service Issue",
                "class": "good" if is_normal else "warning",
                "logo": "https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg",
                "url": "https://health.aws.amazon.com",
                "feed": msgs, "tag": "US-EAST-1"
            })
        except: continue

    # --- 3. ATLASSIAN MULTI-SCANNER ---
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

    # ENFORCE ORDER
    results.sort(key=lambda x: SERVICE_ORDER.index(x['name']) if x['name'] in SERVICE_ORDER else 99)
    return results

@app.route('/')
def index():
    return render_template('index.html', 
                           on_call=ON_CALL_USER, 
                           maintenance=MAINTENANCE_INFO,
                           services=get_health_data(),
                           admin_links=ADMIN_LINKS,
                           ticket_feed={"tickets": get_jira_tickets()},
                           date=datetime.now().strftime('%A, %b %d %Y'),
                           last_updated=datetime.now().strftime('%H:%M:%S'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)