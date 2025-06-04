import msal
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

# Set up MSAL authentication
AUTH = f"https://login.microsoftonline.com/{os.getenv('AAD_TENANT_ID')}"
SCOPE = [f"api://{os.getenv('API_APP_ID')}/access_as_user"]
print(f"Requesting scope: {SCOPE[0]}")

# Create a client application
app = msal.PublicClientApplication(
    client_id=os.getenv("CLIENT_APP_ID"),
    authority=AUTH
)

# Try to get token silently first (from cache)
accounts = app.get_accounts()
result = None
if accounts:
    # Use the first cached account
    account = accounts[0]
    print(f"Using cached account: {account.get('username')}")
    result = app.acquire_token_silent(SCOPE, account=account)

# If silent acquisition fails, fall back to interactive login
if not result:
    print("No suitable token in cache, getting a new one via browser...")
    result = app.acquire_token_interactive(SCOPE)

# Check if we got a token
if "access_token" in result:
    token = result["access_token"]
    
    # Debug: Print some token info
    print("Token acquired successfully!")
    
    # Optional: Extract user information from token
    claims = result.get("id_token_claims", {})
    if claims:
        print(f"Authenticated as: {claims.get('name', 'Unknown')} ({claims.get('preferred_username', 'No email')})")

    # Make API request with token
    r = requests.get("http://localhost:8000/whoami", 
                     headers={"Authorization": f"Bearer {token}"})
    print(f"API Response: {r.json()}")
else:
    print(f"Failed to acquire token: {result.get('error')}")
    print(f"Error description: {result.get('error_description')}")