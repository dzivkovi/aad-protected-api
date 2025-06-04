import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Security, Request
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Log environment variables (safely)
logger.info("=== Azure AD Configuration ===")
logger.info("AAD_TENANT_ID: %s", os.getenv("AAD_TENANT_ID"))
logger.info("API_APP_ID: %s", os.getenv("API_APP_ID"))
logger.info("CLIENT_APP_ID: %s", os.getenv("CLIENT_APP_ID"))

# Log the scope being configured
api_scope = f"api://{os.getenv('API_APP_ID')}/access_as_user"
logger.info("Configured API scope: %s", api_scope)

azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
    app_client_id=os.getenv("API_APP_ID"),
    scopes={api_scope: "access_as_user"},
    validate_iss=False,  # Disable for now
    allow_guest_users=False,  # Start secure
)

logger.info("Azure authentication scheme initialized successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=== API Server Starting ===")
    logger.info("Server is ready to accept requests")
    yield
    # Shutdown (if needed)
    logger.info("=== API Server Shutting Down ===")


app = FastAPI(title="Azure AD Protected API", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log incoming requests
    logger.info("Incoming request: %s %s", request.method, request.url.path)

    # Log authorization header (safely - just presence, not content)
    auth_header = request.headers.get("authorization")
    if auth_header:
        logger.info("Authorization header present in request")
    else:
        logger.warning("No authorization header in request")

    response = await call_next(request)

    # Log response status
    logger.info("Response status: %s", response.status_code)
    return response


@app.get("/whoami")
async def whoami(user=Security(azure_scheme)):
    logger.info("Authenticated user: %s (OID: %s)", user.email, user.oid)
    logger.info("User name: %s", user.name)

    return {
        "message": "Authentication successful",
        "user_id": user.oid,
        "name": user.name,
        "email": user.email,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint that doesn't require authentication"""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "version": "1.0.0",
        # Remove sensitive information
        # "api_app_id": os.getenv("API_APP_ID"),
        # "configured_scope": api_scope
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s: %s", request.method, request.url.path, str(exc)
    )
    return {"detail": "Internal server error", "path": str(request.url.path)}
