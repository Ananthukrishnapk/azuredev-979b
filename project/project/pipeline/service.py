# ===== MAIN PIPELINE FOR SEO/GEO/AEO ANALYSIS ===== #

from analysis import (
    BaseAnalyser,
    SeoAnalyzer,
    GeoAnalyzer,
    AeoAnalyzer,
)
from playwright.async_api import async_playwright
from typing import Any, List, Type
from .views import PipelineResult, PreContext, DiscoveredPage
from playwright.async_api import Browser
from typing import Dict
import asyncio
import json
import uuid

from analysis.unlighthouse_routes import run_unlighthouse, collect_page_artifacts, cleanup_unlighthouse_run


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert any non-JSON-serializable objects to strings.
    This prevents PydanticSerializationError from Playwright Error objects
    or other complex types embedded in the data.
    """
    if obj is None:
        return None
    if isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    if hasattr(obj, "model_dump"):
        return sanitize_for_json(obj.model_dump())
    if hasattr(obj, "__dict__"):
        return sanitize_for_json(obj.__dict__)
    return str(obj)


class Pipeline:
    def __init__(self, url: str, external_analyzers: List[BaseAnalyser] = []):
        self.url = url
        self.external_analyzers = external_analyzers

    async def parallel_run_analysers(self, analysers: list[Type[BaseAnalyser]], browser: Browser, pre_context: PreContext) -> list:

        async def run_single_analyser(analyser: Type[BaseAnalyser]):
            # Get the analyzer name from the CLASS (not instance) for safe error handling
            analyzer_name = getattr(analyser, 'name', str(analyser.__name__))
            
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720}
            )

            page = await context.new_page()
            cdp_session = await context.new_cdp_session(page)
            result = []  # Default to empty list

            try:
                _analyser = analyser(
                    url=self.url,
                    page=page,
                    pre_context=pre_context,
                    context=context,
                    cdp_session=cdp_session,
                )
                result = await _analyser.scan()
                analyzer_name = getattr(_analyser, "name", analyzer_name)
            except Exception as e:
                print(f"Analyzer {analyzer_name} failed: {e}")
                import traceback
                traceback.print_exc()
                result = []
            finally:
                await context.close()

            return {analyzer_name: result}

        res = await asyncio.gather(
            *(run_single_analyser(a) for a in analysers),
            return_exceptions=False
        )

        return res

    async def run(self) -> PipelineResult:
        """Runs SEO/GEO/AEO analysers and outputs as {analyser_name: list_of_results}"""

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            pre_context = PreContext()
            global_context = await browser.new_context()
            results: List[Dict] = []
            run_id: str | None = None
            try:
                global_page = await global_context.new_page()

                await global_page.goto(self.url, timeout=60000)
                await global_page.wait_for_load_state("networkidle")

                pre_context = PreContext()

                # Run Unlighthouse ONCE and share discovered pages with all analysers.
                run_id = uuid.uuid4().hex
                domain, domain_path = await run_unlighthouse(self.url, run_id)
                artifacts = collect_page_artifacts(domain_path)
                pre_context.unlighthouse_run_id = run_id
                pre_context.unlighthouse_domain = domain
                pre_context.unlighthouse_domain_path = str(domain_path)
                pre_context.discovered_pages = [
                    DiscoveredPage(
                        page_id=a.page_id,
                        page_name=a.page_name,
                        url=a.url,
                        timestamp=a.timestamp,
                        accessibility_score=a.accessibility_score,
                    )
                    for a in artifacts
                ]

                results = await self.parallel_run_analysers(
                    analysers=[
                        SeoAnalyzer,
                        AeoAnalyzer,
                        GeoAnalyzer,
                    ],
                    browser=browser,
                    pre_context=pre_context
                )
            finally:
                await global_context.close()
                await browser.close()
                if run_id:
                    cleanup_unlighthouse_run(run_id)

        result = {}
        for r in results:
            for k, v in r.items():
                # Sanitize each analyzer's results to ensure JSON serializability
                result[k] = sanitize_for_json(v)

        result = PipelineResult(results=result, page_type=pre_context.page_type)
        print(result)
        with open('temp.result.json', 'w', encoding='utf-8') as f:
            f.write(result.model_copy().model_dump_json(indent=2))
            
        return result
