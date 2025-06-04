import os, requests
from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential
import base64
import json

load_dotenv()

credential = InteractiveBrowserCredential(
    tenant_id=os.getenv('AAD_TENANT_ID'),
    client_id=os.getenv('CLIENT_APP_ID'),
    allow_guest_users=True
)

scope = f"api://{os.getenv('API_APP_ID')}/access_as_user"
print(f"Requesting scope: {scope}")

token_result = credential.get_token(scope)
token = token_result.token

# Debug: Print ALL token claims
payload = token.split('.')[1]
payload += '=' * (4 - len(payload) % 4)
decoded = base64.urlsafe_b64decode(payload)
claims = json.loads(decoded)

print(f"Token audience (aud): {claims.get('aud')}")
print(f"Token scope (scp): {claims.get('scp')}")
print(f"Token issuer (iss): {claims.get('iss')}")
print(f"Token tenant (tid): {claims.get('tid')}")
print(f"User type (userType): {claims.get('userType')}")
print(f"All claims: {json.dumps(claims, indent=2)}")

r = requests.get("http://localhost:8000/whoami", headers={"Authorization": f"Bearer {token}"})
print(f"API Response: {r.json()}")
