from __future__ import annotations

import os
from typing import Any, Dict, List
from urllib.parse import urlparse

from analysis.views import BaseAnalyser
from analysis.constants import ANALYSERS
from analysis.engines_optimization.views import EOCheckResult, EOPageResult
from analysis.engines_optimization.common import (
    safe_browsing_check,
    gsc_get_access_token,
    gsc_fetch,
    extract_from_html,
    split_internal_external_links,
    detect_hidden_link_patterns,
    count_keyword_matches,
    SPAM_KEYWORDS,
)
import httpx


class SeoAnalyzer(BaseAnalyser):
    name = ANALYSERS.SEARCH_EO

    async def scan(self) -> List[Dict[str, Any]]:
        discovered = self.pre_context.discovered_pages or []
        root_url = self.url
        domain = urlparse(root_url).netloc

        # ---- GSC checks (site-level) ----
        gsc_site_url = os.getenv("GSC_SITE_URL") or root_url
        gsc_client_id = os.getenv("GSC_CLIENT_ID")
        gsc_client_secret = os.getenv("GSC_CLIENT_SECRET")
        gsc_refresh_token = os.getenv("GSC_REFRESH_TOKEN")

        manual_actions_check = EOCheckResult(
            id=1,
            type="SEO",
            category="GSC",
            check_item="Manual actions",
            what_to_verify="No penalties",
            impact="Critical",
            status="warn",
            details="GSC not configured; cannot verify manual actions.",
            evidence={},
        )
        security_issues_check = EOCheckResult(
            id=2,
            type="SEO",
            category="GSC",
            check_item="Security issues",
            what_to_verify="No malware/hacks",
            impact="Critical",
            status="warn",
            details="GSC not configured; cannot verify security issues.",
            evidence={},
        )

        if gsc_client_id and gsc_client_secret and gsc_refresh_token:
            try:
                token = await gsc_get_access_token(gsc_client_id, gsc_client_secret, gsc_refresh_token)
                if token:
                    manual = await gsc_fetch("manualActions", gsc_site_url, token)
                    actions = manual.get("manualActions") or []
                    manual_actions_check = manual_actions_check.model_copy(
                        update={
                            "status": "pass" if len(actions) == 0 else "fail",
                            "details": "No manual actions found." if len(actions) == 0 else f"Found {len(actions)} manual action(s).",
                            "evidence": {"site": gsc_site_url, "manualActions": actions},
                        }
                    )

                    sec = await gsc_fetch("securityIssues", gsc_site_url, token)
                    issues = sec.get("securityIssues") or []
                    security_issues_check = security_issues_check.model_copy(
                        update={
                            "status": "pass" if len(issues) == 0 else "fail",
                            "details": "No security issues found." if len(issues) == 0 else f"Found {len(issues)} security issue(s).",
                            "evidence": {"site": gsc_site_url, "securityIssues": issues},
                        }
                    )
                else:
                    manual_actions_check.evidence["error"] = "Failed to obtain access_token from refresh token."
                    security_issues_check.evidence["error"] = "Failed to obtain access_token from refresh token."
            except Exception as e:
                manual_actions_check = manual_actions_check.model_copy(
                    update={"status": "warn", "details": f"GSC check failed: {str(e)}", "evidence": {"site": gsc_site_url}}
                )
                security_issues_check = security_issues_check.model_copy(
                    update={"status": "warn", "details": f"GSC check failed: {str(e)}", "evidence": {"site": gsc_site_url}}
                )

        # ---- Safe browsing (site-level) ----
        sb_key = os.getenv("SAFE_BROWSING_API_KEY")
        sb_res = await safe_browsing_check([root_url], sb_key)
        safe_browsing_status = "warn"
        safe_browsing_details = "Safe Browsing not configured; cannot verify malware/phishing."
        if sb_res.get("configured") and "error" not in sb_res:
            matches = sb_res.get("matches") or []
            safe_browsing_status = "pass" if len(matches) == 0 else "fail"
            safe_browsing_details = "No Safe Browsing threats found." if len(matches) == 0 else f"Found {len(matches)} Safe Browsing threat match(es)."
        elif sb_res.get("configured") and sb_res.get("error"):
            safe_browsing_details = f"Safe Browsing check failed: {sb_res.get('error')}"

        safe_browsing_check_result = EOCheckResult(
            id=3,
            type="SEO",
            category="Trust",
            check_item="Safe browsing",
            what_to_verify="No malware/phishing",
            impact="Critical",
            status=safe_browsing_status,
            details=safe_browsing_details,
            evidence=sb_res,
        )

        # ---- Spam protection (page-level heuristic, aggregated) ----
        # We scan discovered pages and flag suspicious signals.
        spam_flags: list[dict[str, Any]] = []
        async with httpx.AsyncClient() as client:
            for p in discovered[:50]:
                try:
                    r = await client.get(p.url, follow_redirects=True, timeout=20, headers={"user-agent": "site360"})
                    html = r.text or ""
                    extracted = extract_from_html(html)
                    text = extracted.get("text", "")
                    links = extracted.get("links", []) or []
                    _internal, external = split_internal_external_links(links, domain)
                    hidden_hits = detect_hidden_link_patterns(html)
                    spam_kw = count_keyword_matches(text, SPAM_KEYWORDS)
                    outbound_count = len(external)

                    if hidden_hits > 0 or outbound_count > 200 or len(spam_kw) > 0:
                        spam_flags.append(
                            {
                                "url": p.url,
                                "hidden_pattern_hits": hidden_hits,
                                "outbound_links": outbound_count,
                                "spam_keywords": spam_kw,
                            }
                        )
                except Exception:
                    continue

        if len(spam_flags) == 0:
            spam_status = "pass"
            spam_details = "No obvious injected-spam signals detected across discovered pages (heuristic)."
        else:
            # Fail only if strong signals; otherwise warn.
            strong = [f for f in spam_flags if f["hidden_pattern_hits"] > 5 or f["outbound_links"] > 500 or len(f["spam_keywords"]) > 0]
            spam_status = "fail" if len(strong) > 0 else "warn"
            spam_details = (
                f"Detected suspicious spam signals on {len(spam_flags)} page(s) (heuristic)."
                + (" Strong indicators present." if len(strong) > 0 else "")
            )

        spam_protection_check = EOCheckResult(
            id=4,
            type="SEO",
            category="Trust",
            check_item="Spam protection",
            what_to_verify="No injected spam pages",
            impact="Critical",
            status=spam_status,
            details=spam_details,
            evidence={"flagged_pages": spam_flags[:20], "flagged_count": len(spam_flags)},
        )

        # Return a single site-level record (consistent and avoids duplicating site checks per page).
        page = discovered[0] if discovered else None
        page_result = EOPageResult(
            page_id=page.page_id if page else "site",
            page_name=page.page_name if page else "site",
            url=root_url,
            timestamp=page.timestamp if page else None,
            checks=[
                manual_actions_check,
                security_issues_check,
                safe_browsing_check_result,
                spam_protection_check,
            ],
        )
        return [page_result.model_dump()]



