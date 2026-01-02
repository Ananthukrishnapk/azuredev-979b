"""
Simple test endpoint to verify the API works without Playwright
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

router = APIRouter(prefix="/api", tags=["test"])

class URLRequest(BaseModel):
    url: HttpUrl

@router.post("/test-analyze")
async def test_analyze(request: URLRequest):
    """
    Simple test endpoint that returns mock data without using Playwright
    """
    url = str(request.url)
    
    # Return mock success data
    return {
        "success": True,
        "message": "Test analysis completed (without browser automation)",
        "data": {
            "results": {
                "seo": [
                    {
                        "name": "URL Accessible",
                        "status": "pass",
                        "description": f"URL {url} is accessible",
                        "message": "Basic connectivity test passed"
                    },
                    {
                        "name": "HTTPS Check",
                        "status": "pass" if url.startswith("https") else "fail",
                        "description": "Checking if site uses HTTPS",
                        "message": "HTTPS is recommended for security" if not url.startswith("https") else "Site uses HTTPS"
                    },
                    {
                        "name": "Domain Validation",
                        "status": "pass",
                        "description": "Domain name is valid",
                        "message": "Domain format is correct"
                    }
                ],
                "geo": [
                    {
                        "name": "URL Structure",
                        "status": "pass",
                        "description": "URL structure analysis",
                        "message": "URL structure is valid"
                    },
                    {
                        "name": "Protocol Check",
                        "status": "pass",
                        "description": "Checking URL protocol",
                        "message": f"Using {url.split(':')[0]} protocol"
                    }
                ],
                "aeo": [
                    {
                        "name": "Basic Validation",
                        "status": "pass",
                        "description": "Basic URL validation",
                        "message": "URL passes basic validation checks"
                    }
                ]
            },
            "page_type": "test"
        }
    }

@router.get("/health-test")
async def health_test():
    """Test health endpoint"""
    return {
        "status": "healthy",
        "message": "API is running (test mode - browser automation disabled)",
        "playwright_available": False
    }
