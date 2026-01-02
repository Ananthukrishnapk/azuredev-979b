import sys
import asyncio
from pathlib import Path

# Fix for Windows asyncio subprocess support - MUST be before any asyncio imports
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Add project directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routers import analyze_router

app = FastAPI(
    title="SEO-GEO-AEO API",
    description="Standalone API for SEO, GEO, and AEO website analysis",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router)


@app.get("/")
async def root():
    return {
        "service": "SEO-GEO-AEO API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "health": "GET /api/health",
        }
    }


if __name__ == "__main__":
    import uvicorn
    # Run without reload to properly use the event loop policy
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
