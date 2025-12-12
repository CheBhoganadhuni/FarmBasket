import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/auth"
EMAIL = "debug_user@farmbasket.com"
PASSWORD = "DebugUser@123"

def run():
    print("--- STARTING DEBUG ---")
    
    # 1. Register
    print(f"\n1. Registering {EMAIL}...")
    try:
        r = requests.post(f"{BASE_URL}/register", json={
            "email": EMAIL,
            "password": PASSWORD,
            "password_confirm": PASSWORD,
            "first_name": "Debug",
            "last_name": "User",
            "phone": "9999999999"
        })
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Register failed: {e}")

    # 2. Login
    print(f"\n2. Logging in...")
    token = None
    try:
        r = requests.post(f"{BASE_URL}/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            # print(f"Token received: {token[:20]}...")
            print(f"Full Response Keys: {list(data.keys())}")
        else:
            print(f"Response: {r.text}")
            return
    except Exception as e:
        print(f"Login failed: {e}")
        return

    if not token:
        print("No token received!")
        return

    # 3. Call /me
    print(f"\n3. Calling /me with token...")
    try:
        r = requests.get(f"{BASE_URL}/me", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"/me request failed: {e}")

if __name__ == "__main__":
    run()
