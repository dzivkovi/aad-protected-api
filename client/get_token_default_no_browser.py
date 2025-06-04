import os
import requests
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
import base64
import json

load_dotenv()

# DefaultAzureCredential with browser authentication disabled
# This will try multiple authentication methods in order:
# 1. Environment variables (service principal)
# 2. Managed Identity (if running in Azure)
# 3. Visual Studio / VS Code shared cache
# 4. Azure CLI
# 5. Azure PowerShell
# But NOT interactive browser

credential = DefaultAzureCredential(
    exclude_interactive_browser_credential=True,
    exclude_visual_studio_code_credential=False,
    exclude_azure_cli_credential=False,
    exclude_powershell_credential=False,
    exclude_shared_token_cache_credential=False
)

scope = f"api://{os.getenv('API_APP_ID')}/access_as_user"
print(f"Requesting scope: {scope}")
print("Trying authentication methods (no browser)...")

try:
    token_result = credential.get_token(scope)
    token = token_result.token
    
    # Decode token to show user/app info
    payload = token.split('.')[1]
    payload += '=' * (4 - len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload)
    claims = json.loads(decoded)
    
    # Check if it's a user or app token
    if 'preferred_username' in claims:
        print(f"Authenticated as user: {claims.get('name', 'Unknown')} ({claims.get('preferred_username')})")
    else:
        print(f"Authenticated as app: {claims.get('appid', 'Unknown')}")
    
    print("Token acquired without browser popup!")
    
    # Make API request
    r = requests.get("http://localhost:8000/whoami", 
                     headers={"Authorization": f"Bearer {token}"})
    print(f"API Response: {r.json()}")
    
except Exception as e:
    print(f"Authentication failed: {e}")
    print("\nTo authenticate without browser, try one of these:")
    print("1. Azure CLI: 'az login --use-device-code'")
    print("2. Set up service principal environment variables")
    print("3. Authenticate in Visual Studio or VS Code")
    print("4. Use PowerShell: 'Connect-AzAccount'")