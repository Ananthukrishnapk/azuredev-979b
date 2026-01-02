from __future__ import annotations

import asyncio
from difflib import SequenceMatcher
from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx

from analysis.constants import ANALYSERS
from analysis.views import BaseAnalyser
from analysis.engines_optimization.views import EOCheckResult, EOPageResult
from analysis.engines_optimization.common import (
    DEFAULT_UA,
    GOOGLEBOT_UA,
    extract_from_html,
    split_internal_external_links,
    detect_hidden_link_patterns,
    count_keyword_matches,
    keyword_stuffing_score,
    text_hash,
    normalize_text,
    SPAM_KEYWORDS,
    BAIT_PHRASES,
    DISCLOSURE_KEYWORDS,
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
    }


async def _fetch_pair(client: httpx.AsyncClient, url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    r_user = await client.get(url, follow_redirects=True, timeout=20, headers={"user-agent": DEFAULT_UA})
    r_bot = await client.get(url, follow_redirects=True, timeout=20, headers={"user-agent": GOOGLEBOT_UA})
    return (
        {"final_url": str(r_user.url), "status": r_user.status_code, "html": r_user.text or ""},
        {"final_url": str(r_bot.url), "status": r_bot.status_code, "html": r_bot.text or ""},
    )


def _similarity(a: str, b: str) -> float:
    a = normalize_text(a)[:10000]
    b = normalize_text(b)[:10000]
    if not a and not b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


class GeoAnalyzer(BaseAnalyser):
    name = ANALYSERS.GEN_EO

    async def scan(self) -> List[Dict[str, Any]]:
        discovered = self.pre_context.discovered_pages or []
        root_url = self.url
        domain = urlparse(root_url).netloc
        discovered_urls = [p.url for p in discovered]
        identity = _site_identity_signals(discovered_urls)

        # Fetch all pages once (normal UA) for global heuristics (duplicates, thin content).
        # Limit to avoid runaway scans.
        targets = discovered[:50]
        sem = asyncio.Semaphore(6)
        page_html: dict[str, str] = {}
        page_text_hash: dict[str, str] = {}
        page_text_len: dict[str, int] = {}

        async with httpx.AsyncClient() as client:
            async def fetch_one(p):
                async with sem:
                    r = await client.get(p.url, follow_redirects=True, timeout=20, headers={"user-agent": DEFAULT_UA})
                    html = r.text or ""
                    extracted = extract_from_html(html)
                    text = extracted.get("text", "") or ""
                    page_html[p.url] = html
                    page_text_hash[p.url] = text_hash(text)
                    page_text_len[p.url] = len(normalize_text(text))

            await asyncio.gather(*(fetch_one(p) for p in targets), return_exceptions=True)

            # Duplicate clusters by hash
            from collections import defaultdict
            clusters: dict[str, list[str]] = defaultdict(list)
            for u, h in page_text_hash.items():
                clusters[h].append(u)
            dup_urls = {u for h, urls in clusters.items() if len(urls) >= 3 for u in urls}

            results: List[Dict[str, Any]] = []
            for p in targets:
                html = page_html.get(p.url, "")
                extracted = extract_from_html(html)
                text = extracted.get("text", "") or ""
                links = extracted.get("links") or []
                _internal, external = split_internal_external_links(links, domain)
                citations = len(external)
                dates = extracted.get("dates") or []
                author = extracted.get("author")
                t_norm = normalize_text(text)

                # 7) GEO Trust - Factual accuracy (proxy)
                has_date = len(dates) > 0
                has_author = bool(author)
                has_citations = citations > 0
                text_len = page_text_len.get(p.url, 0)
                if has_date and has_author and has_citations and text_len > 400:
                    s7, d7 = "pass", "Has author + date + outbound references (verifiability proxies)."
                elif text_len < 200:
                    s7, d7 = "fail", "Very thin content; cannot be considered verifiable/current (heuristic)."
                else:
                    s7, d7 = "warn", "Cannot confirm factual accuracy deterministically; proxies are incomplete."

                check7 = EOCheckResult(
                    id=7,
                    type="GEO",
                    category="Trust",
                    check_item="Factual accuracy",
                    what_to_verify="Content is verifiable and current",
                    impact="Critical",
                    status=s7,
                    details=d7,
                    evidence={"author": author, "dates": dates[:5], "outbound_citations": citations, "text_length": text_len},
                )

                # 8) GEO Trust - Transparent intent (proxy)
                disclosures = [k for k in DISCLOSURE_KEYWORDS if k in t_norm]
                if identity["has_about"] and identity["has_contact"] and identity["has_privacy"]:
                    s8, d8 = "pass", "Site identity pages present (about/contact/privacy)."
                else:
                    s8, d8 = "warn", "Transparent intent cannot be validated automatically; identity signals incomplete."
                check8 = EOCheckResult(
                    id=8,
                    type="GEO",
                    category="Trust",
                    check_item="Transparent intent",
                    what_to_verify="No misleading or deceptive framing",
                    impact="Critical",
                    status=s8,
                    details=d8,
                    evidence={"site_identity": identity, "disclosure_keywords_found": disclosures[:10]},
                )

                # 9) GEO Risk - No AI spam (heuristics for low-quality/auto-gen)
                hidden_hits = detect_hidden_link_patterns(html)
                spam_kw = count_keyword_matches(text, SPAM_KEYWORDS)
                stuff = keyword_stuffing_score(text)
                in_dup_cluster = p.url in dup_urls
                thin = text_len < 200

                if in_dup_cluster or thin or hidden_hits > 5 or (stuff.get("suspect") is True) or len(spam_kw) > 0:
                    # Fail if strong combination, else warn
                    strong = thin and (in_dup_cluster or hidden_hits > 5 or len(spam_kw) > 0)
                    s9 = "fail" if strong else "warn"
                    d9 = "Heuristic signals suggest auto-generated/low-quality or spam-like content."
                else:
                    s9, d9 = "pass", "No strong low-quality/auto-generated heuristics detected."

                check9 = EOCheckResult(
                    id=9,
                    type="GEO",
                    category="Risk",
                    check_item="No AI spam",
                    what_to_verify="No auto-generated low-quality content",
                    impact="Critical",
                    status=s9,
                    details=d9,
                    evidence={
                        "thin_content": thin,
                        "text_length": text_len,
                        "duplicate_cluster": in_dup_cluster,
                        "hidden_pattern_hits": hidden_hits,
                        "spam_keywords": spam_kw,
                        "keyword_stuffing": stuff,
                    },
                )

                # 10) GEO Risk - No hallucination bait (phrase heuristics)
                bait = [b for b in BAIT_PHRASES if b in t_norm]
                if bait:
                    s10 = "warn"
                    d10 = f"Found {len(bait)} potential bait phrase(s); manual review recommended."
                else:
                    s10 = "pass"
                    d10 = "No common bait phrases detected (heuristic)."
                check10 = EOCheckResult(
                    id=10,
                    type="GEO",
                    category="Risk",
                    check_item="No hallucination bait",
                    what_to_verify="Avoid speculative or false claims",
                    impact="Critical",
                    status=s10,
                    details=d10,
                    evidence={"matched_phrases": bait},
                )

                # 11) GEO Risk - No cloaking (compare normal vs bot fetch)
                try:
                    user_v, bot_v = await _fetch_pair(client, p.url)
                    user_ex = extract_from_html(user_v["html"])
                    bot_ex = extract_from_html(bot_v["html"])
                    sim = _similarity(user_ex.get("text", ""), bot_ex.get("text", ""))

                    major_mismatch = (
                        user_v["status"] != bot_v["status"]
                        or user_v["final_url"] != bot_v["final_url"]
                        or sim < 0.85
                    )
                    minor_mismatch = sim < 0.95

                    if major_mismatch:
                        s11 = "fail"
                        d11 = "Detected major difference between user vs bot content (possible cloaking)."
                    elif minor_mismatch:
                        s11 = "warn"
                        d11 = "Detected minor differences between user vs bot content (review recommended)."
                    else:
                        s11 = "pass"
                        d11 = "User vs bot content appears consistent (heuristic)."

                    check11 = EOCheckResult(
                        id=11,
                        type="GEO",
                        category="Risk",
                        check_item="No cloaking",
                        what_to_verify="Same content for users & bots",
                        impact="Critical",
                        status=s11,
                        details=d11,
                        evidence={
                            "user": {"status": user_v["status"], "final_url": user_v["final_url"], "title": user_ex.get("title"), "canonical": user_ex.get("canonical")},
                            "bot": {"status": bot_v["status"], "final_url": bot_v["final_url"], "title": bot_ex.get("title"), "canonical": bot_ex.get("canonical")},
                            "text_similarity": sim,
                            "user_text_hash": text_hash(user_ex.get("text", "")),
                            "bot_text_hash": text_hash(bot_ex.get("text", "")),
                        },
                    )
                except Exception as e:
                    check11 = EOCheckResult(
                        id=11,
                        type="GEO",
                        category="Risk",
                        check_item="No cloaking",
                        what_to_verify="Same content for users & bots",
                        impact="Critical",
                        status="warn",
                        details=f"Cloaking check failed: {str(e)}",
                        evidence={},
                    )

                results.append(
                    EOPageResult(
                        page_id=p.page_id,
                        page_name=p.page_name,
                        url=p.url,
                        timestamp=p.timestamp,
                        checks=[check7, check8, check9, check10, check11],
                    ).model_dump()
                )

        return results



