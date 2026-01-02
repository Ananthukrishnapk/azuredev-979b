# ===== COMMON METRICS MODEL ===== #
from __future__ import annotations

from playwright.async_api import Page, BrowserContext, CDPSession
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel
from .constants import ANALYSERS

if TYPE_CHECKING:
    from pipeline.views import PreContext


class BaseAnalyser(ABC):
    name: ANALYSERS
    
    def __init__(self, url: str, page: Page, pre_context: "PreContext", context: Optional[BrowserContext] = None, cdp_session: Optional[CDPSession] = None):
        self.url = url
        self.page = page
        self.context = context
        self.cdp_session = cdp_session
        self.pre_context = pre_context

        self.need_cdp: bool = False

    @abstractmethod
    async def scan(self) -> list:
        raise NotImplementedError("Not implemented")
