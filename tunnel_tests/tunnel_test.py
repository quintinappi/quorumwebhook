import requests
import hmac
import hashlib
import base64
import time
import concurrent.futures
from typing import Dict, List
import json

# Configuration for all sites
SITES_CONFIG = [
    {
        "name": "Workandart",
        "url": "0iy4hkn.localto.net",
        "key": "29316373",
        "secret": "3RAG4CjqZHxCsa2SgBUm"
    },
    {
        "name": "Notabene",
        "url": "wx5pcvv.localto.net",
        "key": "20925621",
        "secret": "2dSTGerv15szic8pf94u"
    },
    {
        "name": "Eastside",
        "url": "1fwhfbk.localto.net",
        "key": "29297534",
        "secret": "PXekgXERv7OPGtyOLaFI"
    },
    {
        "name": "Sovereign",
        "url": "jntsjov.localto.net",
        "key": "24285273",
        "secret": "bMoPZp96osNw4HBBK2av"
    },
    {
        "name": "Stanley",
        "url": "t5jvtxu.localto.net",
        "key": "27794331",
        "secret": "jQXmam6ZxbJZ6eCgiT8e"
    },
    {
        "name": "Drivelines",
        "url": "p1pn4rm.localto.net",
        "key": "20605867",
        "secret": "p1zuLfVz9KjHrBxfjfZz"
    },
    {
        "name": "Highbury",
        "url": "yxlbrot.localto.net",
        "key": "23172008",
        "secret": "KYvfOCfPXoSonLV5Ligj"
    }
]

def generate_hmac_sha256_signature(method: str, content_type: str, ca_key: str, 
                                 path_url: str, timestamp: str, secret_key: str) -> str:
    string_to_sign = f"{method}\n*/*\n{content_type}\nx-ca-key:{ca_key}\nx-ca-timestamp:{timestamp}\n{path_url}"
    
    hmac_sha256 = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    return base64.b64encode(hmac_sha256).decode('utf-8')

def test_single_attempt(site_config: Dict) -> Dict:
    """Make a single test attempt for a site"""
    path_url = '/artemis/api/common/v1/version'
    url = f'https://{site_config["url"]}{path_url}'
    timestamp = str(int(time.time() * 1000))
    
    signature = generate_hmac_sha256_signature(
        method='POST',
        content_type='application/json',
        ca_key=site_config['key'],
        path_url=path_url,
        timestamp=timestamp,
        secret_key=site_config['secret']
    )
    
    headers = {
        'Content-Type': 'application/json',
        'x-ca-key': site_config['key'],
        'x-ca-signature': signature,
        'x-ca-signature-headers': 'x-ca-key,x-ca-timestamp',
        'x-ca-timestamp': timestamp
    }
    
    cookies = {
        'localtonet-skip-warning': 'true'
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json={}, timeout=10)
        response_data = response.json() if response.status_code == 200 else response.text
        return {
            "status_code": response.status_code,
            "response": response_data,
            "success": response.status_code == 200 and 
                      isinstance(response_data, dict) and 
                      response_data.get("msg") == "Success"
        }
    except Exception as e:
        return {
            "status_code": None,
            "response": str(e),
            "success": False
        }

def test_single_site(site_config: Dict) -> Dict:
    """Test a single site three times and compile results"""
    attempts = []
    for i in range(3):
        attempt = test_single_attempt(site_config)
        attempts.append(attempt)
        time.sleep(1)  # Brief pause between attempts
    
    # Site is considered successful only if all three attempts are successful
    all_successful = all(attempt["success"] for attempt in attempts)
    
    return {
        "name": site_config["name"],
        "url": site_config["url"],
        "success": all_successful,
        "attempts": attempts
    }

def test_all_sites():
    """Test all sites concurrently and print results"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(SITES_CONFIG)) as executor:
        future_to_site = {executor.submit(test_single_site, site): site for site in SITES_CONFIG}
        
        print("\nTesting all sites (3 attempts each)...\n")
        print("-" * 80)
        
        for future in concurrent.futures.as_completed(future_to_site):
            result = future.result()
            status = "✅" if result["success"] else "❌"
            print(f"\n{status} {result['name']} ({result['url']})")
            
            for i, attempt in enumerate(result["attempts"], 1):
                attempt_status = "✅" if attempt["success"] else "❌"
                print(f"\nAttempt {i}: {attempt_status}")
                print(f"Status Code: {attempt['status_code']}")
                if isinstance(attempt["response"], dict):
                    print("Response:", json.dumps(attempt["response"], indent=2))
                else:
                    print("Response:", attempt["response"])
            
            print("-" * 80)

if __name__ == "__main__":
    # Test only Highbury
    site_config = {
        "name": "Highbury",
        "url": "yxlbrot.localto.net",
        "key": "23172008",
        "secret": "KYvfOCfPXoSonLV5Ligj"  # Using correct secret from SITES_CONFIG
    }
    result = test_single_site(site_config)
    print(f"\n{'✅' if result['success'] else '❌'} {result['name']} ({result['url']})\n")
    for i, attempt in enumerate(result['attempts'], 1):
        print(f"Attempt {i}: {'✅' if attempt['success'] else '❌'}")
        print(f"Status Code: {attempt['status_code']}")
        print(f"Response: {json.dumps(attempt['response'], indent=2)}\n")