import os
from pathlib import Path

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Temporary uploads folder
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# CORS configuration for future React/Vite frontends
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# API Configuration
PROJECT_NAME = "Sahayak Verification Engine"
VERSION = "0.1.0"
API_PREFIX = "/api"

# AI Key (to be configured in Step 2)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
