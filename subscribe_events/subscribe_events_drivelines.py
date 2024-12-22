import requests
import hmac
import hashlib
import base64
import time
import json

# Configuration
BASE_URL = "https://p1pn4rm.localto.net"
API_KEY = "20605867"
API_SECRET = "p1zuLfVz9KjHrBxfjfZz"

def generate_signature(method: str, content_type: str, ca_key: str, path_url: str, timestamp: str, secret_key: str) -> str:
    string_to_sign = f"{method}\n*/*\n{content_type}\nx-ca-key:{ca_key}\nx-ca-timestamp:{timestamp}\n{path_url}"
    
    hmac_sha256 = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    return base64.b64encode(hmac_sha256).decode('utf-8')

def subscribe_client_url():
    endpoint = "/artemis/api/eventService/v1/eventSubscriptionByEventTypes"
    client_url = "https://api.urbancircle.co.za/api/hik_face_scan"
    
    print(f"\nSubscribing {client_url} to event type 196893...")
    
    data = {
        "eventTypes": [196893],
        "eventDest": client_url,
        "token": "webhook-token",
        "passBack": 0
    }
    
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(
        method='POST',
        content_type='application/json',
        ca_key=API_KEY,
        path_url=endpoint,
        timestamp=timestamp,
        secret_key=API_SECRET
    )
    
    headers = {
        'Content-Type': 'application/json',
        'x-ca-key': API_KEY,
        'x-ca-signature': signature,
        'x-ca-signature-headers': 'x-ca-key,x-ca-timestamp',
        'x-ca-timestamp': timestamp,
        'Accept': '*/*'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}{endpoint}',
            headers=headers,
            json=data,
            verify=False,
            cookies={'localtonet-skip-warning': 'true'}
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        if response_data.get('code') != '0':
            raise Exception(f"API Error: {response_data.get('msg', 'Unknown error')}")
            
        print(f"Successfully subscribed {client_url} to event type 196893")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to subscribe: Network error occurred: {str(e)}")
        raise
    except Exception as e:
        print(f"Failed to subscribe: {str(e)}")
        raise

if __name__ == '__main__':
    subscribe_client_url()
