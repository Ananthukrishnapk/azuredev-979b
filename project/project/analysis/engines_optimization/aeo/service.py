from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx

from analysis.constants import ANALYSERS
from analysis.views import BaseAnalyser
from analysis.engines_optimization.views import EOCheckResult, EOPageResult
from analysis.engines_optimization.common import (
    extract_from_html,
    split_internal_external_links,
    DISCLOSURE_KEYWORDS,
    normalize_text,
)


def _site_identity_signals(urls: list[str]) -> dict[str, bool]:
    u = [urlparse(x).path.lower() for x in urls]
    def has_any(keys: list[str]) -> bool:
        return any(any(k in p for k in keys) for p in u)
    return {
        "has_about": has_any(["/about"]),
        "has_contact": has_any(["/contact"]),
        "has_privacy": has_any(["/privacy"]),
        "has_terms": has_any(["/terms"]),
        "has_refund": has_any(["refund", "return", "returns", "shipping"]),
    }


class AeoAnalyzer(BaseAnalyser):
    name = ANALYSERS.AI_EO

    async def scan(self) -> List[Dict[str, Any]]:
        discovered = self.pre_context.discovered_pages or []
        root_url = self.url
        domain = urlparse(root_url).netloc
        discovered_urls = [p.url for p in discovered]
        identity = _site_identity_signals(discovered_urls)

        results: List[Dict[str, Any]] = []
        async with httpx.AsyncClient() as client:
            for p in discovered[:50]:
                try:
                    r = await client.get(p.url, follow_redirects=True, timeout=20, headers={"user-agent": "site360"})
                    html = r.text or ""
                    extracted = extract_from_html(html)
                    text = extracted.get("text", "") or ""
                    title = extracted.get("title")
                    author = extracted.get("author")
                    dates = extracted.get("dates") or []
                    links = extracted.get("links") or []
                    _internal, external = split_internal_external_links(links, domain)
                    citations = len(external)

                    # ---- Check 5: Factual accuracy (proxy) ----
                    # Proxy: presence of dates + author + at least one external citation.
                    has_date = len(dates) > 0
                    has_author = bool(author)
                    has_citations = citations > 0
                    text_len = len(normalize_text(text))

                    if has_date and has_author and has_citations and text_len > 400:
                        s5, d5 = "pass", "Has author + date + outbound references (verifiability proxies)."
                    elif text_len < 200:
                        s5, d5 = "fail", "Very thin content; cannot be considered verifiable (heuristic)."
                    else:
                        s5, d5 = "warn", "Cannot confirm factual accuracy without human review; proxies are incomplete."

                    check5 = EOCheckResult(
                        id=5,
                        type="AEO",
                        category="Content",
                        check_item="Factual accuracy",
                        what_to_verify="Content is verifiable and up to date",
                        impact="Critical",
                        status=s5,
                        details=d5,
                        evidence={
                            "title": title,
                            "author": author,
                            "dates": dates[:5],
                            "outbound_citations": citations,
                            "text_length": text_len,
                            "site_identity": identity,
                        },
                    )

                    # ---- Check 6: EEAT / No misleading claims (proxy) ----
                    # Proxy: identity pages exist + disclosure language not suspiciously absent when monetization signals exist.
                    t_norm = normalize_text(text)
                    disclosures = [k for k in DISCLOSURE_KEYWORDS if k in t_norm]

                    if identity["has_about"] and identity["has_contact"] and identity["has_privacy"]:
                        s6 = "pass"
                        d6 = "Strong site identity signals present (about/contact/privacy)."
                    else:
                        s6 = "warn"
                        d6 = "Cannot validate 'no misleading claims' automatically; site identity/disclosure signals incomplete."

                    check6 = EOCheckResult(
                        id=6,
                        type="AEO",
                        category="EEAT",
                        check_item="No misleading claims",
                        what_to_verify="Content aligns with facts",
                        impact="Critical",
                        status=s6,
                        details=d6,
                        evidence={
                            "site_identity": identity,
                            "disclosure_keywords_found": disclosures[:10],
                        },
                    )

                    results.append(
                        EOPageResult(
                            page_id=p.page_id,
                            page_name=p.page_name,
                            url=p.url,
                            timestamp=p.timestamp,
                            checks=[check5, check6],
                        ).model_dump()
                    )
                except Exception as e:
                    results.append(
                        EOPageResult(
                            page_id=p.page_id,
                            page_name=p.page_name,
                            url=p.url,
                            timestamp=p.timestamp,
                            checks=[
                                EOCheckResult(
                                    id=5,
                                    type="AEO",
                                    category="Content",
                                    check_item="Factual accuracy",
                                    what_to_verify="Content is verifiable and up to date",
                                    impact="Critical",
                                    status="warn",
                                    details=f"Failed to fetch/analyze page: {str(e)}",
                                    evidence={},
                                ),
                                EOCheckResult(
                                    id=6,
                                    type="AEO",
                                    category="EEAT",
                                    check_item="No misleading claims",
                                    what_to_verify="Content aligns with facts",
                                    impact="Critical",
                                    status="warn",
                                    details=f"Failed to fetch/analyze page: {str(e)}",
                                    evidence={},
                                ),
                            ],
                        ).model_dump()
                    )

        return results



