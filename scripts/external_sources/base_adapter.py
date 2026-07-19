"""
Base adapter contract. Stdlib-only.
Every adapter returns an AdapterResult with: parsed items, raw metadata,
error log, and retry count. Adapters isolate failure so the pipeline continues.
"""
from dataclasses import dataclass, field
from typing import Any

from .config import http_get_json, http_get_text
from .throttle import TokenBucket
from .retry import retry_with_backoff


@dataclass
class AdapterResult:
    parsed: list[dict] = field(default_factory=list)
    raw_meta: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    retries: int = 0


class BaseAdapter:
    source_type: str = "base"

    def __init__(self, cfg: dict, limiter: TokenBucket):
        self.cfg = cfg
        self.limiter = limiter

    def _get_json(self, url: str, timeout: int = 20) -> dict:
        self.limiter.acquire()
        result, attempts = retry_with_backoff(
            lambda: http_get_json(url, timeout=timeout),
            on_retry=lambda a, e, transient: None,
        )
        self.retries = getattr(self, "retries", 0)
        return result

    def _get_text(self, url: str, timeout: int = 20) -> str:
        self.limiter.acquire()
        return retry_with_backoff(lambda: http_get_text(url, timeout=timeout))[0]

    def fetch(self) -> AdapterResult:
        raise NotImplementedError

    def to_record(self, item: dict) -> dict:
        raise NotImplementedError

    def finalize(self, records: list[dict]) -> list[dict]:
        """Hook for post-processing (overridable). Default: identity."""
        return records
