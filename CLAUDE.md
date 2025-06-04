# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Azure AD protected FastAPI REST API demonstration project with Python clients showing how to authenticate and call protected endpoints.

## Common Development Commands

### Server Operations
```bash
# Start the FastAPI server
uvicorn server.app:app --reload

# Server runs on http://127.0.0.1:8000
```

### Client Testing

#### Browser-based Authentication
```bash
# Test with azure-identity (opens browser)
python client/get_token_identity.py

# Test with MSAL (opens browser)
python client/get_token_msal.py
```

#### Non-Browser Authentication Options
```bash
# Use cached credentials from VS/VS Code or Azure CLI
python client/get_token_shared_cache.py

# Use device code flow (authenticate on another device)
python client/get_token_device_code.py

# Use DefaultAzureCredential without browser
python client/get_token_default_no_browser.py

# Use service principal (app-only, no user context)
python client/get_token_service_principal.py
```

### Code Quality
```bash
# Run linters
flake8
pylint server/ client/
```

## Architecture

### Server (`server/app.py`)
- FastAPI application with Azure AD authentication via `fastapi-azure-auth`
- Endpoints:
  - `/whoami` - Protected endpoint requiring bearer token
  - `/health` - Unprotected health check
- Multi-tenant support with configurable guest user access
- Request/response logging middleware

### Client (`client/`)
- Two authentication methods: `azure-identity` (recommended) and MSAL
- Interactive browser-based authentication flow
- Demonstrates token acquisition and API calls

### Configuration
- Uses environment variables via `.env` file
- Required variables: `AAD_TENANT_ID`, `API_APP_ID`, `CLIENT_APP_ID`
- Copy `env.sample` to `.env` and populate with Azure AD app registrations

### Key Dependencies
- `fastapi==0.110.0` - Web framework
- `fastapi-azure-auth>=4.4` - Azure AD integration
- `azure-identity>=1.15.0` - Azure authentication
- `msal==1.32.3` - Microsoft Authentication Library

## Important Notes
- Requires Azure AD app registrations setup (see README.md sections 3.1-3.6)
- Python 3.9-3.12 and Azure CLI ≥ 2.60 required
- Use virtual environments for isolation
- Two terminals needed for testing (server + client)