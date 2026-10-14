import time

from fastapi import HTTPException, status

from app.core.dependencies import CurrentUser


class RateLimiter:

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[int, tuple[float, int]] = {}
        self._cleanup_interval = 256
        self._calls_since_cleanup = 0

    def _cleanup_expired(self, now: float) -> None:
        expired_users = [
            user_id
            for user_id, (window_start, _) in self._hits.items()
            if now - window_start >= self.window_seconds
        ]

        for user_id in expired_users:
            del self._hits[user_id]

    async def __call__(self, user: CurrentUser) -> None:
        now = time.monotonic()

        self._calls_since_cleanup += 1
        
        if self._calls_since_cleanup >= self._cleanup_interval:
            self._cleanup_expired(now)
            self._calls_since_cleanup = 0

        window_start, count = self._hits.get(user.id, (now, 0))

        if now - window_start >= self.window_seconds:
            window_start, count = now, 0

        if count >= self.max_requests:
            retry_after = int(self.window_seconds - (now - window_start)) + 1
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests",
                headers={"Retry-After": str(retry_after)},
            )

        self._hits[user.id] = (window_start, count + 1)