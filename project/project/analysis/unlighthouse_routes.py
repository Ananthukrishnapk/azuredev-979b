import asyncio
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse

from infra.files import CONFIG


unlighthouse_script = CONFIG.paths.project_folder / "scripts/api/unlighthouse_api.js"

# Thread pool for running subprocess
_executor = ThreadPoolExecutor(max_workers=2)


@dataclass(frozen=True)
class LighthousePageArtifact:
    url: str
    timestamp: Optional[str]
    lighthouse_json: Path
    page_id: str
    page_name: str
    accessibility_score: int


def _run_unlighthouse_sync(url: str, run_id: str) -> tuple[int, str, str]:
    """
    Synchronous wrapper to run Unlighthouse via subprocess.
    Returns (returncode, stdout, stderr)
    """
    proc = subprocess.run(
        ["node", str(unlighthouse_script), url, run_id],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


async def run_unlighthouse(url: str, run_id: str) -> tuple[str, Path]:
    """
    Run Unlighthouse for a site and write artifacts into an isolated per-run folder.

    Returns:
      (domain, domain_path)
        - domain: netloc from the URL
        - domain_path: folder containing Unlighthouse output for this domain
    """
    loop = asyncio.get_event_loop()
    
    # Run subprocess in thread pool to avoid Windows async subprocess issues
    returncode, stdout, stderr = await loop.run_in_executor(
        _executor,
        _run_unlighthouse_sync,
        url,
        run_id
    )

    if returncode != 0:
        raise RuntimeError(f"Unlighthouse failed: {stderr}")

    domain = urlparse(url).netloc
    domain_path = CONFIG.paths.unlighthouse_reports / run_id / domain
    return domain, domain_path


def iter_lighthouse_json(domain_path: Path) -> Iterable[Path]:
    return domain_path.rglob("lighthouse.json")


def _stable_page_id_from_url(url: str) -> str:
    import hashlib

    return hashlib.md5(url.encode("utf-8")).hexdigest()[:8]


def collect_page_artifacts(domain_path: Path) -> list[LighthousePageArtifact]:
    pages: list[LighthousePageArtifact] = []
    for lh_file in iter_lighthouse_json(domain_path):
        try:
            data = json.loads(lh_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        final_url = data.get("finalUrl") or data.get("requestedUrl")
        if not final_url:
            continue

        ts = data.get("fetchTime")
        a11y_score = data.get("categories", {}).get("accessibility", {}).get("score")
        a11y_score_int = int(a11y_score * 100) if isinstance(a11y_score, (int, float)) else 0

        page_id = _stable_page_id_from_url(final_url)
        page_name = urlparse(final_url).path.strip("/").split("/")[-1] or "home"

        pages.append(
            LighthousePageArtifact(
                url=str(final_url),
                timestamp=ts,
                lighthouse_json=lh_file,
                page_id=page_id,
                page_name=page_name,
                accessibility_score=a11y_score_int,
            )
        )

    # Stable ordering for deterministic output
    pages.sort(key=lambda p: p.url)
    return pages


def cleanup_unlighthouse_run(run_id: str) -> None:
    run_path = CONFIG.paths.unlighthouse_reports / run_id
    if run_path.exists():
        shutil.rmtree(run_path, ignore_errors=True)

