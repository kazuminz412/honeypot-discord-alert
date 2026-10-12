import json
import requests
import subprocess
import os
from dotenv import load_dotenv

# Load secret configuration from .env file
load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ABUSE_API_KEY = os.getenv("ABUSEIPDB_API_KEY")

log_file = "/home/ubuntu/cowrie-live-logs/cowrie.json"
ip_cache = {}

def get_ip_info(ip):
    if ip in ip_cache:
        return ip_cache[ip]
        
    url = 'https://api.abuseipdb.com/api/v2/check'
    querystring = {'ipAddress': ip, 'maxAgeInDays': '90'}
    headers = {'Accept': 'application/json', 'Key': ABUSE_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        data = response.json()
        if 'data' in data:
            info = data['data']
            result = f"\n🌍 **Country:** {info['countryCode']}\n🚨 **Abuse Score:** {info['abuseConfidenceScore']}%\n🛑 **Reported:** {info['totalReports']} times"
            ip_cache[ip] = result
            return result
    except Exception:
        return "\n⚠️ *Cannot connect to OSINT service at this time.*"
    return ""

def send_discord_alert(ip, username, password=None, command=None):
    ip_details = get_ip_info(ip)
    
    if password:
        title = "🚨 ALERT: HACKER LOGIN DETECTED!"
        description = f"**Hacker IP:** `{ip}`\n**Username:** `{username}`\n**Password:** `{password}`\n{'-'*20}{ip_details}"
        color = 16711680
    elif command:
        title = "💻 ALERT: HACKER COMMAND EXECUTED!"
        description = f"**Hacker IP:** `{ip}`\n**Command:** `{command}`\n{'-'*20}{ip_details}"
        color = 16753920

    data = {"embeds": [{"title": title, "description": description, "color": color}]}
    try:
        if WEBHOOK_URL:
            requests.post(WEBHOOK_URL, json=data)
    except Exception:
        pass

print("--- REAL-TIME HONEYPOT MONITOR & OSINT RUNNING ---")

try:
    process = subprocess.Popen(['tail', '-n', '0', '-F', log_file], stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if not line:
            continue
        try:
            text_line = line.decode('utf-8').strip()
            data = json.loads(text_line)
            event_id = data.get("eventid")
            
            if event_id == "cowrie.login.success":
                ip = data.get("src_ip")
                send_discord_alert(ip, data.get("username"), password=data.get("password"))
            elif event_id == "cowrie.command.input":
                ip = data.get("src_ip")
                send_discord_alert(ip, "N/A", command=data.get("input"))
                
        except json.JSONDecodeError:
            continue
except KeyboardInterrupt:
    print("\nMonitoring system terminated.")
