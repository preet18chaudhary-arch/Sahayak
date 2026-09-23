from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.config import CORS_ORIGINS, PROJECT_NAME, VERSION

# Initialize FastAPI application
app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description=(
        "Sahayak: AI-assisted scholarship document verification platform.\n\n"
        "Follows the **INPUT → UNDERSTAND → VERIFY → ACT** paradigm with "
        "human-in-the-loop confirmation, policy-driven verification rules, and "
        "comprehensive consistency checks."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development and future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core API routes
app.include_router(api_router)


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Returns backend operational status and service metadata.",
)
async def health_check():
    """Verify that the FastAPI service is running normally."""
    return {
        "status": "healthy",
        "app": PROJECT_NAME,
        "version": VERSION,
        "message": "Sahayak backend foundation is operational.",
    }


@app.get(
    "/",
    tags=["System"],
    summary="Root landing",
    description="Welcome page and API pointer.",
)
async def root():
    """Landing route pointing to interactive documentation."""
    return {
        "message": f"Welcome to {PROJECT_NAME} API v{VERSION}",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "scholarships": "/api/scholarships",
            "create_session": "/api/sessions/create",
        },
    }
