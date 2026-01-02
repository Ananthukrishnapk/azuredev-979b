from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Optional
from urllib.parse import urlparse

import httpx
import xxhash


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
GOOGLEBOT_UA = (
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
)


SPAM_KEYWORDS = {
    "casino",
    "betting",
    "poker",
    "viagra",
    "cialis",
    "loan",
    "payday",
    "porn",
    "xxx",
    "crypto giveaway",
}


BAIT_PHRASES = {
    "you won't believe",
    "shocking",
    "secret",
    "doctors hate",
    "guaranteed",
    "miracle",
    "100% guaranteed",
}


DISCLOSURE_KEYWORDS = {
    "sponsored",
    "affiliate",
    "advertisement",
    "ad disclosure",
    "partnered",
}


@dataclass(frozen=True)
class FetchResult:
    url: str
    final_url: str
    status_code: int
    text: str


class _TextLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.in_style = False
        self._text_parts: list[str] = []
        self.title: Optional[str] = None
        self._in_title = False
        self.links: list[tuple[str, str]] = []  # (href, text)
        self._current_a_href: Optional[str] = None
        self._current_a_text: list[str] = []
        self.meta: dict[str, str] = {}
        self.canonical: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]):
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "script":
            self.in_script = True
        elif tag.lower() == "style":
            self.in_style = True
        elif tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "a":
            self._current_a_href = attrs_dict.get("href") or None
            self._current_a_text = []
        elif tag.lower() == "meta":
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").strip().lower()
            content = (attrs_dict.get("content") or "").strip()
            if name and content:
                self.meta[name] = content
        elif tag.lower() == "link":
            rel = (attrs_dict.get("rel") or "").strip().lower()
            href = (attrs_dict.get("href") or "").strip()
            if rel == "canonical" and href:
                self.canonical = href

    def handle_endtag(self, tag: str):
        if tag.lower() == "script":
            self.in_script = False
        elif tag.lower() == "style":
            self.in_style = False
        elif tag.lower() == "title":
            self._in_title = False
        elif tag.lower() == "a":
            if self._current_a_href:
                text = " ".join(self._current_a_text).strip()
                self.links.append((self._current_a_href, text))
            self._current_a_href = None
            self._current_a_text = []

    def handle_data(self, data: str):
        if self.in_script or self.in_style:
            return
        if self._in_title:
            t = (data or "").strip()
            if t:
                self.title = (self.title or "") + t
            return
        if self._current_a_href is not None:
            if data and data.strip():
                self._current_a_text.append(data.strip())
            return
        if data and data.strip():
            self._text_parts.append(data.strip())

    @property
    def text(self) -> str:
        return " ".join(self._text_parts)


def normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def text_hash(s: str) -> str:
    return xxhash.xxh64(normalize_text(s).encode("utf-8")).hexdigest()


def extract_from_html(html: str) -> dict[str, Any]:
    parser = _TextLinkParser()
    try:
        parser.feed(html or "")
    except Exception:
        pass

    # Dates from meta/time/JSON-LD
    dates: list[str] = []
    for k, v in parser.meta.items():
        if k in {"article:published_time", "article:modified_time", "date", "last-modified", "lastmod"}:
            dates.append(v)
    dates.extend(re.findall(r'date(Published|Modified)"\s*:\s*"([^"]+)"', html or "", flags=re.I))
    # Flatten tuples from regex
    dates_flat: list[str] = []
    for d in dates:
        if isinstance(d, tuple):
            dates_flat.append(d[1])
        else:
            dates_flat.append(d)

    author = parser.meta.get("author") or None
    if not author:
        m = re.search(r'"author"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', html or "", flags=re.I)
        if m:
            author = m.group(1)

    return {
        "title": parser.title,
        "canonical": parser.canonical,
        "meta": parser.meta,
        "author": author,
        "dates": [d for d in dates_flat if d],
        "text": parser.text,
        "links": parser.links,
    }


def split_internal_external_links(links: list[tuple[str, str]], base_domain: str) -> tuple[list[str], list[str]]:
    internal: list[str] = []
    external: list[str] = []
    for href, _txt in links:
        if not href:
            continue
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue
        try:
            u = urlparse(href)
        except Exception:
            continue
        if u.scheme in {"http", "https"}:
            if u.netloc and base_domain and base_domain in u.netloc:
                internal.append(href)
            elif u.netloc:
                external.append(href)
        else:
            # relative URL
            internal.append(href)
    return internal, external


def detect_hidden_link_patterns(html: str) -> int:
    html_l = (html or "").lower()
    patterns = [
        "display:none",
        "visibility:hidden",
        "font-size:0",
        "opacity:0",
        "left:-9999",
        "top:-9999",
    ]
    count = 0
    for p in patterns:
        count += html_l.count(p)
    return count


def count_keyword_matches(text: str, keywords: set[str]) -> list[str]:
    t = normalize_text(text)
    matched = [k for k in keywords if k in t]
    return matched


def keyword_stuffing_score(text: str) -> dict[str, Any]:
    t = normalize_text(text)
    words = [w for w in re.findall(r"[a-z]{4,}", t) if w]
    if len(words) < 200:
        return {"suspect": False, "reason": "too_few_words"}
    from collections import Counter

    c = Counter(words)
    top_word, top_count = c.most_common(1)[0]
    ratio = top_count / max(1, len(words))
    return {"suspect": ratio > 0.08 and top_count > 40, "top_word": top_word, "ratio": ratio, "top_count": top_count}


async def fetch_url(client: httpx.AsyncClient, url: str, user_agent: str, timeout_sec: float = 20) -> FetchResult:
    headers = {"user-agent": user_agent, "accept": "text/html,application/xhtml+xml"}
    r = await client.get(url, headers=headers, follow_redirects=True, timeout=timeout_sec)
    return FetchResult(url=url, final_url=str(r.url), status_code=r.status_code, text=r.text or "")


async def safe_browsing_check(urls: list[str], api_key: Optional[str]) -> dict[str, Any]:
    if not api_key:
        return {"configured": False, "matches": [], "error": "SAFE_BROWSING_API_KEY not set"}

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "site360", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": u} for u in urls],
        },
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(endpoint, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            return {"configured": True, "matches": data.get("matches", []) or []}
        except Exception as e:
            return {"configured": True, "matches": [], "error": str(e)}


async def gsc_get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("access_token")


async def gsc_fetch(endpoint_path: str, site_url: str, access_token: str) -> dict[str, Any]:
    # site_url must be URL-encoded in the path
    from urllib.parse import quote

    site_enc = quote(site_url, safe="")
    url = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{site_enc}/{endpoint_path}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"authorization": f"Bearer {access_token}"}, timeout=20)
        resp.raise_for_status()
        return resp.json()


