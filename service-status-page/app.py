from datetime import datetime, timedelta
from flask import Flask, render_template
import requests
import feedparser

# Import the data from our new file
from data import ADMIN_LINKS, RAW_TICKETS, ON_CALL_USER, MAINTENANCE_INFO, ATLASSIAN_TARGETS

app = Flask(__name__)

# --- CONFIGURATION ---
# (Placeholders for future Phase 2 integration)
OPSGENIE_API_KEY = "YOUR_KEY"
OPSGENIE_SCHEDULE_ID = "YOUR_ID"

# CACHE STORAGE
maintenance_cache = {
    "data": None,
    "last_check": datetime.min
}

def get_on_call():
    """Returns the static on-call user from data.py"""
    return ON_CALL_USER

def get_maintenance():
    """
    Checks for maintenance and determines status.
    Uses basic config from data.py but calculates dynamic dates here.
    """
    global maintenance_cache
    now = datetime.now()
    
    # 1. CACHE CHECK (3 Hour expiry)
    if (now - maintenance_cache['last_check']).total_seconds() < 10800:
        if maintenance_cache['data']:
            m = maintenance_cache['data']
            # Re-evaluate status based on current time vs cached window
            m['status'] = 'active' if m['start'] <= now <= m['end'] else 'scheduled'
        return maintenance_cache['data']

    # 2. CONSTRUCT MAINTENANCE OBJECT
    # We grab the static strings from data.py and add dynamic timestamps
    new_data = MAINTENANCE_INFO.copy()
    
    # TOGGLE LOGIC:
    # To test "Green" state (No maintenance), set new_data to None
    # new_data = None 

    if new_data:
        # Dynamic Time Calculation:
        # Currently set to start in 2 days. 
        # To test "Active" (Red Flashing), change to: now - timedelta(minutes=10)
        new_data['start'] = now + timedelta(days=2)
        new_data['end'] = now + timedelta(days=2, hours=4)
        
        # Determine Status
        if new_data['start'] <= now <= new_data['end']:
            new_data['status'] = 'active'
        else:
            new_data['status'] = 'scheduled'
    
    # Update Cache
    maintenance_cache['data'] = new_data
    maintenance_cache['last_check'] = now
    
    return new_data

def get_ticket_status_class(status):
    s = status.lower()
    if s in ['waiting for customer', 'pending', 'in progress']:
        return 'status-blue'
    elif s in ['done', 'resolved']:
        return 'status-green'    
    elif s == 'waiting for support':
        return 'status-yellow'
    return 'status-default'

def get_health_data():
    results = []
    
    # 1. Configuration Maps
    logos = {
        "GitHub": "https://github.githubassets.com/favicons/favicon.svg",
        "Atlassian": "https://wac-cdn.atlassian.com/assets/img/favicons/atlassian/favicon.png",
        "AWS EC2": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS S3": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS LAMBDA": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png"
    }
    
    public_urls = {
        "GitHub": "https://www.githubstatus.com",
        "Atlassian": "https://status.atlassian.com",
        "AWS EC2": "https://status.aws.amazon.com",
        "AWS S3": "https://status.aws.amazon.com",
        "AWS LAMBDA": "https://status.aws.amazon.com"
    }

    # ---------------------------------------------------------
    # 1. GITHUB CHECK
    # ---------------------------------------------------------
    try:
        gh_resp = requests.get("https://www.githubstatus.com/api/v2/summary.json", timeout=5)
        gh_data = gh_resp.json()
        gh_status = "good" if gh_data['status']['indicator'] == "none" else "critical"
        gh_feed = [{"time": datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%H:%M'), "text": i['name']} for i in gh_data.get('incidents', [])[:3]]
        results.append({
            "name": "GitHub", 
            "status": "All Systems Operational" if gh_status == "good" else "Service Incident",
            "class": gh_status, 
            "logo": logos["GitHub"], 
            "url": public_urls["GitHub"], 
            "feed": gh_feed, 
            "tag": None
        })
    except:
        results.append({"name": "GitHub", "status": "API Error", "class": "critical", "logo": logos["GitHub"], "url": "#", "feed": [], "tag": None})

    # ---------------------------------------------------------
    # 2. ATLASSIAN (Multi-Target Direct Scan)
    # ---------------------------------------------------------
    try: # Start the main protective block
        atl_final_status = "All Systems Operational"
        atl_final_class = "good"
        atl_final_url = "https://status.atlassian.com"
        atl_final_feed = []
        atl_affected_tags = [] 

        for target in ATLASSIAN_TARGETS:
            try:
                resp = requests.get(target["api"], timeout=2)
                data = resp.json()
                
                if data.get('incidents'):
                    inc = data['incidents'][0]
                    # Update card to the worst status found
                    if atl_final_class != "critical":
                        atl_final_class = "critical" if inc['impact'] in ['major', 'critical'] else "warning"
                        atl_final_status = "Service Incident"
                    
                    atl_affected_tags.append(target["name"].upper())
                    
                    if len(atl_final_feed) < 3:
                        try: dt = datetime.strptime(inc['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                        except: dt = datetime.now()
                        body = inc['incident_updates'][0]['body'] if inc.get('incident_updates') else inc['name']
                        atl_final_feed.append({"time": dt.strftime('%H:%M'), "text": f"[{target['name'].upper()}] {body}"})
                
                elif data.get('status', {}).get('indicator') != "none":
                    if atl_final_class == "good":
                        atl_final_class = "warning"
                        atl_final_status = "Performance Degraded"
                    atl_affected_tags.append(target["name"].upper())

            except:
                continue

        # Append result inside the try block
        results.append({
            "name": "Atlassian", 
            "status": atl_final_status, 
            "class": atl_final_class, 
            "logo": logos["Atlassian"], 
            "url": atl_final_url, 
            "feed": atl_final_feed,
            "tag": atl_affected_tags # Passed as a list
        })

    except Exception as e:
        print(f"Atlassian Block Error: {e}")
        results.append({"name": "Atlassian", "status": "API Error", "class": "critical", "logo": logos["Atlassian"], "url": "#", "feed": [], "tag": ["ERROR"]})

    # ---------------------------------------------------------
    # 3. AWS CHECKS (RSS)
    # ---------------------------------------------------------
    for svc in ["ec2", "s3", "lambda"]:
        name_key = f"AWS {svc.upper()}"
        rss_url = f"https://status.aws.amazon.com/rss/{svc}-us-east-1.rss"
        try:
            feed = feedparser.parse(rss_url)
            messages = []
            # Only grab top 1 entry for feed to keep layout clean
            for entry in feed.entries[:1]:
                time_str = datetime(*entry.published_parsed[:6]).strftime('%b %d %H:%M')
                messages.append({"time": time_str, "text": entry.title})
            
            is_normal = not feed.entries or "normally" in feed.entries[0].title.lower()
            
            results.append({
                "name": name_key, "region": "us-east-1", 
                "status": "All Services Operational" if is_normal else "Service Alert", 
                "class": "good" if is_normal else "warning", 
                "logo": logos.get(name_key, ""), 
                "url": public_urls.get(name_key, "#"), 
                "feed": messages, "tag": None
            })
        except:
            results.append({"name": name_key, "status": "RSS Error", "class": "critical", "logo": logos.get(name_key, ""), "url": "#", "feed": [], "tag": None})
            
    return results

@app.route('/')
def index():
    status_list = get_health_data()
    on_call_person = get_on_call()
    maintenance_info = get_maintenance()
    
    # Process Ticket Data: Calculate color classes here in the route
    processed_tickets = []
    for t in RAW_TICKETS:
        # Create a copy so we don't modify the original data file
        ticket = t.copy()
        ticket['color_class'] = get_ticket_status_class(t['status'])
        processed_tickets.append(ticket)

    ticket_feed = {"status": "Active", "tickets": processed_tickets}
    
    now = datetime.now()
    return render_template('index.html', 
                           services=status_list, 
                           admin_links=ADMIN_LINKS, 
                           ticket_feed=ticket_feed,
                           on_call=on_call_person,
                           maintenance=maintenance_info, 
                           last_updated=now.strftime("%H:%M"), 
                           date=now.strftime("%b %d, %Y"))

if __name__ == '__main__':
    app.run(debug=True, port=5000)