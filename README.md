# AAD-Protected FastAPI API

Secure a FastAPI endpoint with **Microsoft Entra ID** (Azure AD) and **MSAL**.  
Local-first, cloud-ready.

---

## 0. Prerequisites

| Tool | Purpose | Version |
|------|---------|---------|
| Python | runtime | 3.9 – 3.12 |
| Azure CLI | local token / deployment | ≥ 2.60 |
| Node optional | for `az webapp up` on Linux | pre-installed in Cloud Shell |

---

## 1. Directory layout

```text
aad-protected-api/
├── .env                 # tenant + app IDs (you edit)
├── requirements.txt     # server deps
├── server/
│   ├── app.py
│   └── __init__.py
└── client/
├── get_token.py
└── test_call.sh
````

---

## 2. One-time local setup

```bash
# clone / unzip project, then:
cd aad-protected-api

# 2.1 create isolated Python env
python -m venv .venv               # creates .venv folder
#-- Windows
.venv\Scripts\activate
#-- macOS / Linux / WSL
source .venv/bin/activate

# 2.2 install server dependencies
pip install -r requirements.txt
````

---

## 3. Azure AD Configuration

### 3.1 Create API Application Registration

1. Go to **Azure Portal** → **Microsoft Entra ID** → **App registrations** → **New registration**
2. Enter a name (e.g., "WhoamiAPI")
3. For **Supported account types**, select:
   - For single organization: "Accounts in this organizational directory only"
   - For multi-tenant: "Accounts in any organizational directory"
4. Leave Redirect URI blank for now
5. Click **Register**
6. Note the **Application (client) ID** - this will be your `API_APP_ID`
7. Note the **Directory (tenant) ID** - this will be your `AAD_TENANT_ID`

### 3.2 Expose an API

1. Select your API app ("WhoamiAPI")
2. Click **Expose an API** → **Add a scope**
3. For **Application ID URI**, use the default `api://[your-app-id]` and click **Save**
4. Click **Add a scope** and configure:
   - **Scope name**: `access_as_user`
   - **Admin consent display name**: "Access API as signed-in user"
   - **Admin consent description**: "Allows the app to access the API as the signed-in user"
   - **State**: Enabled
5. Click **Add scope**

### 3.3 Create Client Application Registration

1. Go to **Azure Portal** → **Microsoft Entra ID** → **App registrations** → **New registration**
2. Enter a name (e.g., "REST Clients")
3. For **Supported account types**, choose the same type as your API app
4. Set **Redirect URI** to:
   - Platform: "Public client/native (mobile & desktop)"
   - URI: `http://localhost`
5. Click **Register**
6. Note the **Application (client) ID** - this will be your `CLIENT_APP_ID`

### 3.4 Configure Client App Authentication

1. Select your client app ("REST Clients")
2. Navigate to **Authentication**
3. Under **Platform configurations**, select or add "Mobile and desktop applications"
4. Add the following redirect URIs:
   - `http://localhost`
   - `http://localhost:8080`
   - `https://login.microsoftonline.com/common/oauth2/nativeclient`
5. Under **Advanced settings**, set "Allow public client flows" to **Yes**
6. Click **Save**

### 3.5 Add API Permissions to Client App

1. Select your client app ("REST Clients")
2. Navigate to **API permissions** → **Add a permission**
3. Select **My APIs** and choose your API app ("WhoamiAPI")
4. Select the `access_as_user` scope
5. Click **Add permissions**
6. Click **Grant admin consent for [your-organization]**

### 3.6 (Optional) Configure for Multi-Tenant Usage

If you need to allow external users:

1. In your API app settings, go to **Authentication**
2. Set "Allow guest users" to **Yes**
3. In your server code, use `MultiTenantAzureAuthorizationCodeBearer` with `allow_guest_users=True`

---

## 4. Fill in `.env`

```ini
# ===== .env (sample) =====
AAD_TENANT_ID=<your-tenant-guid>
API_APP_ID=<server-app-client-id>
CLIENT_APP_ID=<desktop-app-client-id>
```

## 5. Testing the API

You'll need two terminal windows to test the API - one for the server and one for the client.

### 5.1 Start the FastAPI Server

```bash
# Terminal 1: Start the server
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

uvicorn server.app:app --reload
```

Wait until you see:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 5.2 Run the Client Tests

Open a second terminal and run:

```bash
# Terminal 2: Make sure you're in the project directory
cd aad-protected-api

# Activate the virtual environment in this terminal too!
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# Run the client - two options available:

# Option 1: Using azure-identity (recommended)
python client/get_token_identity.py

# Option 2: Using MSAL directly
python client/get_token_msal.py
```

### 5.3 Troubleshooting

If you get authentication errors:

1. **Check server logs** in the first terminal for detailed error messages
2. Ensure your virtual environment (`venv`) is active in **both terminals**
3. Verify your Azure AD app registrations are configured correctly (see section 3)
4. Make sure the server settings allow guest users if using a personal Microsoft account:

   ```python
   # in server/app.py
   azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
       # ...
       allow_guest_users=True  # Required for personal accounts
   )
   ```

### 5.4 Test the Health Endpoint

The API has an unauthenticated health endpoint you can use to verify it's running:

```bash
# Using curl
curl http://localhost:8000/health

# Using PowerShell
Invoke-RestMethod -Uri http://localhost:8000/health
```
