from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from pipeline.service import Pipeline

router = APIRouter(prefix="/api", tags=["Analysis"])


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_url(request: AnalyzeRequest):
    """
    Analyze a URL for SEO, GEO, and AEO metrics.
    
    This endpoint:
    1. Crawls the website using Unlighthouse to discover all pages
    2. Runs SEO analysis (GSC checks, Safe Browsing, Spam protection)
    3. Runs GEO analysis (Factual accuracy, Transparent intent, AI spam, Cloaking)
    4. Runs AEO analysis (Factual accuracy, EEAT/No misleading claims)
    
    Returns analysis results for all discovered pages.
    """
    try:
        pipeline = Pipeline(url=str(request.url))
        result = await pipeline.run()
        
        return AnalyzeResponse(
            success=True,
            message="Analysis completed successfully",
            data=result.model_dump()
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SEO-GEO-AEO-API"}
