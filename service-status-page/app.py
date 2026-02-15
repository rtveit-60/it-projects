from datetime import datetime
from flask import Flask, render_template
import requests
import feedparser

app = Flask(__name__)

def get_health_data():
    results = []
    
    # 1. Vendor Logos
    logos = {
        "GitHub": "https://github.githubassets.com/favicons/favicon.svg",
        "Atlassian": "https://wac-cdn.atlassian.com/assets/img/favicons/atlassian/favicon.png",
        "AWS EC2": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS S3": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "AWS LAMBDA": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png"
    }

    # 2. JSON APIs (Global Services)
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
            
            messages = []
            incidents = data.get('incidents', [])[:5]
            
            for inc in incidents:
                dt = datetime.strptime(inc['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                messages.append({
                    "time": dt.strftime('%H:%M'),
                    "text": inc['name']
                })

            if not messages:
                messages.append({
                    "time": datetime.now().strftime('%H:%M'),
                    "text": "No active incidents reported by vendor."
                })

            results.append({
                "name": name,
                "region": None,  # Global services don't need a region tag
                "status": data.get('status', {}).get('description', 'Status Unknown'),
                "class": status_class,
                "logo": logos.get(name, ""),
                "feed": messages
            })
        except Exception:
            results.append({
                "name": name, "status": "API Error", "class": "critical", 
                "logo": logos.get(name, ""), "feed": []
            })

    # 3. AWS RSS Feeds (Regional Services)
    for svc in ["ec2", "s3", "lambda"]:
        name_key = f"AWS {svc.upper()}"
        rss_url = f"https://status.aws.amazon.com/rss/{svc}-us-east-1.rss"
        try:
            feed = feedparser.parse(rss_url)
            messages = []
            
            for entry in feed.entries[:5]:
                time_str = datetime(*entry.published_parsed[:6]).strftime('%H:%M')
                messages.append({
                    "time": time_str,
                    "text": entry.title
                })

            if not messages:
                messages.append({
                    "time": datetime.now().strftime('%H:%M'),
                    "text": "Service is operating normally."
                })

            latest_msg = feed.entries[0].title.lower() if feed.entries else "normally"
            is_normal = "normally" in latest_msg
            
            results.append({
                "name": name_key,
                "region": "us-east-1",  # Specifying the region for AWS
                "status": "Operational" if is_normal else "Service Alert",
                "class": "good" if is_normal else "warning",
                "logo": logos.get(name_key, ""),
                "feed": messages
            })
        except Exception:
            results.append({
                "name": name_key, "status": "RSS Error", "class": "critical", 
                "logo": logos.get(name_key, ""), "feed": []
            })
    
    return results

@app.route('/')
def index():
    status_list = get_health_data()
    if status_list is None:
        status_list = []
        
    now = datetime.now()
    return render_template('index.html', 
                           services=status_list, 
                           last_updated=now.strftime("%H:%M"), 
                           date=now.strftime("%b %d, %Y"))

if __name__ == '__main__':
    app.run(debug=True, port=5000)