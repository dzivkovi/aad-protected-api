import os
import requests
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
import base64
import json

load_dotenv()

# This example uses service principal authentication
# No user context - the app authenticates as itself
# You'll need to add these to your .env file:
# SERVICE_PRINCIPAL_CLIENT_ID=<your-service-principal-client-id>
# SERVICE_PRINCIPAL_CLIENT_SECRET=<your-service-principal-secret>

# Check if service principal credentials are configured
if not os.getenv('SERVICE_PRINCIPAL_CLIENT_ID') or not os.getenv('SERVICE_PRINCIPAL_CLIENT_SECRET'):
    print("Service principal credentials not found in .env file")
    print("Please add:")
    print("  SERVICE_PRINCIPAL_CLIENT_ID=<your-service-principal-client-id>")
    print("  SERVICE_PRINCIPAL_CLIENT_SECRET=<your-service-principal-secret>")
    print("\nTo create a service principal:")
    print("  az ad sp create-for-rbac --name 'YourAppName' --sdk-auth")
    exit(1)

credential = ClientSecretCredential(
    tenant_id=os.getenv('AAD_TENANT_ID'),
    client_id=os.getenv('SERVICE_PRINCIPAL_CLIENT_ID'),
    client_secret=os.getenv('SERVICE_PRINCIPAL_CLIENT_SECRET')
)

# Note: For service principals, you typically use the default scope
# or configure specific application permissions in Azure AD
scope = f"api://{os.getenv('API_APP_ID')}/.default"
print(f"Requesting scope: {scope}")

try:
    token_result = credential.get_token(scope)
    token = token_result.token
    
    # Decode token to show app info
    payload = token.split('.')[1]
    payload += '=' * (4 - len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload)
    claims = json.loads(decoded)
    
    print(f"Authenticated as service principal: {claims.get('appid', 'Unknown')}")
    print(f"Application name: {claims.get('app_displayname', 'Unknown')}")
    print("Note: This is app-to-app authentication, not user authentication")
    
    # Make API request
    r = requests.get("http://localhost:8000/whoami", 
                     headers={"Authorization": f"Bearer {token}"})
    print(f"API Response: {r.json()}")
    
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Ensure your service principal has the required permissions")