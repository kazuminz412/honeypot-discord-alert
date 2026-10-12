#!/bin/bash

echo "[*] Creating live log directory..."
mkdir -p ~/cowrie-live-logs
sudo chmod 777 ~/cowrie-live-logs

echo "[*] Deploying Cowrie Honeypot Container on Port 22..."
sudo docker rm -f cowrie-honeypot 2>/dev/null
sudo docker run -d \
  -p 22:2222 \
  -p 23:2223 \
  --name cowrie-honeypot \
  -v ~/cowrie-live-logs:/cowrie/cowrie-git/var/log/cowrie \
  cowrie/cowrie

echo "[+] Cowrie Honeypot is running successfully!"
