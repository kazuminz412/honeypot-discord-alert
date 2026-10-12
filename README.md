Markdown
# 🛡️ Real-Time Honeypot Monitor & OSINT Alert System

A DevSecOps project that deploys a Cowrie SSH Honeypot, monitors attack logs in real-time bypassing Docker container boundaries, and sends automated threat intelligence alerts to Discord using the AbuseIPDB API.

## 🚀 Architecture & Technologies
* **Infrastructure:** AWS EC2 (Ubuntu), Docker
* **Security Tool:** Cowrie (Medium-interaction SSH/Telnet Honeypot)
* **Scripting:** Python 3 (Subprocess `tail -F` for real-time log streaming)
* **Integrations:** Discord Webhook (Alerts), AbuseIPDB API (OSINT GeoIP & Threat Scoring)

## 🛠️ Installation & Setup

**Step 1: Clone the repository**
```bash
git clone [https://github.com/YOUR_GITHUB_NAME/honeypot-discord-alert.git](https://github.com/YOUR_GITHUB_NAME/honeypot-discord-alert.git)
cd honeypot-discord-alert
Step 2: Install required Python packages

Bash
pip3 install -r requirements.txt --break-system-packages
Step 3: Configure Environment Variables
Rename .env.example to .env and insert your API keys:

Bash
cp .env.example .env
nano .env
Step 4: Deploy the Cowrie Honeypot (Docker)
Run the automated setup script to map ports (22:2222) and bind volumes for log extraction:

Bash
./setup_honeypot.sh
Step 5: Start the Monitoring System
Run the Python script in the background using nohup:

Bash
nohup python3 honeypot_alert.py > alert.log 2>&1 &
