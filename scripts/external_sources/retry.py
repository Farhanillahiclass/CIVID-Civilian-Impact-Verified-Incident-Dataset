"""
Retry with exponential backoff + jitter. Stdlib-only.
Retries on transient errors (URLError, timeout, HTTP 429/5xx).
Stops immediately on 401/403 (auth/forbidden) and 404 where retrying is futile.
"""
import random
import time
from urllib import error as urlerror


def _is_retryable(exc) -> bool:
    if isinstance(exc, urlerror.URLError):
        return True
    if isinstance(exc, urlerror.HTTPError):
        code = exc.code
        if code in (401, 403, 400, 404):
            return False
        return code >= 500 or code == 429
    return isinstance(exc, (TimeoutError, ConnectionError))


def retry_with_backoff(func, max_attempts: int = 3, base: float = 2.0,
                       cap: float = 30.0, on_retry=None):
    """Call func(); retry transient failures with full-jitter exponential backoff.
    Returns (result, attempts). On final failure, re-raises the last exception."""
    last = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func(), attempt
        except Exception as exc:  # noqa: BLE001 - caller isolates per source
            last = exc
            if not _is_retryable(exc):
                if on_retry:
                    on_retry(attempt, exc, False)
                raise
            if attempt == max_attempts:
                if on_retry:
                    on_retry(attempt, exc, True)
                raise
            sleep_for = min(cap, base * (2 ** (attempt - 1)))
            sleep_for = sleep_for * (0.5 + random.random() * 0.5)
            if on_retry:
                on_retry(attempt, exc, True)
            time.sleep(sleep_for)
    if last:
        raise last
