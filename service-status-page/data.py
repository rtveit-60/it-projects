# data.py

# --- IT ADMINISTRATOR TOOLBOX LINKS ---
ADMIN_LINKS = [
    {"name": "EntraID", "url": "https://entra.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=entra.microsoft.com&sz=64"},
    {"name": "Intune", "url": "https://intune.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=intune.microsoft.com&sz=64"},
    {"name": "365 Admin", "url": "https://admin.microsoft.com", "icon": "https://www.google.com/s2/favicons?domain=admin.microsoft.com&sz=64"},
    {"name": "Google Admin", "url": "https://admin.google.com", "icon": "https://www.google.com/s2/favicons?domain=admin.google.com&sz=64"},
    {"name": "vCenter", "url": "https://vcenter.local", "icon": "https://www.google.com/s2/favicons?domain=vmware.com&sz=64"},
    {"name": "CDW", "url": "https://www.cdw.com", "icon": "https://www.google.com/s2/favicons?domain=cdw.com&sz=64"},
    {"name": "Apple Business Manager", "url": "https://business.apple.com", "icon": "https://www.apple.com/favicon.ico"},
]

# --- MOCK TICKET DATA ---
RAW_TICKETS = [
    {
        "id": "INC-1024", 
        "summary": "Outlook connectivity issues", 
        "description": "Users in Sales reporting intermittent connection errors when sending emails with large attachments.", 
        "status": "In Progress", 
        "assigned_to": "Alex Mercer", 
        "time": "10:42"
    },
    {
        "id": "REQ-3391", 
        "summary": "New user onboarding: Sarah Jenkins", 
        "description": "Provision AD account and O365 license for new HR Manager starting Monday.", 
        "status": "Waiting for Customer", 
        "assigned_to": "Jordan Smith", 
        "time": "09:15"
    },
    {
        "id": "INC-1023", 
        "summary": "Printer on 3rd floor jamming", 
        "description": "Xerox AltaLink displaying Tray 2 Jam error despite being cleared.", 
        "status": "Waiting for Support", 
        "assigned_to": "Unassigned", 
        "time": "08:55"
    },
    {
        "id": "INC-1010", 
        "summary": "Password Reset", 
        "description": "User locked out of ERP portal after several failed login attempts.", 
        "status": "Done", 
        "assigned_to": "Alex Mercer", 
        "time": "08:00"
    }
]

# --- ON-CALL USER ---
ON_CALL_USER = {
    "name": "Alex Mercer",
    "email": "amercer@company.com",
    "avatar": "https://i.pravatar.cc/150?u=alex", 
    "status": "On-Shift"
}

# --- MAINTENANCE CONFIGURATION ---
# Note: Start/End times are calculated in app.py to keep them dynamic relative to "now"
MAINTENANCE_INFO = {
    "title": "Core Firewall Firmware Upgrade",
    "id": "CR-4402",
    "window_str": "Sat 10:00 PM - 2:00 AM CST"
}