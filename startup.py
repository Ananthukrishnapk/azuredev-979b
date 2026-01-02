"""
Startup script for Azure App Service
This file should be at the root of your repository
"""
import sys
from pathlib import Path

# Add project directories to Python path
project_path = Path(__file__).parent / "project" / "project"
sys.path.insert(0, str(project_path))

# Import and run the FastAPI app
from main import app

# This is what uvicorn will import
__all__ = ["app"]
