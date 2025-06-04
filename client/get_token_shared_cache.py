import os
import requests
from dotenv import load_dotenv
from azure.identity import SharedTokenCacheCredential, ChainedTokenCredential, AzureCliCredential
import base64
import json

load_dotenv()

# This uses tokens from Visual Studio, VS Code, or other Microsoft developer tools
# No browser popup required if already authenticated in these tools
try:
    # Try shared token cache first (from VS/VS Code)
    credential = SharedTokenCacheCredential()
    print("Using SharedTokenCacheCredential (from VS/VS Code)")
except Exception:
    # Fall back to Azure CLI if available
    try:
        credential = AzureCliCredential()
        print("Using AzureCliCredential (from 'az login')")
    except Exception:
        print("No cached credentials found. Please authenticate via:")
        print("  - Visual Studio / VS Code")
        print("  - Azure CLI: 'az login --use-device-code'")
        exit(1)

scope = f"api://{os.getenv('API_APP_ID')}/access_as_user"
print(f"Requesting scope: {scope}")

try:
    token_result = credential.get_token(scope)
    token = token_result.token
    
    # Decode token to show user info
    payload = token.split('.')[1]
    payload += '=' * (4 - len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload)
    claims = json.loads(decoded)
    
    print(f"Authenticated as: {claims.get('name', 'Unknown')} ({claims.get('preferred_username', 'No email')})")
    print(f"Token acquired from cached credentials - no browser popup!")
    
    # Make API request
    r = requests.get("http://localhost:8000/whoami", 
                     headers={"Authorization": f"Bearer {token}"})
    print(f"API Response: {r.json()}")
    
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Please ensure you're authenticated in VS/VS Code or Azure CLI")