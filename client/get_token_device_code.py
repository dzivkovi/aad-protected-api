import os
import requests
from dotenv import load_dotenv
from azure.identity import DeviceCodeCredential
import base64
import json

load_dotenv()

# Device code flow - user authenticates on another device
# Useful for SSH sessions, containers, or machines without browsers
credential = DeviceCodeCredential(
    tenant_id=os.getenv('AAD_TENANT_ID'),
    client_id=os.getenv('CLIENT_APP_ID'),
    # This callback is called when device code is ready
    prompt_callback=lambda verification_uri, user_code, expires_on: print(
        f"\nTo authenticate, visit:\n{verification_uri}\n"
        f"And enter code: {user_code}\n"
        f"Code expires at: {expires_on}\n"
    )
)

scope = f"api://{os.getenv('API_APP_ID')}/access_as_user"
print(f"Requesting scope: {scope}")

try:
    # This will display the device code and wait for user authentication
    token_result = credential.get_token(scope)
    token = token_result.token
    
    # Decode token to show user info
    payload = token.split('.')[1]
    payload += '=' * (4 - len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload)
    claims = json.loads(decoded)
    
    print(f"\nAuthenticated as: {claims.get('name', 'Unknown')} ({claims.get('preferred_username', 'No email')})")
    
    # Make API request
    r = requests.get("http://localhost:8000/whoami", 
                     headers={"Authorization": f"Bearer {token}"})
    print(f"API Response: {r.json()}")
    
except Exception as e:
    print(f"Authentication failed: {e}")