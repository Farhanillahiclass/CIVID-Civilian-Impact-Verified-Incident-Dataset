"""
Token-bucket rate limiter. Stdlib-only.
Limits requests per host to a configurable rate with a small burst capacity.
"""
import time
import threading


class TokenBucket:
    def __init__(self, rate: float = 1.0, capacity: float = 5.0):
        self.rate = rate                # tokens per second
        self.capacity = capacity        # max burst
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, tokens: float = 1.0):
        with self._lock:
            now = time.monotonic()
            self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
            self._last = now
            if self._tokens < tokens:
                deficit = tokens - self._tokens
                time.sleep(deficit / self.rate)
                self._tokens = 0.0
            else:
                self._tokens -= tokens
