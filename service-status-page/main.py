import requests
import feedparser
import time
from datetime import datetime

def get_json_status(name, url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        indicator = data['status']['indicator']
        status = "✅ OPERATIONAL" if indicator == "none" else "⚠️ ISSUES"
        return {"service": name, "status": status, "message": data['status']['description']}
    except Exception as e:
        return {"service": name, "status": "❌ ERROR", "message": "API Unreachable"}

def get_aws_rss_status(service_slug):
    url = f"https://status.aws.amazon.com/rss/{service_slug}-us-east-1.rss"
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return {"service": f"AWS {service_slug.upper()}", "status": "✅ OPERATIONAL", "message": "Normal"}
        
        latest = feed.entries[0]
        status = "✅ OPERATIONAL" if "operating normally" in latest.title.lower() else "⚠️ ISSUES"
        return {"service": f"AWS {service_slug.upper()}", "status": status, "message": latest.title}
    except Exception as e:
        return {"service": f"AWS {service_slug.upper()}", "status": "❌ ERROR", "message": "RSS Unreachable"}

def run_dashboard():
    # Clear terminal (optional, works for Windows)
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"--- SERVICE HEALTH DASHBOARD | Last Updated: {datetime.now().strftime('%H:%M:%S')} ---")
    print(f"{'SERVICE':<18} | {'STATUS':<15} | {'DETAIL'}")
    print("-" * 70)

    # Combined target list
    results = []
    
    # JSON Targets
    results.append(get_json_status("GitHub", "https://www.githubstatus.com/api/v2/summary.json"))
    results.append(get_json_status("Atlassian", "https://status.atlassian.com/api/v2/summary.json"))
    
    # AWS Targets
    for svc in ["ec2", "s3", "lambda"]:
        results.append(get_aws_rss_status(svc))

    for item in results:
        print(f"{item['service']:<18} | {item['status']:<15} | {item['message']}")

# --- MAIN LOOP ---
if __name__ == "__main__":
    try:
        while True:
            run_dashboard()
            print("\nUpdating in 5 minutes... (Press Ctrl+C to stop)")
            time.sleep(300) # Wait 300 seconds
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")