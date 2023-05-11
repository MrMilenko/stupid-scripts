# failscale.py is a simple tailscale monitor to setup as a cron job.

import requests
import subprocess
import platform

TAILSCALE_STATUS_COMMAND = "tailscale status"
TAILSCALE_STATUS_DARWIN = "/Applications/Tailscale.app/Contents/MacOS/Tailscale status"
WEBHOOK_URL = "set.a.webhook.here"

# Set the notification mode: 0 for webhook, 1 for local message
notification_mode = 1

# Check Tailscale status
if platform.system() == "Darwin":
    tailscale_status = subprocess.run(TAILSCALE_STATUS_DARWIN, stdout=subprocess.PIPE, shell=True)
else:
    tailscale_status = subprocess.run(TAILSCALE_STATUS_COMMAND, stdout=subprocess.PIPE, shell=True)
tailscale_status = tailscale_status.stdout.decode('utf-8')

# Parse Tailscale status output
devices = []
offline_devices = []
for line in tailscale_status.split('\n')[1:]:
    if not line:
        continue
    parts = line.split()
    ip_address, name, user, os, status = parts[:5]
# Set the username we want to monitor (like a service user on all systems)
    if user == "user@":
        devices.append({
            "ip_address": ip_address,
            "name": name,
            "user": user,
            "os": os,
            "status": status
        })
        if status == "offline":
            offline_devices.append(f"{name} ({ip_address})")

# Check for offline devices
if offline_devices:
    if notification_mode == 0:
        # Send message to Teams webhook
        message = {
            "text": "The following Tailscale devices are offline:\n\n" + '\n'.join(offline_devices)
        }
        response = requests.post(WEBHOOK_URL, json=message)
        if response.status_code != 200:
            print(f"Failed to send message to Teams webhook: {response.text}")
        else:
            print("Webhook message sent successfully")
    elif notification_mode == 1:
        # Display system notification for Linux or macOS
        system = platform.system()
        if system == "Linux":
            subprocess.run(['notify-send', "Tailscale Devices Offline", '\n'.join(offline_devices)])
        elif system == "Darwin":
            subprocess.run(['osascript', '-e', f'display notification "{", ".join(offline_devices)}" with title "Tailscale Devices Offline"'])
        else:
            print("System notifications are only supported on Linux and macOS.")
else:
    print("All Tailscale devices are online")
