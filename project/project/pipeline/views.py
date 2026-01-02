from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Any
from .constants import PageCategories


class DiscoveredPage(BaseModel):
    page_id: str
    page_name: str = "home"
    url: str
    timestamp: Optional[str] = None
    accessibility_score: int = 0


class PipelineResult(BaseModel):
    results: Dict[Any, List] = Field(default_factory=dict)
    page_type: PageCategories = PageCategories.OTHER

    @model_validator(mode="after")
    def ensure_all_analysers_present(self):
        from analysis.constants import ANALYSERS
        for analyser in ANALYSERS:
            self.results.setdefault(analyser, [])
        return self


class PreContext(BaseModel):
    page_type: PageCategories = PageCategories.OTHER
    # Shared Unlighthouse artifacts for the whole scan run.
    unlighthouse_run_id: Optional[str] = None
    unlighthouse_domain: Optional[str] = None
    unlighthouse_domain_path: Optional[str] = None
    discovered_pages: List[DiscoveredPage] = Field(default_factory=list)
