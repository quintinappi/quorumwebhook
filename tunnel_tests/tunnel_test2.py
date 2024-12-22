import requests
import time
from datetime import datetime
import os
from typing import List, Dict
import logging
import sys
import signal
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Tunnel configuration with proper names and API endpoints
TUNNELS = [
    {"id": "765134", "url": "wx5pcvv.localto.net/artemis/api/common/v1/version", "name": "Notabene"},
    {"id": "765133", "url": "t5jvtxu.localto.net/artemis/api/common/v1/version", "name": "Stanley"},
    {"id": "765132", "url": "yxlbrot.localto.net/artemis/api/common/v1/version", "name": "Highbury"},
    {"id": "765131", "url": "jntsjov.localto.net/artemis/api/common/v1/version", "name": "Sovereign"},
    {"id": "765129", "url": "1fwhfbk.localto.net/artemis/api/common/v1/version", "name": "Eastside"},
    {"id": "765128", "url": "p1pn4rm.localto.net/artemis/api/common/v1/version", "name": "Drivelines"},
    {"id": "752191", "url": "0iy4hkn.localto.net/artemis/api/common/v1/version", "name": "Workandart"},
]

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": "mail.arqtek.co.za",
    "smtp_port": 26,
    "username": "noreply@arqtek.co.za",
    "password": "debruinresidence123",
    "recipient": "quintin@arqtek.co.za"
}

# Global flag for graceful shutdown
running = True

def signal_handler(signum, frame):
    """Handle interrupt signal."""
    global running
    logging.info("Stopping tunnel monitoring...")
    running = False

def check_tunnel_status(url: str) -> bool:
    """Check if a tunnel is online by making an HTTP request to the API endpoint."""
    try:
        logging.info(f"Checking tunnel: {url}")
        session = requests.Session()
        session.verify = False
        response = session.get(
            f"https://{url}",
            timeout=3,
            allow_redirects=False
        )
        session.close()
        return True
    except requests.RequestException as e:
        logging.error(f"Error checking tunnel {url}: {str(e)}")
        return False

def format_status_message(tunnels_status: list) -> tuple:
    """Format the status message for the template."""
    online_tunnels = [t["name"] for t in tunnels_status if t["status"]]
    offline_tunnels = [t["name"] for t in tunnels_status if not t["status"]]
    
    parts = []
    parts.append(f"{len(online_tunnels)} online, {len(offline_tunnels)} offline")
    
    if online_tunnels:
        parts.append(f"🟢 Online: {', '.join(online_tunnels)}")
    if offline_tunnels:
        parts.append(f"🔴 Offline: {', '.join(offline_tunnels)}")
    
    status_text = ". ".join(parts)
    time_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return status_text, time_text

def send_email_notification(message_tuple: tuple) -> bool:
    """Send an email notification about tunnel status."""
    status_text, time_text = message_tuple
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['username']
        msg['To'] = EMAIL_CONFIG['recipient']
        msg['Subject'] = f"Tunnel Status Report - {time_text}"
        
        body = f"""
        Tunnel Status Report
        
        Time: {time_text}
        Status: {status_text}
        
        This is an automated message from the Tunnel Monitor.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()  # Enable TLS
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Email sent successfully to {EMAIL_CONFIG['recipient']}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return False

def check_all_tunnels() -> list:
    """Check all tunnels and return their status."""
    tunnels_status = []
    
    for tunnel in TUNNELS:
        if not running:  # Check if we should stop
            break
        is_online = check_tunnel_status(tunnel["url"])
        tunnels_status.append({
            "name": tunnel["name"],
            "status": is_online
        })
    
    return tunnels_status

def test_email():
    """Test email connectivity with a simple message."""
    test_status = "5 online, 2 offline. 🟢 Online: Notabene, Highbury, Sovereign, Drivelines, Workandart. 🔴 Offline: Stanley, Eastside"
    test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if send_email_notification((test_status, test_time)):
        logging.info("Email test successful!")
        return True
    else:
        logging.error("Email test failed!")
        return False

def main():
    """Main function to check tunnel status and send notifications."""
    global running
    while running:
        # Check all tunnels
        tunnels_status = check_all_tunnels()
        
        # Format and send message
        message_tuple = format_status_message(tunnels_status)
        send_email_notification(message_tuple)
        
        # Sleep for 1 hour (3600 seconds)
        time.sleep(3600)

if __name__ == "__main__":
    # Test email connection first
    if not test_email():
        logging.error("Email test failed! Please check your configuration.")
        sys.exit(1)
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start monitoring
    main()