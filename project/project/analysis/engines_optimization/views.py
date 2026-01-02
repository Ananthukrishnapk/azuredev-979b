from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class EOCheckResult(BaseModel):
    id: int
    type: str  # "SEO" | "AEO" | "GEO"
    category: str
    check_item: str
    what_to_verify: str
    impact: str  # "Critical" | "High" | "Medium" | "Low"
    status: str  # "pass" | "fail" | "warn"
    details: str
    evidence: Dict[str, Any] = Field(default_factory=dict)


class EOPageResult(BaseModel):
    page_id: str
    page_name: str = "home"
    url: Optional[str] = None
    timestamp: Optional[str] = None
    checks: List[EOCheckResult] = Field(default_factory=list)


