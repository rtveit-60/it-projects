from datetime import datetime
from flask import Flask, render_template
import requests
import feedparser

app = Flask(__name__)

def get_health_data():
    results = []
    
    # Vendor Logos
    logos = {
        "GitHub": "https://github.githubassets.com/favicons/favicon.svg",
        "Atlassian": "https://wac-cdn.atlassian.com/assets/img/favicons/atlassian/favicon.png",
        "AWS EC2": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS S3": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS LAMBDA": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png"
    }

    # 1. JSON APIs (Global Services)
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
            
            # UPDATED: Force your specific text if status is healthy
            display_status = "All Services Currently Operational" if indicator == "none" else data.get('status', {}).get('description', 'Status Unknown')
            
            messages = []
            for inc in data.get('incidents', [])[:5]:
                dt = datetime.strptime(inc['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                messages.append({"time": dt.strftime('%H:%M'), "text": inc['name']})

            results.append({
                "name": name,
                "region": None,
                "status": display_status, 
                "class": status_class,
                "logo": logos.get(name, ""),
                "feed": messages
            })
        except Exception:
            results.append({"name": name, "status": "API Error", "class": "critical", "logo": logos.get(name, ""), "feed": []})

    # 2. AWS RSS Feeds (Regional)
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
            
            results.append({
                "name": name_key,
                "region": "us-east-1",
                # UPDATED: Force your specific text for AWS
                "status": "All Services Currently Operational" if is_normal else "Service Alert",
                "class": "good" if is_normal else "warning",
                "logo": logos.get(name_key, ""),
                "feed": messages
            })
        except Exception:
            results.append({"name": name_key, "status": "RSS Error", "class": "critical", "logo": logos.get(name_key, ""), "feed": []})
    
    return results

@app.route('/')
def index():
    status_list = get_health_data()
    
    # Corporate Admin Links
    admin_links = [
        {"name": "EntraID", "url": "https://entra.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=entra.microsoft.com&sz=64"},
        {"name": "Intune", "url": "https://intune.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=intune.microsoft.com&sz=64"},
        {"name": "365 Admin", "url": "https://admin.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=admin.microsoft.com&sz=64"},
        {"name": "Google Admin", "url": "https://admin.google.com", "icon": "https://www.google.com/s2/favicons?domain=admin.google.com&sz=64"},
        {"name": "vCenter", "url": "https://vcenter.local", "icon": "https://www.google.com/s2/favicons?domain=vmware.com&sz=64"},
        {"name": "CDW", "url": "https://www.cdw.com", "icon": "https://www.google.com/s2/favicons?domain=cdw.com&sz=64"},
        {"name": "Apple Business", "url": "https://business.apple.com", "icon": "https://www.apple.com/favicon.ico"},
        # {"name": "Confluence", "url": "#", "icon": "https://www.google.com/s2/favicons?domain=atlassian.com&sz=64"} 
    ]
    
    # Ticket Feed
    ticket_feed = {
        "status": "Concept Preview",
        "tickets": [
            {"id": "INC-1024", "summary": "Outlook connectivity issues reported by Sales", "time": "10:42"},
            {"id": "REQ-3391", "summary": "New user onboarding: Sarah Jenkins", "time": "09:15"},
            {"id": "INC-1023", "summary": "Printer on 3rd floor jamming", "time": "08:55"}
        ]
    }
    
    now = datetime.now()
    return render_template('index.html', 
                           services=status_list, 
                           admin_links=admin_links,
                           ticket_feed=ticket_feed,
                           last_updated=now.strftime("%H:%M"), 
                           date=now.strftime("%b %d, %Y"))

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Note: In production, use a WSGI server like Gunicorn or Waitress instead of Flask's built-in server.