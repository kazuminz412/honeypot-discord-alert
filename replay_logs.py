import json
import requests
import os
import glob
import time
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ABUSE_API_KEY = os.getenv("ABUSEIPDB_API_KEY")

log_pattern = "/home/ubuntu/cowrie-live-logs/cowrie.json*"
MAX_EVENTS = 30  # Số lượng sự kiện gần nhất muốn gửi bù
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

def send_discord_alert(ip, timestamp, username, password=None, command=None):
    ip_details = get_ip_info(ip)
    
    if command is not None:
        title = "💻 [HISTORICAL] HACKER COMMAND EXECUTED!"
        description = f"🕒 **Time:** `{timestamp}`\n**Hacker IP:** `{ip}`\n**Command:** `{command}`\n{'-'*20}{ip_details}"
        color = 16753920
    else:
        title = "🚨 [HISTORICAL] HACKER LOGIN DETECTED!"
        description = f"🕒 **Time:** `{timestamp}`\n**Hacker IP:** `{ip}`\n**Username:** `{username}`\n**Password:** `{password}`\n{'-'*20}{ip_details}"
        color = 16711680

    data = {"embeds": [{"title": title, "description": description, "color": color}]}
    try:
        if WEBHOOK_URL:
            res = requests.post(WEBHOOK_URL, json=data, timeout=5)
            # Nếu vẫn chạm giới hạn của Discord, tự động đợi theo yêu cầu của server
            if res.status_code == 429:
                retry_after = res.json().get("retry_after", 5)
                print(f"[!] Rate limited by Discord. Waiting {retry_after}s...")
                time.sleep(float(retry_after))
                requests.post(WEBHOOK_URL, json=data, timeout=5)
    except Exception as e:
        print(f"[!] Error sending webhook: {e}")

print("[*] Scanning historical log files...")
log_files = sorted(glob.glob(log_pattern), key=os.path.getmtime)

events_to_send = []

for file_path in log_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    event_id = data.get("eventid")
                    if event_id in ["cowrie.login.success", "cowrie.command.input"]:
                        events_to_send.append(data)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"[!] Could not read {file_path}: {e}")

total_found = len(events_to_send)
print(f"[+] Found {total_found} total events across {len(log_files)} log file(s).")

# Cắt lấy MAX_EVENTS sự kiện gần nhất
selected_events = events_to_send[-MAX_EVENTS:] if MAX_EVENTS else events_to_send
print(f"[*] Replaying the last {len(selected_events)} events to Discord (2 seconds delay per message)...")

for idx, data in enumerate(selected_events, 1):
    event_id = data.get("eventid")
    ip = data.get("src_ip")
    timestamp = data.get("timestamp", "Unknown Time")
    
    if event_id == "cowrie.login.success":
        pwd = data.get("password") or "(empty)"
        print(f"[{idx}/{len(selected_events)}] Sending Login Alert from {ip} at {timestamp}...")
        send_discord_alert(ip, timestamp, data.get("username"), password=pwd)
    elif event_id == "cowrie.command.input":
        cmd = data.get("input") or "(empty)"
        print(f"[{idx}/{len(selected_events)}] Sending Command Alert from {ip} at {timestamp}...")
        send_discord_alert(ip, timestamp, "N/A", command=cmd)
        
    time.sleep(2)

print("[+] Done! All selected historical alerts have been sent to Discord.")
