from datetime import datetime, timedelta
from flask import Flask, render_template
import requests
import feedparser

app = Flask(__name__)

# --- CONFIGURATION ---
OPSGENIE_API_KEY = "YOUR_KEY"
OPSGENIE_SCHEDULE_ID = "YOUR_ID"

# CACHE STORAGE
maintenance_cache = {
    "data": None,
    "last_check": datetime.min
}

def get_on_call():
    """Fetches On-Call user. (Currently Mocked)"""
    return {
        "name": "Alex Mercer",
        "email": "amercer@company.com",
        "avatar": "https://i.pravatar.cc/150?u=alex", 
        "status": "On-Shift"
    }

def get_maintenance():
    """
    Checks for scheduled maintenance.
    - Green state: returns None.
    - Amber/Red: returns data with calculated status.
    """
    global maintenance_cache
    now = datetime.now()
    
    # 1. CACHE CHECK (3 Hour expiry)
    if (now - maintenance_cache['last_check']).total_seconds() < 10800:
        if maintenance_cache['data']:
            m = maintenance_cache['data']
            m['status'] = 'active' if m['start'] <= now <= m['end'] else 'scheduled'
        return maintenance_cache['data']

    # 2. MOCK DATA - Toggle 'new_data = None' to test the Green state
    new_data = {
        "title": "Core Firewall Firmware Upgrade",
        "id": "CR-4402",
        "start": now + timedelta(days=2),
        "end": now + timedelta(days=2, hours=4),
        "window_str": "Sat 10:00 PM - 2:00 AM CST"
    } 

    # 3. STATUS CALCULATION
    if new_data:
        new_data['status'] = 'active' if new_data['start'] <= now <= new_data['end'] else 'scheduled'
    
    maintenance_cache['data'] = new_data
    maintenance_cache['last_check'] = now
    return new_data

def get_ticket_status_class(status):
    """Maps Jira status text to CSS color classes."""
    s = status.lower()
    if s in ['waiting for customer', 'pending', 'in progress']:
        return 'status-blue'
    elif s == 'done':
        return 'status-green'
    elif s == 'waiting for support':
        return 'status-yellow'
    return 'status-default'

def get_health_data():
    """Fetches real-time status from GitHub, Atlassian, and AWS RSS."""
    results = []
    logos = {
        "GitHub": "https://github.githubassets.com/favicons/favicon.svg",
        "Atlassian": "https://wac-cdn.atlassian.com/assets/img/favicons/atlassian/favicon.png",
        "AWS EC2": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS S3": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS LAMBDA": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png"
    }

    # 1. JSON APIs
    json_targets = {
        "GitHub": "https://www.githubstatus.com/api/v2/summary.json",
        "Atlassian": "https://status.atlassian.com/api/v2/summary.json"
    }
    for name, url in json_targets.items():
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            indicator = data.get('status', {}).get('indicator', 'none')
            status_class = "good" if indicator == "none" else "critical"
            display_status = "All Services Currently Operational" if indicator == "none" else data.get('status', {}).get('description', 'Status Unknown')
            
            messages = []
            for inc in data.get('incidents', [])[:5]:
                dt = datetime.strptime(inc['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                messages.append({"time": dt.strftime('%H:%M'), "text": inc['name']})

            results.append({"name": name, "region": None, "status": display_status, "class": status_class, "logo": logos.get(name, ""), "feed": messages})
        except Exception:
            results.append({"name": name, "status": "API Error", "class": "critical", "logo": logos.get(name, ""), "feed": []})

    # 2. AWS RSS
    for svc in ["ec2", "s3", "lambda"]:
        name_key = f"AWS {svc.upper()}"
        rss_url = f"https://status.aws.amazon.com/rss/{svc}-us-east-1.rss"
        try:
            feed = feedparser.parse(rss_url)
            messages = []
            for entry in feed.entries[:5]:
                time_str = datetime(*entry.published_parsed[:6]).strftime('%H:%M')
                messages.append({"time": time_str, "text": entry.title})
            is_normal = not feed.entries or "normally" in feed.entries[0].title.lower()
            results.append({"name": name_key, "region": "us-east-1", "status": "All Services Currently Operational" if is_normal else "Service Alert", "class": "good" if is_normal else "warning", "logo": logos.get(name_key, ""), "feed": messages})
        except Exception:
            results.append({"name": name_key, "status": "RSS Error", "class": "critical", "logo": logos.get(name_key, ""), "feed": []})
    return results

@app.route('/')
def index():
    status_list = get_health_data()
    on_call_person = get_on_call()
    maintenance_info = get_maintenance()
    
    admin_links = [
        {"name": "EntraID", "url": "https://entra.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=entra.microsoft.com&sz=64"},
        {"name": "Intune", "url": "https://intune.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=intune.microsoft.com&sz=64"},
        {"name": "365 Admin", "url": "https://admin.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=admin.microsoft.com&sz=64"},
        {"name": "Google Admin", "url": "https://admin.google.com", "icon": "https://www.google.com/s2/favicons?domain=admin.google.com&sz=64"},
        {"name": "vCenter", "url": "https://vcenter.local", "icon": "https://www.google.com/s2/favicons?domain=vmware.com&sz=64"},
        {"name": "CDW", "url": "https://www.cdw.com", "icon": "https://www.google.com/s2/favicons?domain=cdw.com&sz=64"},
        {"name": "Apple Business", "url": "https://business.apple.com", "icon": "https://www.apple.com/favicon.ico"},
    ]
    
    raw_tickets = [
        {"id": "INC-1024", "summary": "Outlook connectivity issues", "description": "Users in Sales reporting intermittent connection errors when sending emails with large attachments.", "status": "In Progress", "assigned_to": "Alex Mercer", "time": "10:42"},
        {"id": "REQ-3391", "summary": "New user onboarding: Sarah Jenkins", "description": "Provision AD account and O365 license for new HR Manager starting Monday.", "status": "Waiting for Customer", "assigned_to": "Jordan Smith", "time": "09:15"},
        {"id": "INC-1023", "summary": "Printer on 3rd floor jamming", "description": "Xerox AltaLink displaying Tray 2 Jam error despite being cleared.", "status": "Waiting for Support", "assigned_to": "Unassigned", "time": "08:55"},
        {"id": "INC-1010", "summary": "Password Reset", "description": "User locked out of ERP portal after several failed login attempts.", "status": "Done", "assigned_to": "Alex Mercer", "time": "08:00"}
    ]

    for t in raw_tickets:
        t['color_class'] = get_ticket_status_class(t['status'])

    ticket_feed = {"status": "Active", "tickets": raw_tickets}
    
    now = datetime.now()
    return render_template('index.html', 
                           services=status_list, 
                           admin_links=admin_links,
                           ticket_feed=ticket_feed,
                           on_call=on_call_person,
                           maintenance=maintenance_info, 
                           last_updated=now.strftime("%H:%M"), 
                           date=now.strftime("%b %d, %Y"))

if __name__ == '__main__':
    app.run(debug=True, port=5000)