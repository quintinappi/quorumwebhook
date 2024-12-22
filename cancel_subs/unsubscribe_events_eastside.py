import requests
import hmac
import hashlib
import base64
import time
import json

# Configuration
BASE_URL = "https://1fwhfbk.localto.net"
API_KEY = "29297534"
API_SECRET = "PXekgXERv7OPGtyOLaFI"
CALLBACK_URL = "https://api.urbancircle.co.za/api/hik_face_scan"
EVENT_TYPES = [196893]  # Access Granted by Face

def generate_signature(method: str, content_type: str, ca_key: str, path_url: str, timestamp: str, secret_key: str) -> str:
    string_to_sign = f"{method}\n*/*\n{content_type}\nx-ca-key:{ca_key}\nx-ca-timestamp:{timestamp}\n{path_url}"
    
    hmac_sha256 = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    return base64.b64encode(hmac_sha256).decode('utf-8')

def unsubscribe_from_events():
    # API endpoint
    endpoint = "/artemis/api/eventService/v1/eventUnSubscriptionByEventTypes"
    
    # Request body
    data = {
        "eventTypes": EVENT_TYPES,
        "eventDest": CALLBACK_URL,
        "token": "webhook-token",
        "passBack": 0
    }
    
    # Generate timestamp
    timestamp = str(int(time.time() * 1000))
    
    # Generate signature
    signature = generate_signature(
        method='DELETE',
        content_type='application/json',
        ca_key=API_KEY,
        path_url=endpoint,
        timestamp=timestamp,
        secret_key=API_SECRET
    )
    
    # Prepare headers
    headers = {
        'Content-Type': 'application/json',
        'x-ca-key': API_KEY,
        'x-ca-signature': signature,
        'x-ca-signature-headers': 'x-ca-key,x-ca-timestamp',
        'x-ca-timestamp': timestamp
    }
    
    # Make the request
    response = requests.delete(
        f'{BASE_URL}{endpoint}',
        headers=headers,
        json=data,
        verify=False
    )
    
    print(f'Response Status: {response.status_code}')
    print('Response Body:')
    print(response.text)

if __name__ == '__main__':
    unsubscribe_from_events()
